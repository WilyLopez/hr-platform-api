from .base import *

DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)

# Render (como la mayoria de los PaaS) termina el TLS en su proxy y reenvia
# la peticion al contenedor por HTTP simple, agregando la cabecera
# X-Forwarded-Proto. Sin esto, Django cree que toda peticion llega por HTTP
# y con SECURE_SSL_REDIRECT=True entra en un bucle infinito de redirecciones.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Email - Use SMTP in production
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# Static files storage: WhiteNoise sirve los estaticos (incluido el admin de
# Django) directamente desde el contenedor, sin necesitar nginx ni un bucket
# aparte. El manifiesto comprime y agrega hash a cada archivo para cache-busting.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
