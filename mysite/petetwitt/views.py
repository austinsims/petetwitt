from petetwitt.models import *
from petetwitt.forms import *
from petetwitt import settings
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import re

def latest_tweets(request):
    """
    List tweets from users the logged in user is following, or everyone if they're anonymous

    Also show a form for making a new tweet
    """

    import pdb; pdb.set_trace()
    q = Q()
    if request.user.is_authenticated():
        following = request.user.get_profile().get_following()
        for u in following:
            q = q | Q(author=u)
        if len(following) > 0:
            tweets = reversed(Tweet.objects.filter(q).order_by('timestamp'))
        else:
            tweets = None
        form = TweetForm()
    else:
        tweets = reversed(Tweet.objects.all().order_by('timestamp'))
        form = None
    return render(request, 'petetwitt/list_tweets.html', {'tweets' : tweets, 'logged_in_user' : request.user, 'enable_autorefresh' : settings.ENABLE_AUTOREFRESH, 'form' : form })

def directory(request):
    users = User.objects.all()
    return render(request, 'petetwitt/directory.html', {'users' : users, 'logged_in_user' : request.user})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated():
        following = user in request.user.get_profile().following.all()
    else:
        following = False
    tweets = Tweet.objects.filter(author=user)
    return render(request, 'petetwitt/profile.html', {'user' : user , 'logged_in_user' : request.user, 'tweets' : tweets, 'following' : following})

@login_required
def my_profile(request):
    return profile(request, request.user.username)

@login_required
def reply(request, tweet_pk):
    return post(request, in_reply_to_pk=tweet_pk)

@login_required
def follow(request, username):
    profile = request.user.get_profile()
    followed = get_object_or_404(User, username=username)
    profile.following.add(followed)
    Notification.objects.create(
        type=NotificationType.FOLLOW,
        sender=request.user,
        recipient=followed,
    )
    return HttpResponseRedirect(reverse('profile', kwargs={'username' : username}))

@login_required
def unfollow(request, username):
    profile = request.user.get_profile()
    followed = get_object_or_404(User, username=username)
    profile.following.remove(followed)
    profile.save()
    return HttpResponseRedirect(reverse('profile', kwargs={'username' : username}))

@login_required
def post(request, **kwargs):
    in_reply_to_pk = None
    if 'in_reply_to_pk' in kwargs:
        in_reply_to_pk = kwargs.pop('in_reply_to_pk')
    if request.method == 'GET':
        if in_reply_to_pk is not None:
            in_reply_to = get_object_or_404(Tweet, pk=in_reply_to_pk)
            username = in_reply_to.author.username
            form = TweetForm(body='@%s:&nbsp;' % username, in_reply_to=in_reply_to)
        else:
            form = TweetForm()
        return render(request, 'petetwitt/post.html', {'form' : form, 'logged_in_user' : request.user})
    else:
        form = TweetForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data['body']
            in_reply_to = form.cleaned_data['in_reply_to']
            tweet = request.user.tweet_authors.create(body=body, in_reply_to=in_reply_to)

            if tweet.in_reply_to is not None:
                Notification.objects.create(
                    type=NotificationType.REPLY,
                    sender = request.user,
                    recipient = in_reply_to.author,
                    tweet = tweet,
                )

            # find and create or get hashtags
            p = re.compile(r'(?<!color: )#(\w+)')
            
            pos = 0
            while True:
                m = p.search(body, pos)
                if m is None:
                    break
                else:
                    st = m.start()
                    end = m.end()
                    name = body[st+1:end]
                    hashtag, created = Hashtag.objects.get_or_create(name=name)
                    tweet.hashtags.add(hashtag)
                    link_prefix = '<a href="' + reverse(search) + '?query=' + name + '">'
                    link_suffix = '</a>'
                    body = body[0:st] + link_prefix + body[st:end] + link_suffix + body[end:]
                    pos = st + len(link_prefix) + (end-st) + len(link_suffix)


            p = re.compile(r'@\w+')   
            pos = 0
            while True:
                m = p.search(body, pos)
                if m is None:
                    break
                else:
                    st = m.start()
                    end = m.end()
                    username = body[st+1:end]
                    user = User.objects.get(username=username)
                    if user is not None:
                        if in_reply_to is not None and in_reply_to.author.pk is not user.pk:
                            tweet.shoutouts.add(user)

                            Notification.objects.create(
                                type=NotificationType.SHOUTOUT,
                                sender=request.user,
                                recipient=user,
                                tweet=tweet,
                            )
                    link_prefix = '<a href="' + reverse(profile, kwargs={'username' : username}) + '">'
                    link_suffix = '</a>'
                    body = body[0:st] + link_prefix + body[st:end] + link_suffix + body[end:]
                    pos = st + len(link_prefix) + (end-st) + len(link_suffix)
                
            # TODO: find and create hyperlinks
            p = re.compile(r'^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$')
            for m in p.finditer(body):
                pass
            tweet.body = body
            tweet.save()
                                    
            return HttpResponseRedirect(reverse('latest_tweets'))
        else:
            return render(request, 'petetwitt/post.html', {'form' : form, 'logged_in_user' : request.user})

class TweetDelete(generic.DeleteView):
    model = Tweet
    success_url = reverse_lazy('latest_tweets')
    def get_object(self, queryset=None):
        tweet = super(TweetDelete, self).get_object()
        if not tweet.author == self.request.user:
            raise Http404
        return tweet

def count(request):
    return HttpResponse('%d' % Tweet.objects.count())

def data(request):
    return HttpResponse('this is data from the server')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('timestamp')

    # Generate response before marking notifications as read
    response = render(request, 'petetwitt/notifications.html', {'logged_in_user' : request.user, 'notifications' : reversed(notifications)})

    # TODO: fix read/unread rendering.

    # Mark them all as read
    for notification in notifications:
        notification.unread = False

    return response

def conversation(request, pk):
    convo = list()
    tweet = get_object_or_404(Tweet, pk=int(pk))
    convo.append(tweet)
    while tweet.in_reply_to is not None:
        tweet = tweet.in_reply_to
        convo.append(tweet)

    return render(request, 'petetwitt/conversation.html', {'convo' : convo, 'logged_in_user' : request.user})

def tweet(request, pk):
    return HttpResponse('not implemented')

def search(request):
    query = request.GET['query']
    words = [query[m.start():m.end()] for m in re.finditer(r'\w+', query)]

    # Find users

    q = Q()
    for word in words:
        q = q | Q(username__icontains=word) | Q(first_name__icontains=word) | Q(last_name__icontains=word)

    users = User.objects.filter(q)

    # Find tweets
    q = Q()
    for word in words:
        q = q | Q(author__username__icontains=word) | Q(hashtags__name__icontains=word) | Q(body__icontains=word)

    tweets = Tweet.objects.filter(q)
    
    return render(request, 'petetwitt/search_results.html', {'logged_in_user' : request.user, 'users' : users, 'tweets' : tweets })
