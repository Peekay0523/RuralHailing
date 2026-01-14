from django.db import models
from django.contrib.auth import get_user_model
from drivers.models import Driver
from rides.models import Ride

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('ride_request', 'Ride Request'),
        ('ride_accepted', 'Ride Accepted'),
        ('driver_arrived', 'Driver Arrived'),
        ('ride_completed', 'Ride Completed'),
        ('payment', 'Payment'),
        ('system', 'System Message'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

class Location(models.Model):
    """
    Store location history for tracking purposes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, null=True, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.driver:
            return f"Location for {self.driver.user.username} at {self.timestamp}"
        elif self.user:
            return f"Location for {self.user.username} at {self.timestamp}"
        else:
            return f"Location at {self.timestamp}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    )

    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Ride #{self.ride.id} - {self.amount}"
