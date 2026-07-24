import os
import sys
import shutil
import glob
import django
from django.core.management import call_command

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hopebridge.settings.development')

def clean_old_migrations():
    """Purge old migration files from all local app directories."""
    base_dir = os.path.dirname(__file__)
    apps = ['accounts', 'donations', 'drives', 'events', 'programs', 'volunteers', 'notifications', 'invoices', 'pages', 'custom_admin']
    
    for app in apps:
        mig_dir = os.path.join(base_dir, app, 'migrations')
        if os.path.exists(mig_dir):
            for f in os.listdir(mig_dir):
                if f != '__init__.py' and (f.endswith('.py') or f.endswith('.pyc')):
                    file_path = os.path.join(mig_dir, f)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            print(f"Cleaned old migration: {app}/migrations/{f}")
                    except Exception as e:
                        print(f"Notice: Could not remove {file_path}: {e}")
                elif f == '__pycache__':
                    try:
                        shutil.rmtree(os.path.join(mig_dir, f))
                    except Exception:
                        pass
        else:
            # Create migrations folder if missing
            os.makedirs(mig_dir, exist_ok=True)
            with open(os.path.join(mig_dir, '__init__.py'), 'w') as fp:
                pass
            print(f"Created migrations directory for {app}")

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    # Remove old database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Removed old db.sqlite3.")
        except Exception as e:
            print(f"Notice: Could not remove old db.sqlite3: {e}")

    # Clean old migrations
    print("--- 0. Cleaning old broken migration files ---")
    clean_old_migrations()

    django.setup()
    
    print("\n--- 1. Making fresh migrations for all apps ---")
    call_command('makemigrations', 'accounts', 'donations', 'drives', 'events', 'programs', 'volunteers', 'notifications', 'invoices')
    
    print("\n--- 2. Running migrate ---")
    call_command('migrate')
    
    print("\n--- 3. Creating superadmin account ---")
    from accounts.models import CustomUser
    if not CustomUser.objects.filter(email='admin@hopebridge.org').exists():
        admin_user = CustomUser.objects.create_superuser(
            username='admin@hopebridge.org',
            email='admin@hopebridge.org',
            password='adminpassword123',
            first_name='NGO',
            last_name='Admin',
            role='admin'
        )
        print("Created default admin user: email='admin@hopebridge.org', password='adminpassword123'")
    else:
        print("Admin user already exists.")
        
    print("\n✅ SUCCESS! All migrations, database initialization, and admin accounts complete!")

if __name__ == '__main__':
    main()
