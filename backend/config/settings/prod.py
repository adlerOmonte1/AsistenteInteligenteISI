from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import SECRET_KEY, env, env_lista

DEBUG = False

if SECRET_KEY.startswith("solo-para-desarrollo"):
    raise ImproperlyConfigured("Defina DJANGO_SECRET_KEY en el entorno de producción.")

# "localhost" permite el healthcheck interno de Docker; desde fuera solo entra el dominio vía Nginx.
ALLOWED_HOSTS = [*env_lista("DJANGO_ALLOWED_HOSTS"), "localhost"]
CSRF_TRUSTED_ORIGINS = env_lista("CSRF_TRUSTED_ORIGINS")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", "false").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "0"))
X_FRAME_OPTIONS = "DENY"
