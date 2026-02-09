from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to find the user by email
        try:
            user = User.objects.get(Q(email=username) | Q(username=username))
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing difference
            # between existing and non-existing users
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Return the first user if multiple users are found
            user = User.objects.filter(Q(email=username) | Q(username=username)).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None