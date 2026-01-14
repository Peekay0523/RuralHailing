from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.request_ride_view, name='request-ride'),
    path('api/request/', views.RequestRideView.as_view(), name='api-request-ride'),
    path('track/', views.track_ride_view, name='track-ride'),
    path('accept/', views.AcceptRideView.as_view(), name='accept-ride'),
    path('<int:pk>/', views.RideDetailView.as_view(), name='ride-detail'),
    path('<int:pk>/cancel/', views.CancelRideView.as_view(), name='cancel-ride'),
    path('<int:pk>/complete/', views.CompleteRideView.as_view(), name='complete-ride'),
    path('history/', views.RideHistoryView.as_view(), name='ride-history'),
    path('current/', views.CurrentRideView.as_view(), name='current-ride'),
]

app_name = 'rides'