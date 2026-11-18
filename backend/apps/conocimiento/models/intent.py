from django.db import models
from pgvector.django import HnswIndex, VectorField

from .catalogo import Proceso
from .ficha import Ficha


class Intent(models.Model):
    """Intención del estudiante, con sus ejemplos y la ficha que la responde.

    ``secciones`` limita qué partes de la ficha se muestran en la vía
    determinista: el intent ``CPP_costo`` solo necesita la sección «Pago».
    Vacío equivale a mostrar todas.
    """

    proceso = models.ForeignKey(Proceso, on_delete=models.PROTECT, related_name="intents")
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    fichas = models.ManyToManyField(Ficha, blank=True, related_name="intents")
    secciones = models.JSONField(default=list, blank=True)
    entidades = models.JSONField(default=list, blank=True)
    si_falta_entidad = models.TextField(blank=True)
    respuesta_fija = models.TextField(
        blank=True, help_text="Para intents sin ficha (saludo, cierre): texto que se responde tal cual."
    )
    activo = models.BooleanField(default=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "intent"
        ordering = ["proceso__orden", "nombre"]

    def __str__(self):
        return self.nombre


class EjemploIntent(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name="ejemplos")
    texto = models.CharField(max_length=500)
    proveedor_embedding = models.CharField(max_length=30, blank=True)
    embedding = VectorField(dimensions=768, null=True, blank=True)

    class Meta:
        verbose_name = "ejemplo de intent"
        indexes = [
            HnswIndex(
                name="ejemplo_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]

    def __str__(self):
        return self.texto


class Plantilla(models.Model):
    """Texto de respuesta reutilizable (bienvenida, cierre, dato pendiente...)."""

    proceso = models.ForeignKey(Proceso, null=True, blank=True, on_delete=models.CASCADE, related_name="plantillas")
    clave = models.CharField(max_length=80)
    texto = models.TextField()

    class Meta:
        verbose_name = "plantilla"
        ordering = ["proceso__orden", "clave"]
        constraints = [models.UniqueConstraint(fields=["proceso", "clave"], name="plantilla_unica_por_proceso")]

    def __str__(self):
        return self.clave


class Pendiente(models.Model):
    """Dato que falta confirmar con Coordinación (pendientes.md)."""

    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name="pendientes")
    codigo = models.CharField(max_length=40)
    descripcion = models.TextField()
    pregunta = models.TextField(blank=True, help_text="Pregunta concreta para Coordinación.")
    fichas = models.ManyToManyField(Ficha, blank=True, related_name="pendientes")
    resuelto = models.BooleanField(default=False)
    resolucion = models.TextField(blank=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "pendiente"
        ordering = ["resuelto", "proceso__orden", "codigo"]
        constraints = [models.UniqueConstraint(fields=["proceso", "codigo"], name="pendiente_unico_por_proceso")]

    def __str__(self):
        return self.codigo
