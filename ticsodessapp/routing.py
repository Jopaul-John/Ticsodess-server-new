from django.conf.urls import url
from ticsodessapp import MessageConsumer
from ticsodessapp import invitationConsumerNew

websocket_urlpatterns = [
    url(r'^ws/movements/$', MessageConsumer.MessageConsumer),
    url(r'^ws/gameroom/(?P<room_name>[^/]+)/$', invitationConsumerNew.InvitationConsumerNew),
    url(r'^ws/invite$', invitationConsumerNew.InvitationConsumerFriend),
]