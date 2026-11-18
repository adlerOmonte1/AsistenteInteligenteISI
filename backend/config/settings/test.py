from .base import *  # noqa: F403

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
Q_CLUSTER = {**Q_CLUSTER, "sync": True}  # noqa: F405
LLM = {**LLM, "PROVEEDOR": "local"}  # noqa: F405
EMBEDDINGS = {**EMBEDDINGS, "PROVEEDOR": "local"}  # noqa: F405
MEDIA_ROOT = BASE_DIR / ".media-pruebas"  # noqa: F405
