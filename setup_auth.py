"""
Run this script once with:
    python setup_auth.py

It will:
1. Apply all Django database migrations
2. Create a demo user for testing
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riskchain_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Run migrations programmatically
from django.core.management import call_command
print("Applying migrations...")
call_command('migrate', verbosity=1)
print("Migrations applied!")

# Ensure Site ID=1 exists for allauth
from django.contrib.sites.models import Site
site, created = Site.objects.get_or_create(id=1, defaults={'domain': 'localhost', 'name': 'Localhost'})
if not created and site.domain == 'example.com':
    site.domain = 'localhost'
    site.name = 'Localhost'
    site.save()
print("Site ID=1 configured.")

# Create demo user
from django.contrib.auth.models import User
if not User.objects.filter(email='demo@riskchain.ai').exists():
    User.objects.create_user(
        username='demo',
        email='demo@riskchain.ai',
        password='RiskChain2025!',
        first_name='Basmala'
    )
    print("Demo user created: demo@riskchain.ai / RiskChain2025!")
else:
    print("Demo user already exists.")
