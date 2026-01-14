from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from drivers.models import Driver
from rides.models import Ride, RideRequest
from core.models import Notification
import json

User = get_user_model()

def notify_available_drivers(ride_request):
    """
    Notify available drivers about a new ride request
    """
    channel_layer = get_channel_layer()
    
    # Find nearby available drivers
    available_drivers = Driver.objects.filter(
        status='available',
        is_active=True
    )
    
    for driver in available_drivers:
        # Create notification for the driver
        Notification.objects.create(
            recipient=driver.user,
            notification_type='ride_request',
            title='New Ride Request',
            message=f'A passenger needs a ride from {ride_request.pickup_address[:50]}...'
        )
        
        # Send WebSocket notification
        async_to_sync(channel_layer.group_send)(
            f"driver_{driver.user.id}",
            {
                'type': 'notification_message',
                'message': {
                    'type': 'ride_request',
                    'ride_request_id': ride_request.id,
                    'pickup_address': ride_request.pickup_address,
                    'destination_address': ride_request.destination_address,
                }
            }
        )

def notify_passenger_ride_accepted(ride):
    """
    Notify passenger that their ride has been accepted
    """
    channel_layer = get_channel_layer()
    
    # Create notification for the passenger
    Notification.objects.create(
        recipient=ride.passenger,
        notification_type='ride_accepted',
        title='Ride Accepted',
        message=f'Driver {ride.driver.user.get_full_name()} has accepted your ride request.'
    )
    
    # Send WebSocket notification
    async_to_sync(channel_layer.group_send)(
        f"passenger_{ride.passenger.id}",
        {
            'type': 'notification_message',
            'message': {
                'type': 'ride_accepted',
                'ride_id': ride.id,
                'driver_name': ride.driver.user.get_full_name(),
                'vehicle_info': f"{ride.driver.vehicle_make} {ride.driver.vehicle_model}",
            }
        }
    )

def broadcast_location_update(ride, latitude, longitude):
    """
    Broadcast location update to both passenger and driver
    """
    channel_layer = get_channel_layer()
    
    # Send to passenger
    async_to_sync(channel_layer.group_send)(
        f"passenger_{ride.passenger.id}",
        {
            'type': 'location_update',
            'message': {
                'type': 'driver_location',
                'ride_id': ride.id,
                'latitude': latitude,
                'longitude': longitude,
            }
        }
    )
    
    # Send to driver
    async_to_sync(channel_layer.group_send)(
        f"driver_{ride.driver.user.id}",
        {
            'type': 'location_update',
            'message': {
                'type': 'passenger_location',
                'ride_id': ride.id,
                'latitude': latitude,
                'longitude': longitude,
            }
        }
    )