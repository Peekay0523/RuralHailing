import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

logger = logging.getLogger('tracking')

class TrackingConsentMiddleware(MiddlewareMixin):
    """
    Middleware to handle user tracking based on consent
    """
    
    def process_request(self, request):
        # Store the user's tracking consent status in the request
        # Check if user attribute exists (it might not be available early in the request cycle)
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.user_tracking_consent = request.user.tracking_consent_given
        else:
            request.user_tracking_consent = False
            
        return None
    
    def process_response(self, request, response):
        # Log user activity if they have given consent
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            hasattr(request.user, 'tracking_consent_given') and
            request.user.tracking_consent_given):
            
            # Track user activity
            self.log_user_activity(request)
            
        return response
    
    def log_user_activity(self, request):
        """
        Log user activity based on their consent
        """
        try:
            user = request.user
            path = request.path
            method = request.method
            timestamp = timezone.now()
            
            # Log the activity (in a real app, you might store this in a database)
            logger.info(f"User {user.email} accessed {method} {path} at {timestamp}")
            
            # Additional tracking logic can be added here
            # For example, storing in a database table, sending to analytics service, etc.
            
        except Exception as e:
            # Log any errors in tracking without affecting the main application
            logger.error(f"Error in tracking user activity: {str(e)}")