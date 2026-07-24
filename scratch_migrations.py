import os
import django
from django.core.management import call_command
import sys
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hopebridge.settings.base')
django.setup()

old_stdout = sys.stdout
sys.stdout = my_stdout = io.StringIO()

try:
    print("Running makemigrations...")
    call_command('makemigrations', 'volunteers', 'drives', 'donations', 'accounts', 'events', 'programs', 'invoices', 'notifications', 'custom_admin', 'pages', 'donors')
    print("Running migrate...")
    call_command('migrate')
except Exception as e:
    print(f"Error: {e}")

sys.stdout = old_stdout

with open('scratch_migrations_output.txt', 'w', encoding='utf-8') as f:
    f.write(my_stdout.getvalue())

print("Migrations executed. Check scratch_migrations_output.txt")
