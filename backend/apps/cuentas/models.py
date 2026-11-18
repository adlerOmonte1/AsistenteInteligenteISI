from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Cuenta del personal administrativo. Los estudiantes no tienen cuenta."""

    class Rol(models.TextChoices):
        SUPERADMIN = "superadmin", "Centro de Cómputo"
        REVISOR = "revisor", "Revisor (Coordinación)"
        EDITOR = "editor", "Editor"
        LECTOR = "lector", "Lector"

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.EDITOR)
    facultad = models.ForeignKey(
        "conocimiento.Facultad",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text="Vacío: puede operar en todas las facultades.",
    )

    class Meta:
        verbose_name = "usuario"
        ordering = ["username"]

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.rol = self.Rol.SUPERADMIN
        super().save(*args, **kwargs)
