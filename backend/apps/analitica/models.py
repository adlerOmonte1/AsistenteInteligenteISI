from django.db import models


class Consulta(models.Model):
    """Registro de una pregunta y su respuesta, sin datos personales.

    ``pregunta`` se guarda ya enmascarada (DNI, códigos, teléfonos y correos
    personales reemplazados). Se borra a los 12 meses (Ley 29733).
    """

    class Via(models.TextChoices):
        DETERMINISTA = "determinista", "Determinista"
        DESAMBIGUACION = "desambiguacion", "Desambiguación"
        RAG = "rag", "RAG"
        DERIVACION = "derivacion", "Derivación"
        ACLARACION = "aclaracion", "Aclaración de entidad"

    sesion = models.UUIDField(db_index=True)
    proceso = models.ForeignKey(
        "conocimiento.Proceso", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    pregunta = models.TextField()
    respuesta = models.TextField(blank=True)
    intent = models.CharField(max_length=80, blank=True)
    confianza = models.FloatField(default=0)
    via = models.CharField(max_length=20, choices=Via.choices)
    fichas_citadas = models.JSONField(default=list, blank=True)
    derivada = models.BooleanField(default=False)
    validacion_fallida = models.BooleanField(default=False)
    datos_no_respaldados = models.JSONField(default=list, blank=True)
    motivo = models.CharField(max_length=40, blank=True, help_text="Por qué se tomó la vía (p. ej. limite_de_gasto).")
    tokens_entrada = models.PositiveIntegerField(default=0)
    tokens_salida = models.PositiveIntegerField(default=0)
    tokens_embedding = models.PositiveIntegerField(default=0)
    costo_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    latencia_ms = models.PositiveIntegerField(default=0)
    util = models.BooleanField(null=True, blank=True)
    creada = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "consulta"
        ordering = ["-creada"]
        indexes = [models.Index(fields=["via", "creada"]), models.Index(fields=["derivada", "creada"])]

    def __str__(self):
        return f"{self.creada:%Y-%m-%d %H:%M} · {self.via}"
