"""Configuración común a todos los entornos.

Los valores sensibles y los que cambian entre entornos se leen de variables de
entorno. La lista completa está en `.env.example` en la raíz del repositorio.
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_DIR = BASE_DIR.parent


def _cargar_env_local(ruta: Path):
    """Lee backend/.env en desarrollo. Las variables ya definidas en el entorno tienen prioridad."""
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip("\"'"))


_cargar_env_local(BASE_DIR / ".env")


def env(nombre, defecto=None):
    return os.environ.get(nombre, defecto)


def env_bool(nombre, defecto=False):
    valor = os.environ.get(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes")


def env_lista(nombre, defecto=""):
    return [v.strip() for v in os.environ.get(nombre, defecto).split(",") if v.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", "solo-para-desarrollo-no-usar-en-produccion")
DEBUG = False
ALLOWED_HOSTS = env_lista("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_q",
    "drf_spectacular",
    "apps.cuentas",
    "apps.sistema",
    "apps.conocimiento",
    "apps.nlu",
    "apps.recuperacion",
    "apps.generacion",
    "apps.validacion",
    "apps.dialogo",
    "apps.evaluacion",
    "apps.analitica",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

DATABASES = {
    "default": dj_database_url.parse(
        env("DATABASE_URL", "postgres://asistente:asistente@localhost:5433/asistente"),
        conn_max_age=60,
    )
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_asistente",
    }
}

AUTH_USER_MODEL = "cuentas.Usuario"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / "media")))
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "comun.paginacion.PaginacionEstandar",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "comun.excepciones.manejar_excepcion",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

COOKIE_REFRESH = {
    "NOMBRE": "udh_refresh",
    "RUTA": "/api/v1/auth/",
    "SECURE": True,
    "SAMESITE": "Strict",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API del Asistente Virtual UDH",
    "DESCRIPTION": "Consultas de trámites del P.A. de Ingeniería de Sistemas e Informática.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1",
}

CORS_ALLOWED_ORIGINS = env_lista(
    "CORS_ALLOWED_ORIGINS", "http://localhost:4200,http://localhost:4201,http://localhost:4202"
)
CORS_ALLOW_CREDENTIALS = True

Q_CLUSTER = {
    "name": "asistente",
    "orm": "default",
    "workers": int(env("Q_WORKERS", "2")),
    "timeout": 600,
    "retry": 900,
    "max_attempts": 2,
    "catch_up": False,
}

# Parámetros del asistente. Los marcados con * se pueden sobrescribir desde la
# pantalla Configuración del panel (modelo sistema.Configuracion).
ASISTENTE = {
    "UMBRAL_DETERMINISTA": 0.75,  # *
    "UMBRAL_DESAMBIGUACION": 0.40,  # *
    "INTENTOS_ANTES_DE_DERIVAR": 2,  # *
    "LIMITE_USD_MES": float(env("LIMITE_USD_MES", "8")),  # *
    "SECCIONES_RAG": 4,
    "SIMILITUD_MINIMA_RAG": 0.35,
    "MAX_TOKENS_SALIDA": 600,
    "LONGITUD_MAXIMA_MENSAJE": 500,
    "VECINOS_INTENT": 7,
    "LIMITE_MENSAJES_SESION_HORA": int(env("LIMITE_MENSAJES_SESION_HORA", "30")),
    "LIMITE_MENSAJES_IP_HORA": int(env("LIMITE_MENSAJES_IP_HORA", "300")),
    "INTENTOS_LOGIN": 5,
    "BLOQUEO_LOGIN_MINUTOS": 15,
    "MESES_RETENCION_CONSULTAS": 12,
    "CARPETA_CONOCIMIENTO": Path(env("CARPETA_CONOCIMIENTO", str(REPO_DIR / "knowledge-base" / "procesos"))),
}

# Proveedores externos. "local" funciona sin red ni clave y sirve para
# desarrollo y pruebas; en producción se usa "gemini" u "openai".
LLM = {
    "PROVEEDOR": env("LLM_PROVEEDOR", "local"),
    "MODELO": env("LLM_MODELO", "gemini-2.5-flash-lite"),
    "API_KEY": env("LLM_API_KEY", ""),
    "URL_BASE": env("LLM_URL_BASE", ""),
    "PRECIO_ENTRADA_MILLON": float(env("LLM_PRECIO_ENTRADA_MILLON", "0.10")),
    "PRECIO_SALIDA_MILLON": float(env("LLM_PRECIO_SALIDA_MILLON", "0.40")),
    "TIMEOUT": float(env("LLM_TIMEOUT", "30")),
}
EMBEDDINGS = {
    "PROVEEDOR": env("EMBED_PROVEEDOR", "local"),
    "MODELO": env("EMBED_MODELO", "gemini-embedding-001"),
    "API_KEY": env("EMBED_API_KEY", env("LLM_API_KEY", "")),
    "URL_BASE": env("EMBED_URL_BASE", ""),
    "DIMENSIONES": 768,
    "PRECIO_MILLON": float(env("EMBED_PRECIO_MILLON", "0.15")),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
    "handlers": {"consola": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["consola"], "level": env("LOG_LEVEL", "INFO")},
}
