from django.db import models


class Conversacion(models.Model):
    """Estado del diálogo de una sesión anónima del widget.

    La sesión es un UUID que genera el navegador; no identifica a la persona.
    """

    sesion = models.UUIDField(unique=True)
    proceso_actual = models.ForeignKey(
        "conocimiento.Proceso", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    ficha_actual = models.ForeignKey(
        "conocimiento.Ficha", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    intent_pendiente = models.CharField(
        max_length=80, blank=True, help_text="Intent que espera una entidad (p. ej. el número de fase)."
    )
    entidades = models.JSONField(default=dict, blank=True)
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)
    mensajes = models.PositiveIntegerField(default=0)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "conversación"
        verbose_name_plural = "conversaciones"

    def __str__(self):
        return str(self.sesion)
