from django.conf import settings
from django.db import models


class CasoEvaluacion(models.Model):
    """Pregunta del golden set con la respuesta que se espera del asistente."""

    proceso = models.ForeignKey("conocimiento.Proceso", on_delete=models.CASCADE, related_name="casos")
    codigo = models.CharField(max_length=40)
    pregunta = models.TextField()
    intent_esperado = models.CharField(max_length=80, blank=True)
    ficha_esperada = models.CharField(max_length=30, blank=True)
    respuesta_clave = models.TextField(blank=True, help_text="Dato que la respuesta debe contener.")
    tipo = models.CharField(max_length=30, blank=True, help_text="normal, parafraseo, fuera_de_tema...")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "caso de evaluación"
        verbose_name_plural = "casos de evaluación"
        ordering = ["proceso__orden", "codigo"]
        constraints = [models.UniqueConstraint(fields=["proceso", "codigo"], name="caso_unico_por_proceso")]

    def __str__(self):
        return self.codigo


class Evaluacion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EJECUTANDO = "ejecutando", "Ejecutando"
        COMPLETADA = "completada", "Completada"
        ERROR = "error", "Error"

    class Motivo(models.TextChoices):
        MANUAL = "manual", "Ejecución manual"
        REVISION = "revision", "Envío a revisión"
        HUMO = "humo", "Prueba de humo tras publicar"

    proceso = models.ForeignKey(
        "conocimiento.Proceso", null=True, blank=True, on_delete=models.CASCADE, related_name="evaluaciones"
    )
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    motivo = models.CharField(max_length=20, choices=Motivo.choices, default=Motivo.MANUAL)
    limite_casos = models.PositiveIntegerField(null=True, blank=True)
    metricas = models.JSONField(default=dict, blank=True)
    mensaje = models.TextField(blank=True)
    iniciada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    creada = models.DateTimeField(auto_now_add=True)
    finalizada = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "evaluación"
        verbose_name_plural = "evaluaciones"
        ordering = ["-creada"]

    def __str__(self):
        return f"Evaluación {self.pk} ({self.get_motivo_display()})"


class ResultadoCaso(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name="resultados")
    caso = models.ForeignKey(CasoEvaluacion, on_delete=models.CASCADE, related_name="+")
    intent_obtenido = models.CharField(max_length=80, blank=True)
    confianza = models.FloatField(default=0)
    fichas_obtenidas = models.JSONField(default=list, blank=True)
    via = models.CharField(max_length=20)
    respuesta = models.TextField(blank=True)
    acierto_intent = models.BooleanField(null=True)
    acierto_ficha = models.BooleanField(null=True)
    clave_contenida = models.BooleanField(null=True)
    dato_inventado = models.BooleanField(default=False)

    class Meta:
        ordering = ["caso__codigo"]

    def __str__(self):
        return f"{self.caso.codigo} en evaluación {self.evaluacion_id}"
