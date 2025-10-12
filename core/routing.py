from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/bookings/(?P<booking_id>[^/]+)/?$', consumers.BookingConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>[^/]+)/?$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<user_id>[^/]+)/(?P<role>[^/]+)/?$', consumers.ChatConsumer.as_asgi()),
]