from .base import *
import os

SECRET_KEY = os.environ.get('BIASET_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['localhost', '*']

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = False
EMAIL_HOST = os.environ.get('email-host')
EMAIL_HOST_USER = os.environ.get('email-user')
EMAIL_HOST_PASSWORD = os.environ.get('email-password')
EMAIL_PORT = 587
