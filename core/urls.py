from django.urls import path
from . import views
from .views_notifications import NotificationListView, MarkNotificationAsReadView
from .views import CreatePaymentIntentView, ProcessPaymentView, CashPaymentView

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.home, name='home'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
    path('payments/create/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('payments/process/', ProcessPaymentView.as_view(), name='process-payment'),
    path('payments/cash/', CashPaymentView.as_view(), name='cash-payment'),
]

app_name = 'core'