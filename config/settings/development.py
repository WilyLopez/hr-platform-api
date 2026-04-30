from .base import *

DEBUG = True

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '[::1]'])

# Show emails in console during development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable password validation in development
AUTH_PASSWORD_VALIDATORS = []

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Internal IPs for debug toolbar or other tools
INTERNAL_IPS = ['127.0.0.1']
