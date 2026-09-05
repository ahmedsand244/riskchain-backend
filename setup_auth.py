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
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
            socialapp_id integer NOT NULL REFERENCES socialaccount_socialapp (id) DEFERRABLE INITIALLY DEFERRED, 
            site_id integer NOT NULL REFERENCES django_site (id) DEFERRABLE INITIALLY DEFERRED
        );
    ''')
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS socialaccount_socialapp_sites_socialapp_id_site_id_71a9a768_uniq 
        ON socialaccount_socialapp_sites (socialapp_id, site_id);
    ''')

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

if not User.objects.filter(email='google.agent@riskchain.ai').exists():
    user = User.objects.create_user(
        username='google_agent',
        email='google.agent@riskchain.ai',
        first_name='Google Agent'
    )
    user.set_unusable_password()
    user.save()
    print("Google Agent demo user created.")
