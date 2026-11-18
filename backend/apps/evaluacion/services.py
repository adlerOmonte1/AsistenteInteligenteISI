"""Ejecución del golden set y cálculo de métricas frente a las metas del sistema.

Metas (docs/00-proyecto/bases_del_sistema.md): intent ≥ 90 %, ficha ≥ 90 %,
respuesta clave ≥ 95 %, datos inventados = 0.
"""

import uuid

from django.utils import timezone

from apps.dialogo.orquestador import INTENT_DERIVAR, Orquestador
from comun.texto import normalizar, tokenizar

from .models import CasoEvaluacion, Evaluacion, ResultadoCaso

METAS = {"exactitud_intent": 90.0, "exactitud_ficha": 90.0, "clave_contenida": 95.0, "datos_inventados": 0}
COBERTURA_CLAVE = 0.7


def clave_contenida(respuesta: str, clave: str) -> bool:
    """La clave está contenida si aparece literal o si aparece el 70 % de sus palabras."""
    r, c = normalizar(respuesta), normalizar(clave)
    if not c:
        return True
    if c in r:
        return True
    palabras = set(tokenizar(clave))
    if not palabras:
        return False
    return len(palabras & set(tokenizar(respuesta))) / len(palabras) >= COBERTURA_CLAVE


def _porcentaje(aciertos: list[bool]) -> float | None:
    return round(100.0 * sum(aciertos) / len(aciertos), 1) if aciertos else None


def calcular_metricas(resultados: list[ResultadoCaso]) -> dict:
    intents = [r.acierto_intent for r in resultados if r.acierto_intent is not None]
    fichas = [r.acierto_ficha for r in resultados if r.acierto_ficha is not None]
    claves = [r.clave_contenida for r in resultados if r.clave_contenida is not None]
    metricas = {
        "casos": len(resultados),
        "exactitud_intent": _porcentaje(intents),
        "exactitud_ficha": _porcentaje(fichas),
        "clave_contenida": _porcentaje(claves),
        "datos_inventados": sum(r.dato_inventado for r in resultados),
        "por_via": {},
    }
    for r in resultados:
        metricas["por_via"][r.via] = metricas["por_via"].get(r.via, 0) + 1
    metricas["cumple"] = {
        "exactitud_intent": (metricas["exactitud_intent"] or 0) >= METAS["exactitud_intent"],
        "exactitud_ficha": (metricas["exactitud_ficha"] or 0) >= METAS["exactitud_ficha"],
        "clave_contenida": (metricas["clave_contenida"] or 0) >= METAS["clave_contenida"],
        "datos_inventados": metricas["datos_inventados"] == METAS["datos_inventados"],
    }
    metricas["cumple_todas"] = all(metricas["cumple"].values())
    return metricas


def evaluar_caso(evaluacion: Evaluacion, caso: CasoEvaluacion) -> ResultadoCaso:
    r = Orquestador(registrar=False).responder(uuid.uuid4(), caso.pregunta)
    codigos = [f["codigo"] for f in r.fichas]
    esperado = caso.intent_esperado.strip()
    acierto_intent = None
    if esperado:
        # Derivar es correcto cuando se espera derivar, aunque el intent clasificado sea otro.
        acierto_intent = r.intent == esperado or (esperado == INTENT_DERIVAR and r.derivada)
    return ResultadoCaso.objects.create(
        evaluacion=evaluacion,
        caso=caso,
        intent_obtenido=r.intent,
        confianza=r.confianza,
        fichas_obtenidas=codigos,
        via=r.via.value,
        respuesta=r.texto,
        acierto_intent=acierto_intent,
        # "A|B" en el golden set: vale cualquiera de las fichas indicadas.
        acierto_ficha=any(f in codigos for f in caso.ficha_esperada.split("|")) if caso.ficha_esperada else None,
        clave_contenida=clave_contenida(r.texto, caso.respuesta_clave) if caso.respuesta_clave else None,
        dato_inventado=r.validacion_fallida,
    )


def ejecutar(evaluacion_id: int) -> Evaluacion:
    evaluacion = Evaluacion.objects.get(pk=evaluacion_id)
    evaluacion.estado = Evaluacion.Estado.EJECUTANDO
    evaluacion.save(update_fields=["estado"])
    try:
        casos = CasoEvaluacion.objects.filter(activo=True)
        if evaluacion.proceso_id:
            casos = casos.filter(proceso_id=evaluacion.proceso_id)
        if evaluacion.limite_casos:
            casos = casos.order_by("?")[: evaluacion.limite_casos]
        resultados = [evaluar_caso(evaluacion, caso) for caso in casos]
        evaluacion.metricas = calcular_metricas(resultados)
        evaluacion.estado = Evaluacion.Estado.COMPLETADA
    except Exception as exc:  # noqa: BLE001 - se informa en el panel
        evaluacion.estado = Evaluacion.Estado.ERROR
        evaluacion.mensaje = str(exc)[:1000]
    evaluacion.finalizada = timezone.now()
    evaluacion.save()
    return evaluacion
