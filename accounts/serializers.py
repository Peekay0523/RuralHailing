from rest_framework import serializers  
from django.contrib.auth import get_user_model  
from .models import User  
from drivers.models import Driver, Vehicle  
from rides.models import Ride, RideRequest  
  
User = get_user_model()  
  
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'profile_picture', 'date_of_birth', 'is_verified', 'tracking_consent_given', 'tracking_consent_date')
        read_only_fields = ('id', 'is_verified', 'tracking_consent_date')
  
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    tracking_consent = serializers.BooleanField(required=True, write_only=True, 
                                               error_messages={'required': 'You must agree to allow tracking to use this application.'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'password', 'password_confirm', 'tracking_consent')
        read_only_fields = ('id',)
  
    def validate(self, attrs):  
        if attrs['password'] != attrs['password_confirm']:  
            raise serializers.ValidationError("Passwords don't match")  
        return attrs  
  
    def create(self, validated_data):
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        # Extract password before creating user
        password = validated_data.pop('password')
        # Extract tracking_consent
        tracking_consent = validated_data.pop('tracking_consent', False)
        
        # Create user with email as username
        user = User(**validated_data)
        user.set_password(password)  # Properly hash the password
        
        # Set tracking consent
        user.tracking_consent_given = tracking_consent
        if tracking_consent:
            from django.utils import timezone
            user.tracking_consent_date = timezone.now()
            
        user.save()
        return user
  
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
