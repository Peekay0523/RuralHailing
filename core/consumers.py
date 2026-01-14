import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from drivers.models import Driver
from rides.models import Ride
from core.models import Location
from django.utils import timezone

User = get_user_model()

class RideTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            await self.accept()
            
            # Add user to a group for tracking updates
            if self.user.user_type == 'driver':
                self.group_name = f"driver_{self.user.id}"
            else:
                self.group_name = f"passenger_{self.user.id}"
                
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Remove user from group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'location_update':
            latitude = text_data_json.get('latitude')
            longitude = text_data_json.get('longitude')
            ride_id = text_data_json.get('ride_id')
            
            # Save location to database
            await self.save_location(latitude, longitude, ride_id)
            
            # Broadcast location to relevant parties
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'location_message',
                    'latitude': latitude,
                    'longitude': longitude,
                    'ride_id': ride_id
                }
            )
        elif message_type == 'ride_status_update':
            ride_id = text_data_json.get('ride_id')
            status = text_data_json.get('status')
            
            # Update ride status in database
            await self.update_ride_status(ride_id, status)
            
            # Broadcast status update
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'status_message',
                    'ride_id': ride_id,
                    'status': status
                }
            )

    async def location_message(self, event):
        # Send location data to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'ride_id': event['ride_id']
        }))

    async def status_message(self, event):
        # Send status update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'ride_status_update',
            'ride_id': event['ride_id'],
            'status': event['status']
        }))

    @sync_to_async
    def save_location(self, latitude, longitude, ride_id):
        try:
            ride = Ride.objects.get(id=ride_id)
            Location.objects.create(
                user=self.user if self.user.user_type == 'passenger' else None,
                driver=self.user.driver_profile if self.user.user_type == 'driver' else None,
                ride=ride,
                latitude=latitude,
                longitude=longitude
            )
            
            # Update driver's location if this is a driver
            if self.user.user_type == 'driver':
                driver = self.user.driver_profile
                driver.location_lat = latitude
                driver.location_lng = longitude
                driver.last_location_update = timezone.now()
                driver.save()
                
        except Ride.DoesNotExist:
            pass

    @sync_to_async
    def update_ride_status(self, ride_id, status):
        try:
            ride = Ride.objects.get(id=ride_id)
            ride.status = status
            ride.save()
        except Ride.DoesNotExist:
            pass