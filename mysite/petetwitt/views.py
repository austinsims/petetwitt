from petetwitt.models import *
from petetwitt.forms import *
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

def latest_tweets(request):
    tweets = reversed(Tweet.objects.order_by('timestamp'))
    return render(request, 'petetwitt/list_tweets.html', {'tweets' : tweets, 'logged_in_user' : request.user})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(author=user)
    return render(request, 'petetwitt/profile.html', {'user' : user , 'logged_in_user' : request.user, 'tweets' : tweets})

# TODO: add extra args
#login_required([redirect_field_name=REDIRECT_FIELD_NAME, login_url=None])
@login_required
def post(request):
    if request.method == 'GET':
        return render(request, 'petetwitt/post.html', {'form' : TweetForm(), 'logged_in_user' : request.user})
    else:
        form = TweetForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data['body']
            # TODO: check length. do this in form or something probably
            # TODO: find and create or get hashtags
            # TODO: find and create shoutouts
            tweet = request.user.tweet_authors.create(body=body)
                        
            return HttpResponseRedirect(reverse('latest_tweets'))
        else:
            return render(request, 'petetwitt/post.html', {'form' : form, 'logged_in_user' : request.user})


