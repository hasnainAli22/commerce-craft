from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin'

        try:
            # Check if user exists
            user = User.objects.get(username=username)
            # If user exists, update password
            user.set_password(password)
            user.is_admin = True
            user.is_active = True
            user.is_staff = True
            user.save()
            print(f"Password updated for user {username}")
        except User.DoesNotExist:
            # Create user if not exists
            user = User.objects.create_user(username=username, password=password)
            user.is_admin = True
            user.is_active = True
            user.is_staff = True
            print(f"User {username} created")