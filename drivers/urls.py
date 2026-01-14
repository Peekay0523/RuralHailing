from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.DriverRegistrationView.as_view(), name='driver-register'),
    path('available/', views.AvailableDriversView.as_view(), name='available-drivers'),
    path('profile/', views.DriverProfileView.as_view(), name='driver-profile'),
    path('update-status/', views.UpdateDriverStatusView.as_view(), name='update-driver-status'),
]

app_name = 'drivers'