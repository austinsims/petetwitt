from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login
from django.conf import settings
from registration.backends.simple.views import RegistrationView
from petetwitt.forms import CustomRegistrationForm
from petetwitt import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'petetwitt/login.html', 'extra_context' : { 'next' : '/' }}, name='login'),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=CustomRegistrationForm)),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', views.latest_tweets, name='latest_tweets'),
    url(r'^users/$', views.directory, name='directory'),
    url(r'^users/(?P<username>\w+)/$', views.profile, name='profile'), 
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name' : 'petetwitt/logout.html' }, name='logout'),
    url(r'^post/$', views.post, name='post'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^conversation/(?P<last_tweet_pk>)\d+/$', views.conversation, name='conversation'),
    url(r'^tweet/(?P<pk>)\d+/$', views.tweet, name='tweet'),
    url(r'^reply/(?P<tweet_pk>\d+)/$', views.reply, name='reply'),
    url(r'^follow/(?P<username>\w+)/$', views.follow, name='follow'),
    url(r'^unfollow/(?P<username>\w+)/$', views.unfollow, name='unfollow'),
    url(r'^search/(?P<query>@?#?\w+)/$', views.search, name='search'),
    url(r'^delete/(?P<pk>\d+)/$', views.TweetDelete.as_view(), name='tweet_delete'),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^count/$', views.count, name='count'),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
