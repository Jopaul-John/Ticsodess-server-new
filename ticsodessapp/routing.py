from django.conf.urls import url

from ticsodessapp import consumers
from ticsodessapp import InvitationConsumer
from ticsodessapp import friendsConsumer
from ticsodessapp import MessageConsumer
from ticsodessapp import invitationConsumerNew

websocket_urlpatterns = [
    url(r'^ws/gameroom/(?P<room_name>[^/]+)$', consumers.TicsodessConsumer),
    url(r'^ws/invitationroom/(?P<username>[^/]+)$', InvitationConsumer.InvitationConsumer),
    url(r'^ws/friends/$', friendsConsumer.FriendsStatus),
    # new version
    url(r'^ws/movements/$', MessageConsumer.MessageConsumer),
    url(r'^ws/gameroom/(?P<room_name>[^/]+)/$', invitationConsumerNew.InvitationConsumerNew),
    url(r'^ws/invite$', invitationConsumerNew.InvitationConsumerFriend),
]