from django.contrib import admin
from .models import Notification, Location, Payment

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    readonly_fields = ('created_at',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'timestamp', 'user', 'driver')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'driver__user__username')
    readonly_fields = ('timestamp',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('ride', 'amount', 'payment_method', 'status', 'processed_at')
    list_filter = ('payment_method', 'status', 'processed_at')
    search_fields = ('transaction_id', 'ride__id')
    readonly_fields = ('processed_at',)