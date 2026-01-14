import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rural_hailing.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    print(f'Superuser "{username}" created successfully!')
else:
    print(f'Superuser "{username}" already exists.')