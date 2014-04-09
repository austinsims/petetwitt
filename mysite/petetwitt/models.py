from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile_user')
    following = models.ManyToManyField(User, related_name='profile_following', blank=True)
    portrait = models.ImageField(upload_to='media')

    def __str__(self):
        return "%s's profile" % self.user

    def count_tweets(self):
        return len(Tweet.objects.filter(author=self.user))

    def count_followers(self):
        return len(Profile.objects.filter(following=self.user))

    def get_followers(self):
        return [profile.user for profile in self.user.profile_following.all()]

    def get_following(self):
        return self.following.all()

    def count_following(self):
        return self.following.count()

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = Profile.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User) 

class Hashtag(models.Model):
    name = models.CharField(max_length=139)

    def __str__(self):
        return self.name

class Tweet(models.Model):
    author = models.ForeignKey(User, related_name='tweet_authors')
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    picture = models.ImageField(blank=True, upload_to='media')
    thumbnail = models.ImageField(blank=True, upload_to='media')
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='tweet_hashtags')
    shoutouts = models.ManyToManyField(User, blank=True, related_name='tweet_shoutouts')

    def __str__(self):
        return self.body
