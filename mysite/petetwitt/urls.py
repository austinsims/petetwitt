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
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=CustomRegistrationForm)),
    url(r'^accounts/profile/$', views.my_profile, name='my_profile'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/avatar', views.change_avatar, name='change_avatar'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^$', views.latest_tweets, name='latest_tweets'),
    url(r'^users/$', views.directory, name='directory'),
    url(r'^users/(?P<username>\w+)/$', views.profile, name='profile'), 
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name' : 'petetwitt/logout.html' }, name='logout'),
    url(r'^post/$', views.post, name='post'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^conversation/(?P<pk>\d+)/$', views.conversation, name='conversation'),
    url(r'^tweet/(?P<pk>)\d+/$', views.tweet, name='tweet'),
    url(r'^reply/(?P<tweet_pk>\d+)/$', views.reply, name='reply'),
    url(r'^follow/(?P<username>\w+)/$', views.follow, name='follow'),
    url(r'^unfollow/(?P<username>\w+)/$', views.unfollow, name='unfollow'),
    url(r'^delete/(?P<pk>\d+)/$', views.TweetDelete.as_view(), name='tweet_delete'),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^count/$', views.count, name='count'),
    url(r'^search/$', views.search, name='search'),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
