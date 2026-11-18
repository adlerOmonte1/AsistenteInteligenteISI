"""Registro anonimizado de consultas, métricas del panel y purga por retención."""

import re
from datetime import timedelta

from django.conf import settings
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Consulta

# Orden importante: primero lo más específico.
_PATRONES_PERSONALES = [
    (re.compile(r"[a-z0-9._%+-]+@(?!udh\.edu\.pe\b)[a-z0-9.-]+\.[a-z]{2,}", re.I), "[correo]"),
    (re.compile(r"\b(?:\+?51\s?)?9\d{2}[\s-]?\d{3}[\s-]?\d{3}\b"), "[telefono]"),
    (re.compile(r"\b20\d{8}\b"), "[codigo]"),
    (re.compile(r"\b\d{8}\b"), "[dni]"),
    (re.compile(r"\b\d{9,12}\b"), "[numero]"),
]


def enmascarar(texto: str) -> str:
    """Reemplaza datos personales que el estudiante haya escrito por marcadores."""
    for patron, marcador in _PATRONES_PERSONALES:
        texto = patron.sub(marcador, texto)
    return texto


def registrar(**datos) -> Consulta:
    datos["pregunta"] = enmascarar(datos["pregunta"])[:1000]
    return Consulta.objects.create(**datos)


def purgar_antiguas() -> int:
    meses = settings.ASISTENTE["MESES_RETENCION_CONSULTAS"]
    limite = timezone.now() - timedelta(days=30 * meses)
    borradas, _ = Consulta.objects.filter(creada__lt=limite).delete()
    return borradas


def _porcentaje(parte: int, total: int) -> float:
    return round(100.0 * parte / total, 1) if total else 0.0


def resumen(desde=None, hasta=None) -> dict:
    hasta = hasta or timezone.now()
    desde = desde or hasta - timedelta(days=30)
    qs = Consulta.objects.filter(creada__gte=desde, creada__lte=hasta)

    totales = qs.aggregate(
        total=Count("id"),
        derivadas=Count("id", filter=Q(derivada=True)),
        utiles=Count("id", filter=Q(util=True)),
        no_utiles=Count("id", filter=Q(util=False)),
        fallas_validacion=Count("id", filter=Q(validacion_fallida=True)),
        costo=Sum("costo_usd"),
        latencia=Avg("latencia_ms"),
        sesiones=Count("sesion", distinct=True),
    )
    total = totales["total"]
    calificadas = totales["utiles"] + totales["no_utiles"]
    por_via = {v: 0 for v in Consulta.Via.values}
    for fila in qs.values("via").annotate(n=Count("id")):
        por_via[fila["via"]] = fila["n"]
    por_dia = [
        {"fecha": fila["dia"].isoformat(), "consultas": fila["n"]}
        for fila in qs.annotate(dia=TruncDate("creada")).values("dia").annotate(n=Count("id")).order_by("dia")
    ]
    top_intents = list(qs.exclude(intent="").values("intent").annotate(n=Count("id")).order_by("-n")[:10])
    por_proceso = list(qs.exclude(proceso=None).values("proceso__nombre").annotate(n=Count("id")).order_by("-n"))

    inicio_mes = timezone.localtime().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    costo_mes = Consulta.objects.filter(creada__gte=inicio_mes).aggregate(c=Sum("costo_usd"))["c"] or 0

    return {
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "total": total,
        "sesiones": totales["sesiones"],
        "por_via": por_via,
        "porcentaje_por_via": {v: _porcentaje(n, total) for v, n in por_via.items()},
        "porcentaje_derivadas": _porcentaje(totales["derivadas"], total),
        "porcentaje_utiles": _porcentaje(totales["utiles"], calificadas),
        "calificadas": calificadas,
        "fallas_validacion": totales["fallas_validacion"],
        "costo_periodo_usd": float(totales["costo"] or 0),
        "costo_mes_usd": float(costo_mes),
        "latencia_promedio_ms": round(totales["latencia"] or 0),
        "por_dia": por_dia,
        "top_intents": top_intents,
        "por_proceso": [{"proceso": f["proceso__nombre"], "consultas": f["n"]} for f in por_proceso],
    }
