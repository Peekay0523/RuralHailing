from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User
from drivers.models import Driver, Vehicle
from rides.models import Ride, RideRequest

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'profile_picture', 'date_of_birth', 'is_verified')
        read_only_fields = ('id', 'is_verified')

class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Driver
        fields = '__all__'
        read_only_fields = ('user', 'rating', 'total_rides', 'created_at', 'updated_at')

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class RideSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    
    class Meta:
        model = Ride
        fields = '__all__'

class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = '__all__'