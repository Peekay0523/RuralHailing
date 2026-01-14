from django.db import models
from django.contrib.auth import get_user_model
from drivers.models import Driver, Vehicle

User = get_user_model()

class Ride(models.Model):
    RIDE_STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )

    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_as_passenger')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='rides_as_driver')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='rides')

    pickup_address = models.TextField()
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)

    destination_address = models.TextField()
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)

    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in kilometers
    duration = models.IntegerField(null=True, blank=True)  # in minutes
    fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=RIDE_STATUS_CHOICES, default='requested')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    dropoff_time = models.DateTimeField(null=True, blank=True)

    payment_status = models.CharField(max_length=20, default='pending')
    payment_method = models.CharField(max_length=20, default='cash')

    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    review = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride #{self.id} - {self.passenger.username} - {self.status}"

class RideRequest(models.Model):
    """
    Model to store ride requests before they are assigned to a driver
    """
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ride_requests')
    pickup_address = models.TextField()
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)

    destination_address = models.TextField()
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)

    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, default='active')  # active, matched, expired

    def __str__(self):
        return f"Ride Request #{self.id} - {self.passenger.username}"
