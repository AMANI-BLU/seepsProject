# createadmin.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from getpass import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user or replace if it exists'

    def handle(self, *args, **options):
        self.create_admin_user()

    def create_admin_user(self):
        username = input('Enter admin username: ')
        email = input('Enter admin email: ')
        password = getpass('Enter admin password: ')
        confirm_password = getpass('Confirm admin password: ')

        # Validate email
        try:
            User._meta.get_field('email').run_validators(email)
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Invalid email: {", ".join(e.messages)}'))
            return

        # Validate password
        try:
            User._meta.get_field('password').run_validators(password)
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Invalid password: {", ".join(e.messages)}'))
            return

        # Confirm password
        if password != confirm_password:
            self.stdout.write(self.style.ERROR('Passwords do not match.'))
            return

        # Check if the user already exists
        admin_user = User.objects.filter(username=username).first()
        if admin_user:
            # Replace the existing admin user
            admin_user.email = email
            admin_user.set_password(password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user replaced successfully.'))
        else:
            # Create a new admin user
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Admin user created successfully.'))
