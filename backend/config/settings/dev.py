from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
COOKIE_REFRESH = {**COOKIE_REFRESH, "SECURE": False}  # noqa: F405
