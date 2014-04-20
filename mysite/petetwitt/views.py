from petetwitt.models import *
from petetwitt.forms import *
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import re

def latest_tweets(request):
    tweets = reversed(Tweet.objects.order_by('timestamp'))
    return render(request, 'petetwitt/list_tweets.html', {'tweets' : tweets, 'logged_in_user' : request.user})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    following = user in request.user.get_profile().following.all()
    tweets = Tweet.objects.filter(author=user)
    return render(request, 'petetwitt/profile.html', {'user' : user , 'logged_in_user' : request.user, 'tweets' : tweets, 'following' : following})

@login_required
def reply(request, username):
    return post(request, username=username)

@login_required
def follow(request, username):
    profile = request.user.get_profile()
    followed = get_object_or_404(User, username=username)
    profile.following.add(followed)
    return HttpResponseRedirect(reverse('profile', kwargs={'username' : username}))

@login_required
def unfollow(request, username):
    import pdb; pdb.set_trace()
    profile = request.user.get_profile()
    followed = get_object_or_404(User, username=username)
    profile.following.remove(followed)
    profile.save()
    return HttpResponseRedirect(reverse('profile', kwargs={'username' : username}))

@login_required
def post(request, **kwargs):
    username = None
    if 'username' in kwargs:
        username = kwargs.pop('username')
    if request.method == 'GET':
        if username is not None:
            form = TweetForm(body='@%s: ' % username)
        else:
            form = TweetForm()
        return render(request, 'petetwitt/post.html', {'form' : form, 'logged_in_user' : request.user})
    else:
        form = TweetForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data['body']
            tweet = request.user.tweet_authors.create(body=body)

            # find and create or get hashtags
            p = re.compile(r'#\w+')
            for m in p.finditer(body):
                st = m.start()
                end = m.end()
                name = body[st+1:end]
                hashtag, created = Hashtag.objects.get_or_create(name=name)
                tweet.hashtags.add(hashtag)
                link_prefix = '<a href="' + reverse(search, kwargs={'query' : name}) + '">'
                link_suffix = '</a>'
                body = body[0:st] + link_prefix + body[st:end] + link_suffix + body[end:]

            # TODO: find and create shoutouts
            p = re.compile(r'@\w+')
            for m in p.finditer(body):
                st = m.start()
                end = m.end()
                username = body[st+1:end]
                user = User.objects.get(username=username)
                if user is not None:
                    # commented out due to bug
                    tweet.shoutouts.add(user)
                link_prefix = '<a href="' + reverse(profile, kwargs={'username' : username}) + '">'
                link_suffix = '</a>'
                body = body[0:st] + link_prefix + body[st:end] + link_suffix + body[end:]

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

def search(request, query):
    return HttpResponse('not implemented')
