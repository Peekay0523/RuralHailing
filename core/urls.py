from django.urls import path
from . import views
from . import views_tracking
from .views_notifications import NotificationListView, MarkNotificationAsReadView
from .views import CreatePaymentIntentView, ProcessPaymentView, CashPaymentView

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.home, name='home'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('tracking-preferences/', views_tracking.tracking_preferences, name='tracking_preferences'),
    path('update-tracking-preferences/', views_tracking.update_tracking_preferences, name='update_tracking_preferences'),
    path('get-tracking-status/', views_tracking.get_tracking_status, name='get_tracking_status'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
    path('payments/create/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('payments/process/', ProcessPaymentView.as_view(), name='process-payment'),
    path('payments/cash/', CashPaymentView.as_view(), name='cash-payment'),
]

app_name = 'core'