from django.conf import settings
from django.db import models

from .catalogo import Proceso

# Secciones fijas del contrato de fichas (docs/03-arquitectura/base-conocimiento/esquema_metadatos.md §3)
SECCIONES = ("requisitos", "pasos", "pago", "plazo", "enviar_a", "siguiente_fase")
TITULOS_SECCION = {
    "requisitos": "Requisitos",
    "pasos": "Pasos",
    "pago": "Pago",
    "plazo": "Plazo",
    "enviar_a": "Enviar a",
    "siguiente_fase": "Siguiente fase",
    "informacion_adicional": "Información adicional",
}


class Ficha(models.Model):
    """Una fase o etapa de un trámite: la unidad de conocimiento del asistente.

    Los campos de esta tabla son el **borrador** que edita el panel. Lo que el
    asistente responde sale siempre de ``version_publicada`` (una copia
    inmutable en ``VersionFicha``), de modo que editar una ficha publicada no
    cambia ninguna respuesta hasta que el revisor la aprueba.
    """

    class EstadoDato(models.TextChoices):
        CONFIRMADO = "confirmado", "Confirmado"
        PENDIENTE = "pendiente", "Pendiente de confirmar"

    class EstadoRevision(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        EN_REVISION = "en_revision", "En revisión"
        PUBLICADA = "publicada", "Publicada"
        RECHAZADA = "rechazada", "Rechazada"

    proceso = models.ForeignKey(Proceso, on_delete=models.PROTECT, related_name="fichas")
    codigo = models.CharField(max_length=30, help_text="Identificador del contrato, p. ej. BAC_P02.")
    fase = models.PositiveSmallIntegerField(default=0)
    titulo = models.CharField(max_length=300)
    fuente = models.TextField(help_text="Norma o documento oficial que respalda la ficha.")
    vigencia = models.DateField(null=True, blank=True)
    vigencia_texto = models.CharField(max_length=100, blank=True, help_text="Se usa cuando no hay fecha exacta.")
    estado_dato = models.CharField(max_length=20, choices=EstadoDato.choices, default=EstadoDato.PENDIENTE)

    requisitos = models.TextField(blank=True)
    pasos = models.TextField(blank=True)
    pago = models.TextField(blank=True)
    plazo = models.TextField(blank=True)
    enviar_a = models.TextField(blank=True)
    siguiente_fase = models.TextField(blank=True)
    informacion_adicional = models.TextField(blank=True)
    palabras_clave = models.JSONField(default=list, blank=True)

    estado_revision = models.CharField(max_length=20, choices=EstadoRevision.choices, default=EstadoRevision.BORRADOR)
    observaciones = models.TextField(blank=True, help_text="Observaciones del revisor al rechazar.")
    version_publicada = models.ForeignKey(
        "VersionFicha", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    reemplazada_por = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="reemplaza_a"
    )

    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    actualizada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        verbose_name = "ficha"
        ordering = ["proceso__orden", "fase", "codigo"]
        constraints = [models.UniqueConstraint(fields=["proceso", "codigo"], name="ficha_unica_por_proceso")]
        indexes = [models.Index(fields=["codigo"])]

    def __str__(self):
        return f"{self.codigo} · {self.titulo}"

    @property
    def vigencia_legible(self) -> str:
        return self.vigencia.isoformat() if self.vigencia else (self.vigencia_texto or "no indicada")

    def contenido(self) -> dict:
        """Copia serializable del borrador, la misma forma que guarda VersionFicha."""
        datos = {
            "codigo": self.codigo,
            "proceso": self.proceso.clave,
            "fase": self.fase,
            "titulo": self.titulo,
            "fuente": self.fuente,
            "vigencia": self.vigencia_legible,
            "estado_dato": self.estado_dato,
            "informacion_adicional": self.informacion_adicional,
            "palabras_clave": list(self.palabras_clave or []),
        }
        for seccion in SECCIONES:
            datos[seccion] = getattr(self, seccion)
        return datos

    def aplicar_contenido(self, datos: dict):
        """Carga en el borrador el contenido de una versión (para revertir)."""
        self.fase = datos.get("fase", self.fase)
        self.titulo = datos.get("titulo", self.titulo)
        self.fuente = datos.get("fuente", self.fuente)
        self.estado_dato = datos.get("estado_dato", self.estado_dato)
        self.informacion_adicional = datos.get("informacion_adicional", "")
        self.palabras_clave = datos.get("palabras_clave", [])
        for seccion in SECCIONES:
            setattr(self, seccion, datos.get(seccion, ""))

    @property
    def tiene_cambios_sin_publicar(self) -> bool:
        if self.version_publicada is None:
            return True
        return self.version_publicada.contenido != self.contenido()


class VersionFicha(models.Model):
    """Copia inmutable de una ficha en el momento en que se publicó."""

    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name="versiones")
    numero = models.PositiveIntegerField()
    contenido = models.JSONField()
    nota = models.CharField(max_length=300, blank=True)
    publicada_en = models.DateTimeField(auto_now_add=True)
    publicada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        verbose_name = "versión de ficha"
        verbose_name_plural = "versiones de fichas"
        ordering = ["ficha", "-numero"]
        constraints = [models.UniqueConstraint(fields=["ficha", "numero"], name="version_unica_por_ficha")]

    def __str__(self):
        return f"{self.ficha.codigo} v{self.numero}"
