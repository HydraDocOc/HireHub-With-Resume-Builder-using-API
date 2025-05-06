from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.hashers import make_password
from jobs.models import CustomUser

class Command(BaseCommand):
    help = 'Load initial data for the application'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Loading initial data...'))
        
        # Load fixtures
        call_command('loaddata', 'initial_data.json', verbosity=1)
        
        # Make sure the admin user has a properly hashed password
        try:
            admin = CustomUser.objects.get(email='admin@gmail.com')
            admin.password = make_password('admin123')  # Set known password
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user updated: {admin.email}'))
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.WARNING('Admin user not found in fixtures'))
        
        self.stdout.write(self.style.SUCCESS('Initial data loaded successfully!'))
