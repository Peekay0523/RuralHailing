from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Ride, RideRequest
from .serializers import RideSerializer, RideRequestSerializer
from drivers.models import Driver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
import math
from core.services import notify_available_drivers, notify_passenger_ride_accepted

User = get_user_model()

from django.contrib.auth.decorators import login_required

@login_required
def request_ride_view(request):
    return render(request, 'rides/request_ride.html')

@login_required
def track_ride_view(request):
    return render(request, 'rides/track_ride.html')

class RequestRideView(generics.CreateAPIView):
    serializer_class = RideRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Create a ride request
        ride_request = serializer.save(passenger=self.request.user)

        # Notify available drivers about the new ride request
        notify_available_drivers(ride_request)

        # Find the nearest available driver
        available_drivers = Driver.objects.filter(
            status='available',
            is_active=True
        )

        # Calculate distances and find the closest driver
        closest_driver = None
        min_distance = float('inf')

        for driver in available_drivers:
            if driver.location_lat and driver.location_lng:
                distance = self.calculate_distance(
                    float(ride_request.pickup_lat),
                    float(ride_request.pickup_lng),
                    float(driver.location_lat),
                    float(driver.location_lng)
                )

                if distance < min_distance:
                    min_distance = distance
                    closest_driver = driver

        # If we found a driver, assign the ride
        if closest_driver:
            with transaction.atomic():
                # Create the actual ride
                ride = Ride.objects.create(
                    passenger=self.request.user,
                    driver=closest_driver,
                    pickup_address=ride_request.pickup_address,
                    pickup_lat=ride_request.pickup_lat,
                    pickup_lng=ride_request.pickup_lng,
                    destination_address=ride_request.destination_address,
                    destination_lat=ride_request.destination_lat,
                    destination_lng=ride_request.destination_lng,
                    status='accepted'
                )

                # Update driver status
                closest_driver.status = 'on_ride'
                closest_driver.save()

                # Mark the ride request as matched
                ride_request.status = 'matched'
                ride_request.save()

                # Notify the passenger that their ride has been accepted
                notify_passenger_ride_accepted(ride)

                # Return the created ride
                ride_serializer = RideSerializer(ride)
                return ride

        # If no driver found, keep the request open
        return ride_request

    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points in km using Haversine formula"""
        R = 6371  # Earth radius in km

        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lng2 - lng1)
        a = (math.sin(dLat/2) * math.sin(dLat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dLon/2) * math.sin(dLon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        return distance

class AcceptRideView(APIView):
    """Endpoint for drivers to accept a ride request"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ride_request_id = request.data.get('ride_request_id')

        try:
            ride_request = RideRequest.objects.get(id=ride_request_id, status='active')

            # Get the driver
            try:
                driver = request.user.driver_profile
            except Driver.DoesNotExist:
                return Response(
                    {'error': 'Only drivers can accept ride requests'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Create the ride
            with transaction.atomic():
                ride = Ride.objects.create(
                    passenger=ride_request.passenger,
                    driver=driver,
                    pickup_address=ride_request.pickup_address,
                    pickup_lat=ride_request.pickup_lat,
                    pickup_lng=ride_request.pickup_lng,
                    destination_address=ride_request.destination_address,
                    destination_lat=ride_request.destination_lat,
                    destination_lng=ride_request.destination_lng,
                    status='accepted'
                )

                # Update driver status
                driver.status = 'on_ride'
                driver.save()

                # Mark the request as matched
                ride_request.status = 'matched'
                ride_request.save()

                # Notify the passenger that their ride has been accepted
                notify_passenger_ride_accepted(ride)

                serializer = RideSerializer(ride)
                return Response(serializer.data)

        except RideRequest.DoesNotExist:
            return Response(
                {'error': 'Ride request not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class RideDetailView(generics.RetrieveAPIView):
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ride.objects.filter(
            passenger=self.request.user
        ) | Ride.objects.filter(
            driver__user=self.request.user
        )

class RideHistoryView(generics.ListAPIView):
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ride.objects.filter(
            passenger=self.request.user
        ).order_by('-created_at')

class CurrentRideView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the current active ride for the user
        try:
            current_ride = Ride.objects.filter(
                passenger=request.user,
                status__in=['requested', 'accepted', 'picked_up', 'in_transit']
            ).order_by('-created_at').first()

            if current_ride:
                serializer = RideSerializer(current_ride)
                return Response(serializer.data)
            else:
                return Response({'message': 'No active ride found'})
        except Ride.DoesNotExist:
            return Response({'message': 'No active ride found'})

class CancelRideView(APIView):
    """Allow passengers to cancel a ride request"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            ride = Ride.objects.get(id=pk, passenger=request.user)

            if ride.status in ['requested', 'accepted']:
                ride.status = 'cancelled'
                ride.save()

                # If the ride was accepted, make the driver available again
                if ride.driver:
                    ride.driver.status = 'available'
                    ride.driver.save()

                serializer = RideSerializer(ride)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'Cannot cancel ride in current status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Ride.DoesNotExist:
            return Response(
                {'error': 'Ride not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class CompleteRideView(APIView):
    """Allow drivers to mark a ride as completed"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            ride = Ride.objects.get(id=pk, driver__user=request.user)

            if ride.status == 'in_transit':
                ride.status = 'completed'
                ride.dropoff_time = timezone.now()
                ride.save()

                # Update driver status
                driver = ride.driver
                driver.status = 'available'
                driver.total_rides += 1
                driver.save()

                serializer = RideSerializer(ride)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'Ride must be in transit to complete'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Ride.DoesNotExist:
            return Response(
                {'error': 'Ride not found'},
                status=status.HTTP_404_NOT_FOUND
            )