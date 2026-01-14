from django.contrib import admin
from .models import Ride, RideRequest

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'driver', 'status', 'fare', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('passenger__username', 'driver__user__username', 'pickup_address', 'destination_address')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'pickup_address', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('passenger__username', 'pickup_address', 'destination_address')
    readonly_fields = ('requested_at',)