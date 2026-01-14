from django.contrib import admin
from .models import Driver, Vehicle

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'vehicle_make', 'vehicle_model', 'status', 'rating', 'total_rides', 'is_active')
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'license_number', 'vehicle_plate_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'plate_number', 'vehicle_type', 'driver', 'is_active')
    list_filter = ('vehicle_type', 'is_active', 'year')
    search_fields = ('make', 'model', 'plate_number', 'driver__user__username')
    readonly_fields = ('created_at', 'updated_at')