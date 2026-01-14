from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class Driver(models.Model):
    DRIVER_STATUS_CHOICES = (
        ('available', 'Available'),
        ('on_ride', 'On Ride'),
        ('offline', 'Offline'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True)
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.IntegerField()
    vehicle_color = models.CharField(max_length=30)
    vehicle_plate_number = models.CharField(max_length=20, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_rides = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=DRIVER_STATUS_CHOICES, default='offline')
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Driver {self.user.get_full_name()} - {self.vehicle_make} {self.vehicle_model}"

class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = (
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
        ('van', 'Van'),
    )

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    color = models.CharField(max_length=30)
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='car')
    insurance_number = models.CharField(max_length=50)
    insurance_expiry_date = models.DateField()
    registration_number = models.CharField(max_length=50)
    registration_expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.plate_number})"
