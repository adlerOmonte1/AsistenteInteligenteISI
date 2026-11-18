from django.db import models


class Facultad(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    sigla = models.CharField(max_length=20, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "facultad"
        verbose_name_plural = "facultades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Programa(models.Model):
    """Programa académico (P.A.). Cada proceso pertenece a uno."""

    facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT, related_name="programas")
    nombre = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "programa académico"
        ordering = ["facultad__nombre", "nombre"]
        constraints = [models.UniqueConstraint(fields=["facultad", "nombre"], name="programa_unico_por_facultad")]

    def __str__(self):
        return self.nombre


class Proceso(models.Model):
    """Trámite académico: prácticas, bachiller, título, traslados...

    ``prefijos`` son los prefijos de los códigos de ficha e intent que le
    pertenecen (``["BAC", "CPP"]``). El proceso ``general`` agrupa los intents
    transversales (``GEN_``) y no tiene fichas.
    """

    programa = models.ForeignKey(Programa, on_delete=models.PROTECT, related_name="procesos")
    clave = models.SlugField(max_length=60)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    prefijos = models.JSONField(default=list, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)
    visible_en_portal = models.BooleanField(default=True)

    class Meta:
        verbose_name = "proceso"
        ordering = ["orden", "nombre"]
        constraints = [models.UniqueConstraint(fields=["programa", "clave"], name="proceso_unico_por_programa")]

    def __str__(self):
        return self.nombre

    @property
    def facultad_id(self):
        return self.programa.facultad_id
