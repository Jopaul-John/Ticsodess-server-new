from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from ticsodessapp import views

urlpatterns = [
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
    url(r'^privacy/$',views.privacyPolicy),
]