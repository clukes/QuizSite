from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import quiz.routing
from quiz.consumers import QueryAuthMiddlewareStack

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': QueryAuthMiddlewareStack(
        URLRouter(
            quiz.routing.websocket_urlpatterns
        )
    ),
})
