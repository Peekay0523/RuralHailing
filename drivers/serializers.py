from rest_framework import serializers
from .models import Driver, Vehicle
from accounts.models import User

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'
        read_only_fields = ('user', 'rating', 'total_rides', 'created_at', 'updated_at')

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'