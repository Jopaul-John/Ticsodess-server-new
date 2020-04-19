from django.conf.urls import url

from ticsodessapp import consumers
from ticsodessapp import InvitationConsumer
from ticsodessapp import friendsConsumer
websocket_urlpatterns = [
    url(r'^ws/gameroom/(?P<room_name>[^/]+)$', consumers.TicsodessConsumer),
    url(r'^ws/invitationroom/(?P<username>[^/]+)$', InvitationConsumer.InvitationConsumer),
    url(r'^ws/friends/$', friendsConsumer.FriendsStatus),
]