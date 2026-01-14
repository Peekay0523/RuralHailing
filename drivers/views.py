from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Driver, Vehicle
from .serializers import DriverSerializer, VehicleSerializer
from accounts.serializers import UserSerializer

User = get_user_model()

class DriverRegistrationView(generics.CreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Check if user is already a driver
        if hasattr(self.request.user, 'driver_profile'):
            raise serializers.ValidationError("User already has a driver profile")

        # Ensure the user type is set to driver
        user = self.request.user
        user.user_type = 'driver'
        user.save()

        # Create the driver profile
        serializer.save(user=user)

class AvailableDriversView(generics.ListAPIView):
    serializer_class = DriverSerializer

    def get_queryset(self):
        return Driver.objects.filter(status='available', is_active=True)

class DriverProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            driver = request.user.driver_profile
            serializer = DriverSerializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response({'error': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            driver = request.user.driver_profile
            serializer = DriverSerializer(driver, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Driver.DoesNotExist:
            return Response({'error': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateDriverStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            driver = request.user.driver_profile
            status_value = request.data.get('status')

            if status_value in ['available', 'on_ride', 'offline']:
                driver.status = status_value
                driver.save()

                serializer = DriverSerializer(driver)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'Invalid status value'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Driver.DoesNotExist:
            return Response({'error': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)