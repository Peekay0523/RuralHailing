from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/ride-tracking/', consumers.RideTrackingConsumer.as_asgi()),
]