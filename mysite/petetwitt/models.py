from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_enumfield import enum


def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = Profile.objects.get_or_create(user=instance)  
       # follow self
       profile.following.add(instance)

post_save.connect(create_user_profile, sender=User) 

class Hashtag(models.Model):
    name = models.CharField(max_length=139, unique=True)

    def __str__(self):
        return self.name

class Tweet(models.Model):
    author = models.ForeignKey(User, related_name='tweet_authors')
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    picture = models.ImageField(blank=True, null=True, upload_to='media')
    thumbnail = models.ImageField(blank=True, null=True, upload_to='media')
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='tweet_hashtags')
    shoutouts = models.ManyToManyField(User, blank=True, related_name='tweet_shoutouts')
    in_reply_to = models.ForeignKey('self', blank=True, null=True, related_name='tweet_in_reply_to')

    def __str__(self):
        return self.body

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile_user')
    following = models.ManyToManyField(User, related_name='profile_following', blank=True)
    portrait = models.ImageField(upload_to='media')
    favorites = models.ManyToManyField(Tweet, related_name='profile_favorites', blank=True)

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

class NotificationType(enum.Enum):
    SHOUTOUT = 0
    REPLY = 1
    FAVORITE = 2
    FOLLOW = 3

class Notification(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    type = enum.EnumField(NotificationType)
    sender = models.ForeignKey(User, related_name='notification_sender')
    recipient = models.ForeignKey(User, related_name='notication_recipient')
    tweet = models.ForeignKey(Tweet, related_name='notification_tweet', blank=True, null=True)
    unread = models.BooleanField(default=True)
