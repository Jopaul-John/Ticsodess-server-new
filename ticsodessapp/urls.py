from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from ticsodessapp import views

urlpatterns = [
    url(r'^user/$', views.UserProfileView.as_view()),
    url(r'^user/imageurl/$', views.UserImageView.as_view()),
    url(r'^user/friends/$', views.UserFriends.as_view()),
    url(r'^gameroom/$', views.GameRoomView.as_view()),
    url(r'^getfriend/$',views.FriendView.as_view()),
    url(r'^gamemodel/$',views.GameModelView.as_view()),
    url(r'^user/status/$',views.UserStatusView.as_view()),
    url(r'^user/busy/$',views.BusyStatus.as_view()),
    url(r'^ai/room/$',views.AiHandOver.as_view()),
    url(r'^release/room/$',views.ReleaseResource.as_view()),
]