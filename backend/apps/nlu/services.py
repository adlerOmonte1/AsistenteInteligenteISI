"""Comprensión de la pregunta: normalización, entidades y clasificación de intents.

El clasificador es de k vecinos sobre los embeddings de los ejemplos de cada
intent (ADR-0003). No se entrena: agregar ejemplos desde el panel basta para
que el cambio tenga efecto.

Confianza = (similitud del mejor vecino del intent ganador) × (proporción del
voto que obtiene ese intent entre los k vecinos). Una pregunta que se parece
mucho a un solo intent da un valor alto; una que se reparte entre dos intents
baja a la zona de desambiguación; una que no se parece a nada queda baja y va
a la vía RAG.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field

from django.conf import settings
from django.db.models import Max, Q
from pgvector.django import CosineDistance

from apps.conocimiento.models import EjemploIntent, Intent
from apps.generacion.proveedores.base import estimar_tokens
from apps.generacion.proveedores.fabrica import embeber_con_respaldo, obtener_embeddings
from comun.texto import normalizar

# Abreviaturas y errores frecuentes. Se aplican antes de clasificar.
SINONIMOS = {
    r"\bppp\b": "practicas preprofesionales",
    r"\bpre ?profesionales\b": "preprofesionales",
    r"\btsp\b": "trabajo de suficiencia profesional",
    r"\bsuficiencia\b": "suficiencia profesional",
    r"\bbachi\b": "bachiller",
    r"\bkiero\b": "quiero",
    r"\bq\b": "que",
    r"\bxq\b": "porque",
    r"\bpq\b": "porque",
    r"\bnesesito\b": "necesito",
    r"\bcuanto cuesta\b": "costo pago cuanto cuesta",
    r"\bcuanto pago\b": "costo pago cuanto",
    r"\bcorreo\b": "correo enviar",
    r"\bisi\b": "ingenieria de sistemas e informatica",
}
_SINONIMOS_COMPILADOS = [(re.compile(p), r) for p, r in SINONIMOS.items()]

ORDINALES = {
    "primer": 1,
    "primera": 1,
    "primero": 1,
    "segunda": 2,
    "segundo": 2,
    "tercera": 3,
    "tercer": 3,
    "tercero": 3,
    "cuarta": 4,
    "cuarto": 4,
    "quinta": 5,
    "quinto": 5,
    "sexta": 6,
    "sexto": 6,
    "septima": 7,
    "septimo": 7,
    "octava": 8,
    "octavo": 8,
    "novena": 9,
    "noveno": 9,
}
RE_FASE = re.compile(r"\b(fase|paso|etapa)\s*(?:n(?:ro|umero)?\.?\s*)?(\d{1,2})\b")
RE_FASE_ORDINAL = re.compile(r"\b(" + "|".join(ORDINALES) + r")\s+(fase|paso|etapa)\b")
RE_NUMERO_SOLO = re.compile(r"^\s*(?:la |el )?(\d{1,2})\s*$")


@dataclass
class Prediccion:
    intent: str | None
    confianza: float
    alternativas: list[tuple[str, float]] = field(default_factory=list)
    entidades: dict = field(default_factory=dict)
    texto_normalizado: str = ""
    vector: list[float] | None = None
    proveedor_vector: str = ""
    tokens_embedding: int = 0


def normalizar_consulta(texto: str) -> str:
    plano = normalizar(texto)
    for patron, reemplazo in _SINONIMOS_COMPILADOS:
        plano = patron.sub(reemplazo, plano)
    return plano


def extraer_entidades(texto_normalizado: str) -> dict:
    entidades: dict = {}
    m = RE_FASE.search(texto_normalizado)
    if m:
        entidades["fase"] = int(m.group(2))
    else:
        m = RE_FASE_ORDINAL.search(texto_normalizado)
        if m:
            entidades["fase"] = ORDINALES[m.group(1)]
        else:
            m = RE_NUMERO_SOLO.match(texto_normalizado)
            if m:
                entidades["fase"] = int(m.group(1))
    if re.search(r"\binterno\b", texto_normalizado):
        entidades["tipo_traslado"] = "interno"
    elif re.search(r"\bexterno\b|otra universidad", texto_normalizado):
        entidades["tipo_traslado"] = "externo"
    m = re.search(r"\banexo\s*0?(\d{1,2})\b", texto_normalizado)
    if m:
        entidades["anexo"] = m.group(1).zfill(2)
    return entidades


_cache_exactos: dict = {"firma": None, "mapa": {}}


def _coincidencia_exacta(texto_normalizado: str) -> str | None:
    """Una pregunta idéntica a un ejemplo no necesita votación."""
    activos = EjemploIntent.objects.filter(intent__activo=True)
    firma = (activos.count(), activos.aggregate(m=Max("id"))["m"], Intent.objects.aggregate(m=Max("actualizado"))["m"])
    if firma != _cache_exactos["firma"]:
        _cache_exactos["mapa"] = {
            normalizar_consulta(texto): nombre for texto, nombre in activos.values_list("texto", "intent__nombre")
        }
        _cache_exactos["firma"] = firma
    return _cache_exactos["mapa"].get(texto_normalizado)


def clasificar(texto: str) -> Prediccion:
    texto_normalizado = normalizar_consulta(texto)
    entidades = extraer_entidades(texto_normalizado)
    vectores, proveedor = embeber_con_respaldo([texto_normalizado], tipo="consulta")
    vector = vectores[0]
    prediccion = Prediccion(
        intent=None,
        confianza=0.0,
        entidades=entidades,
        texto_normalizado=texto_normalizado,
        vector=vector,
        proveedor_vector=proveedor,
        tokens_embedding=estimar_tokens(texto_normalizado),
    )

    exacto = _coincidencia_exacta(texto_normalizado)
    if exacto:
        prediccion.intent, prediccion.confianza = exacto, 1.0
        prediccion.alternativas = [(exacto, 1.0)]
        return prediccion

    # Si el proveedor principal falló, los ejemplos están en otro espacio vectorial.
    if proveedor != obtener_embeddings().nombre:
        return prediccion

    k = settings.ASISTENTE["VECINOS_INTENT"]
    vecinos = (
        EjemploIntent.objects.filter(intent__activo=True, embedding__isnull=False, proveedor_embedding=proveedor)
        .annotate(distancia=CosineDistance("embedding", vector))
        .select_related("intent")
        .order_by("distancia")[:k]
    )
    votos: dict[str, float] = defaultdict(float)
    mejor: dict[str, float] = {}
    for v in vecinos:
        similitud = max(0.0, 1.0 - float(v.distancia))
        votos[v.intent.nombre] += similitud
        mejor[v.intent.nombre] = max(mejor.get(v.intent.nombre, 0.0), similitud)
    total = sum(votos.values())
    if not total:
        return prediccion

    ranking = sorted(((n, mejor[n] * votos[n] / total) for n in votos), key=lambda x: x[1], reverse=True)
    prediccion.intent, prediccion.confianza = ranking[0]
    prediccion.alternativas = ranking[:3]
    return prediccion


LOTE_EJEMPLOS = 50


def embeber_ejemplos(intent: Intent | None = None, todos: bool = False, reintentos: int = 0, al_avanzar=None) -> int:
    """Calcula los embeddings que falten, los de un intent o todos (tras cambiar de proveedor).

    Se guarda cada lote apenas se calcula: si la cuota del proveedor se agota,
    lo ya calculado queda y la siguiente ejecución solo procesa lo que falta.
    """
    # Sin respaldo: los ejemplos deben quedar en el espacio vectorial del proveedor activo.
    proveedor = obtener_embeddings()
    qs = EjemploIntent.objects.all()
    if intent is not None:
        qs = qs.filter(intent=intent)
    elif todos:
        qs = qs.filter(Q(embedding__isnull=True) | ~Q(proveedor_embedding=proveedor.nombre))
    else:
        qs = qs.filter(embedding__isnull=True)
    ejemplos = list(qs.order_by("id"))
    for i in range(0, len(ejemplos), LOTE_EJEMPLOS):
        lote = ejemplos[i : i + LOTE_EJEMPLOS]
        vectores = proveedor.embeber(
            [normalizar_consulta(e.texto) for e in lote], tipo="consulta", reintentos=reintentos
        )
        for ejemplo, vector in zip(lote, vectores, strict=True):
            ejemplo.embedding = vector
            ejemplo.proveedor_embedding = proveedor.nombre
        EjemploIntent.objects.bulk_update(lote, ["embedding", "proveedor_embedding"])
        if al_avanzar:
            al_avanzar(i + len(lote), len(ejemplos))
    return len(ejemplos)
