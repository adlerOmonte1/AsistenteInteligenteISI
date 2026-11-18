"""Indexación de fichas publicadas y búsqueda híbrida (BM25 + embeddings).

La búsqueda combina dos listas con Reciprocal Rank Fusion: la de BM25 premia
coincidencias exactas («anexo 06», «S/ 5.00»), la de embeddings premia
paráfrasis («cuánto me cobran»). Solo se buscan secciones vigentes de fichas
publicadas y no reemplazadas.
"""

import logging
from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from pgvector.django import CosineDistance
from rank_bm25 import BM25Okapi

from apps.conocimiento.models import SECCIONES, TITULOS_SECCION, VersionFicha
from apps.generacion.proveedores.fabrica import embeber_con_respaldo, obtener_embeddings
from comun.texto import tokenizar

from .models import SeccionIndexada

logger = logging.getLogger(__name__)

SECCIONES_INDEXABLES = (*SECCIONES, "informacion_adicional")
CONSTANTE_RRF = 60
CANDIDATOS = 20


@dataclass(frozen=True)
class Resultado:
    seccion: SeccionIndexada
    puntaje: float
    similitud: float
    bm25: float


def texto_para_indice(contenido: dict, seccion: str) -> str:
    titulo = TITULOS_SECCION[seccion]
    return f"{contenido['titulo']} — {titulo}\n{contenido.get(seccion, '').strip()}"


@transaction.atomic
def indexar_version(version: VersionFicha, estricto: bool = False, reintentos: int = 0) -> int:
    """Indexa una versión publicada y retira del índice las anteriores de la misma ficha.

    Con ``estricto`` no se usa el respaldo local: si el proveedor falla, se lanza el
    error y la ficha conserva su índice anterior. Es el modo de ``manage.py reindexar``,
    que no debe dejar el índice con vectores de dos proveedores.
    """
    ficha = version.ficha
    SeccionIndexada.objects.filter(ficha=ficha, vigente=True).update(vigente=False)
    if ficha.reemplazada_por_id:
        return 0

    contenido = version.contenido
    secciones = [s for s in SECCIONES_INDEXABLES if (contenido.get(s) or "").strip()]
    textos = [texto_para_indice(contenido, s) for s in secciones]
    if not textos:
        return 0
    if estricto:
        proveedor_activo = obtener_embeddings()
        vectores = proveedor_activo.embeber(textos, tipo="documento", reintentos=reintentos)
        proveedor = proveedor_activo.nombre
    else:
        vectores, proveedor = embeber_con_respaldo(textos, tipo="documento")
    SeccionIndexada.objects.bulk_create(
        SeccionIndexada(
            version=version,
            ficha=ficha,
            proceso_id=ficha.proceso_id,
            seccion=seccion,
            fase=contenido.get("fase", 0),
            texto=texto,
            proveedor_embedding=proveedor,
            embedding=vector,
        )
        for seccion, texto, vector in zip(secciones, textos, vectores, strict=True)
    )
    return len(textos)


def reindexar_todo(solo_pendientes: bool = True, reintentos: int = 0, al_avanzar=None) -> int:
    """Reindexa las versiones publicadas con el proveedor activo.

    Con ``solo_pendientes`` se omiten las fichas cuyo índice vigente ya usa el
    proveedor activo, de modo que, si la cuota se agota a mitad de camino,
    volver a ejecutar continúa donde quedó. Cada ficha se guarda en su propia
    transacción.
    """
    nombre = obtener_embeddings().nombre
    versiones = [
        v
        for v in VersionFicha.objects.filter(ficha__version_publicada_id__isnull=False).select_related("ficha")
        if v.ficha.version_publicada_id == v.id
    ]
    total = 0
    for n, version in enumerate(versiones, start=1):
        vigentes = SeccionIndexada.objects.filter(ficha=version.ficha, vigente=True)
        if solo_pendientes and vigentes.exists() and not vigentes.exclude(proveedor_embedding=nombre).exists():
            continue
        total += indexar_version(version, estricto=True, reintentos=reintentos)
        if al_avanzar:
            al_avanzar(n, len(versiones))
    return total


def _rrf(posiciones: dict[int, int]) -> float:
    return sum(1.0 / (CONSTANTE_RRF + p) for p in posiciones.values())


def buscar(
    pregunta: str,
    vector: list[float] | None,
    proveedor_vector: str = "",
    procesos: list[int] | None = None,
    k: int | None = None,
) -> list[Resultado]:
    """Devuelve las ``k`` secciones más relevantes para la pregunta."""
    k = k or settings.ASISTENTE["SECCIONES_RAG"]
    base = SeccionIndexada.objects.filter(vigente=True).select_related("ficha", "version")
    if procesos:
        base = base.filter(proceso_id__in=procesos)

    candidatas = list(base)
    if not candidatas:
        return []

    rangos: dict[int, dict[str, int]] = {}
    similitudes: dict[int, float] = {}

    # Solo se compara contra vectores del mismo proveedor; mezclar espacios no tiene sentido.
    if vector is not None:
        cercanas = (
            base.filter(proveedor_embedding=proveedor_vector, embedding__isnull=False)
            .annotate(distancia=CosineDistance("embedding", vector))
            .order_by("distancia")[:CANDIDATOS]
        )
        for posicion, s in enumerate(cercanas, start=1):
            rangos.setdefault(s.id, {})["vector"] = posicion
            similitudes[s.id] = 1.0 - float(s.distancia)

    corpus = [tokenizar(s.texto) for s in candidatas]
    consulta = tokenizar(pregunta)
    puntajes_bm25: dict[int, float] = {}
    if consulta and any(corpus):
        bm25 = BM25Okapi(corpus)
        puntajes = bm25.get_scores(consulta)
        orden = sorted(range(len(candidatas)), key=lambda i: puntajes[i], reverse=True)[:CANDIDATOS]
        maximo = max(puntajes) or 1.0
        for posicion, i in enumerate(orden, start=1):
            if puntajes[i] <= 0:
                break
            sid = candidatas[i].id
            rangos.setdefault(sid, {})["bm25"] = posicion
            puntajes_bm25[sid] = float(puntajes[i] / maximo)

    por_id = {s.id: s for s in candidatas}
    resultados = [
        Resultado(
            seccion=por_id[sid],
            puntaje=_rrf(pos),
            similitud=similitudes.get(sid, 0.0),
            bm25=puntajes_bm25.get(sid, 0.0),
        )
        for sid, pos in rangos.items()
        if sid in por_id
    ]
    resultados.sort(key=lambda r: r.puntaje, reverse=True)
    return resultados[:k]


def es_relevante(resultado: Resultado) -> bool:
    """Una sección es relevante si se parece semánticamente o coincide bien por palabras."""
    minimo = settings.ASISTENTE["SIMILITUD_MINIMA_RAG"]
    return resultado.similitud >= minimo or resultado.bm25 >= 0.5


def proveedor_activo() -> str:
    return obtener_embeddings().nombre


__all__ = ["Resultado", "buscar", "es_relevante", "indexar_version", "reindexar_todo", "logger"]
