from django.conf import settings
from django.db import models


class Configuracion(models.Model):
    """Parámetros que el Centro de Cómputo ajusta desde el panel sin redesplegar.

    Es una fila única (pk=1). Los valores por defecto salen de ``settings.ASISTENTE``.
    """

    umbral_determinista = models.FloatField(default=0.75)
    umbral_desambiguacion = models.FloatField(default=0.40)
    intentos_antes_de_derivar = models.PositiveSmallIntegerField(default=2)
    limite_usd_mes = models.DecimalField(max_digits=8, decimal_places=2, default=8)
    llm_habilitado = models.BooleanField(
        default=True, help_text="Apagarlo deja solo la vía determinista y la derivación."
    )
    mensaje_bienvenida = models.TextField(
        default=(
            "Buen día. Soy el Asistente Académico del P.A. de Ingeniería de Sistemas e Informática. "
            "Puedo orientarle sobre prácticas preprofesionales, bachiller, título y traslados. "
            "¿En qué trámite le ayudo?"
        )
    )
    contacto_derivacion = models.TextField(
        default=(
            "Para atención personalizada comuníquese con la Coordinación del P.A. de Ingeniería de "
            "Sistemas e Informática."
        ),
        help_text="Texto que se muestra al derivar a una persona. Solo datos oficiales.",
    )
    aviso_legal = models.TextField(
        default=(
            "Este asistente orienta con base en la normativa vigente del programa. No reemplaza la "
            "comunicación oficial de la Coordinación. No ingrese datos personales."
        )
    )
    actualizado = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        verbose_name = "configuración"

    def __str__(self):
        return "Configuración del asistente"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def actual(cls) -> "Configuracion":
        cfg = settings.ASISTENTE
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "umbral_determinista": cfg["UMBRAL_DETERMINISTA"],
                "umbral_desambiguacion": cfg["UMBRAL_DESAMBIGUACION"],
                "intentos_antes_de_derivar": cfg["INTENTOS_ANTES_DE_DERIVAR"],
                "limite_usd_mes": cfg["LIMITE_USD_MES"],
            },
        )
        return obj
