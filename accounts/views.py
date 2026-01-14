from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render
from django.views import View
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .models import User
from .serializers import UserSerializer

User = get_user_model()

# HTML Views for browser access
class RegisterHTMLView(View):
    def get(self, request):
        # Only show the registration form
        return render(request, 'accounts/register.html')

class LoginHTMLView(View):
    def get(self, request):
        # Only show the login form
        return render(request, 'accounts/login.html')

# API Views for API access
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Automatically log in the user after registration
        django_login(request, user)

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            user = authenticate(request, username=email, password=password)

            if user:
                django_login(request, user)
                return Response(UserSerializer(user).data)
            else:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {'error': 'Email and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Automatically log in the user after registration
        django_login(request, user)
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            
            if user:
                django_login(request, user)
                return Response(UserSerializer(user).data)
            else:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {'error': 'Email and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )

class LogoutView(APIView):
    def post(self, request):
        django_logout(request)
        return Response({'message': 'Logged out successfully'})