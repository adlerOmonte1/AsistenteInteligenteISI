from django.conf import settings
from django.db import models

from .catalogo import Proceso
from .ficha import Ficha


class Documento(models.Model):
    """Resolución, reglamento, formato o guía que se publica en el portal.

    Es la biblioteca normativa del portal: el estudiante consulta y descarga
    los documentos oficiales de cada trámite desde un solo lugar.
    """

    class Tipo(models.TextChoices):
        RESOLUCION = "resolucion", "Resolución"
        REGLAMENTO = "reglamento", "Reglamento"
        FORMATO = "formato", "Formato o anexo"
        FLUJOGRAMA = "flujograma", "Flujograma"
        GUIA = "guia", "Guía"
        OTRO = "otro", "Otro"

    proceso = models.ForeignKey(Proceso, null=True, blank=True, on_delete=models.SET_NULL, related_name="documentos")
    titulo = models.CharField(max_length=300)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.OTRO)
    numero = models.CharField(max_length=120, blank=True, help_text="Ej.: Res. N.° 2367-2025-R-CU-UDH")
    fecha_emision = models.DateField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to="documentos/%Y/", blank=True)
    url_externa = models.URLField(blank=True)
    publico = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        verbose_name = "documento"
        ordering = ["-fecha_emision", "titulo"]

    def __str__(self):
        return self.titulo


class CargaDocumento(models.Model):
    """Documento subido para que el sistema proponga fichas en borrador.

    Las fichas propuestas nunca se publican solas: pasan por revisión.
    """

    class Estado(models.TextChoices):
        PROCESANDO = "procesando", "Procesando"
        COMPLETADA = "completada", "Completada"
        ERROR = "error", "Error"

    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name="cargas")
    archivo = models.FileField(upload_to="cargas/%Y/")
    nombre_original = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PROCESANDO)
    mensaje = models.TextField(blank=True)
    fichas_propuestas = models.ManyToManyField(Ficha, blank=True, related_name="+")
    creada = models.DateTimeField(auto_now_add=True)
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        verbose_name = "carga de documento"
        ordering = ["-creada"]

    def __str__(self):
        return self.nombre_original
