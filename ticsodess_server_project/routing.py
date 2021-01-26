from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import ticsodessapp.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            ticsodessapp.routing.websocket_urlpatterns
        )
    ),
})