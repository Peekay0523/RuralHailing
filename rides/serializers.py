from rest_framework import serializers
from .models import Ride, RideRequest
from accounts.serializers import UserSerializer
from drivers.serializers import DriverSerializer

class RideSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    
    class Meta:
        model = Ride
        fields = '__all__'

class RideRequestSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)
    
    class Meta:
        model = RideRequest
        fields = '__all__'