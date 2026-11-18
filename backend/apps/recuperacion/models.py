from django.db import models
from pgvector.django import HnswIndex, VectorField


class SeccionIndexada(models.Model):
    """Una sección de una versión publicada de ficha, lista para la búsqueda.

    Cada sección hereda los metadatos de su ficha (proceso, fase) para poder
    filtrar. Al publicar una versión nueva, las secciones anteriores pasan a
    ``vigente=False``; no se borran para poder auditar qué se respondía antes.
    """

    version = models.ForeignKey("conocimiento.VersionFicha", on_delete=models.CASCADE, related_name="secciones")
    ficha = models.ForeignKey("conocimiento.Ficha", on_delete=models.CASCADE, related_name="secciones_indexadas")
    proceso = models.ForeignKey("conocimiento.Proceso", on_delete=models.CASCADE, related_name="+")
    seccion = models.CharField(max_length=30)
    fase = models.PositiveSmallIntegerField(default=0)
    texto = models.TextField()
    vigente = models.BooleanField(default=True, db_index=True)
    proveedor_embedding = models.CharField(max_length=30, blank=True)
    embedding = VectorField(dimensions=768, null=True, blank=True)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "sección indexada"
        verbose_name_plural = "secciones indexadas"
        indexes = [
            models.Index(fields=["proceso", "vigente"]),
            HnswIndex(
                name="seccion_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.ficha.codigo}/{self.seccion}"
