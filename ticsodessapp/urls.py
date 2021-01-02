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
    url(r'^tempuser/$',views.TempUser.as_view()),
    
    url(r'^aimove/$', views.ArtificialIntelligence.as_view()),
    url(r'^tempusercreate/$', views.TemperoryUser.as_view()),
    url(r'^freeroom/$', views.GameRoomViewNew.as_view()),
    url(r'^room/$', views.SwitchToBotPlayer.as_view()),
    url(r'^recentfriends/$', views.Friends.as_view()),
    url(r'^searchfriend/$', views.FriendSearch.as_view()),
    url(r'^friendroom/$', views.FriendRoom.as_view()),
    url(r'^joinroom/$', views.JoinFriend.as_view()),
    url(r'^userDetails/$', views.UserDetails.as_view()),
    url(r'^sociallogin/$', views.SocialLoginView.as_view()),
    url(r'^busy/$',views.BusyView.as_view()),
    url(r'^updatestat/$',views.UpdateStatsAndRelease.as_view()),
    url(r'^updateusername/$',views.UpdateUserName.as_view()),
    url(r'^stats/$',views.UserStats.as_view()),
    url(r'^shareimage/$',views.ShareImage.as_view()),
]