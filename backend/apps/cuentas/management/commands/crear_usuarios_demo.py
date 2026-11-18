import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.cuentas.models import Usuario

CUENTAS = [
    ("demo-centro", "superadmin", "Centro de Cómputo"),
    ("demo-revisor", "revisor", "Coordinación"),
    ("demo-editor", "editor", "Editor"),
    ("demo-lector", "lector", "Lector"),
]


class Command(BaseCommand):
    help = (
        "Crea una cuenta de demostración por rol para desarrollo y presentaciones. "
        "La contraseña sale de DEMO_PASSWORD. No se ejecuta en producción."
    )

    def handle(self, *args, **opciones):
        if not settings.DEBUG and os.environ.get("PERMITIR_DEMO") != "1":
            raise CommandError("Solo en desarrollo (DEBUG=True) o con PERMITIR_DEMO=1.")
        password = os.environ.get("DEMO_PASSWORD")
        if not password:
            raise CommandError("Defina DEMO_PASSWORD en el entorno (ver .env.example).")
        for username, rol, nombre in CUENTAS:
            usuario, creado = Usuario.objects.get_or_create(
                username=username, defaults={"rol": rol, "first_name": nombre}
            )
            usuario.rol = rol
            usuario.set_password(password)
            usuario.save()
            self.stdout.write(f"{'Creada' if creado else 'Actualizada'}: {username} ({rol})")
