from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

User = get_user_model()

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
    
    def test_email_backend_authentication(self):
        """Test that the email backend allows authentication with email"""
        # Test authentication using the custom backend
        from django.contrib.auth import authenticate
        
        user = authenticate(username='test@example.com', password='testpassword123')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
        # Test authentication with wrong password
        user = authenticate(username='test@example.com', password='wrongpassword')
        self.assertIsNone(user)
    
    def test_registration_api(self):
        """Test the registration API endpoint"""
        registration_url = reverse('accounts:api-register')
        
        # Test successful registration
        response = self.client.post(
            registration_url,
            data=json.dumps({
                'email': 'newuser@example.com',
                'username': 'newuser@example.com',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'newpassword123',
                'password_confirm': 'newpassword123',
                'user_type': 'passenger'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Verify user was created
        new_user = User.objects.get(email='newuser@example.com')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'User')
    
    def test_login_api_with_email(self):
        """Test the login API endpoint with email"""
        login_url = reverse('accounts:api-login')
        
        # Test successful login
        response = self.client.post(
            login_url,
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'testpassword123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Test failed login
        response = self.client.post(
            login_url,
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_duplicate_registration_error_handling(self):
        """Test that duplicate registrations are handled properly"""
        registration_url = reverse('accounts:api-register')
        
        # Register the same user twice
        response1 = self.client.post(
            registration_url,
            data=json.dumps({
                'email': 'duplicate@example.com',
                'username': 'duplicate@example.com',
                'first_name': 'Duplicate',
                'last_name': 'User',
                'password': 'newpassword123',
                'password_confirm': 'newpassword123',
                'user_type': 'passenger'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response1.status_code, 201)
        
        # Second registration should fail due to unique email constraint
        response2 = self.client.post(
            registration_url,
            data=json.dumps({
                'email': 'duplicate@example.com',
                'username': 'duplicate@example.com',
                'first_name': 'Duplicate',
                'last_name': 'User',
                'password': 'newpassword123',
                'password_confirm': 'newpassword123',
                'user_type': 'passenger'
            }),
            content_type='application/json'
        )
        
        self.assertNotEqual(response2.status_code, 201)