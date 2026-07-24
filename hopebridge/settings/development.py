"""
Development settings for HopeBridge project.
"""

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email - Console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'HopeBridge NGO <noreply@hopebridge.org>'

# Static files - No compression in dev
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
