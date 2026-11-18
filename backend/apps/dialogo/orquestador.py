"""Orquestador del diálogo: de la pregunta del estudiante a una respuesta validada.

Flujo (docs/03-arquitectura/modulos.md, módulo Diálogo):

1. Clasificar la pregunta (NLU) o tomar el intent/ficha que eligió el estudiante.
2. Completar una entidad que se había pedido (p. ej. «la 3» tras «¿qué fase?»).
3. Elegir la vía con el router por confianza.
4. Responder: determinista, desambiguación, RAG o derivación.
5. Validar los datos críticos de la respuesta RAG contra las fichas citadas.
6. Registrar la consulta sin datos personales.

La respuesta se arma completa y se valida **antes** de enviarse; el streaming
del canal es solo de presentación (ADR-0006).
"""

import re
import time
import uuid
from dataclasses import dataclass, field

from django.db import transaction

from apps.analitica import services as analitica
from apps.conocimiento.models import Ficha, Intent
from apps.generacion import services as generacion
from apps.generacion.proveedores.base import ErrorProveedor, ResultadoLLM
from apps.generacion.proveedores.local import LLMExtractivo
from apps.nlu import services as nlu
from apps.recuperacion import services as recuperacion
from apps.sistema.models import Configuracion
from apps.validacion import services as validacion

from . import respuestas
from .models import Conversacion
from .router import Umbrales, Via, elegir_via

INTENT_DERIVAR = "GEN_derivar_humano"
RE_CODIGO = re.compile(r"\b[A-Z]{3}_[A-Z0-9_]*[A-Z]\d{2}\b")


@dataclass
class Respuesta:
    texto: str
    via: Via
    intent: str = ""
    confianza: float = 0.0
    fichas: list[dict] = field(default_factory=list)
    opciones: list[dict] = field(default_factory=list)
    derivada: bool = False
    motivo: str = ""
    validacion_fallida: bool = False
    no_respaldados: list[str] = field(default_factory=list)
    proceso_id: int | None = None
    tokens_entrada: int = 0
    tokens_salida: int = 0
    tokens_embedding: int = 0
    consulta_id: int | None = None
    traza: dict = field(default_factory=dict)


class Orquestador:
    def __init__(self, registrar: bool = True):
        self.registrar = registrar
        self.cfg = Configuracion.actual()
        self.umbrales = Umbrales.desde_configuracion(self.cfg)

    # ---------------------------------------------------------------- entrada
    def responder(
        self,
        sesion: uuid.UUID | str,
        mensaje: str,
        intent_elegido: str | None = None,
        ficha_elegida: str | None = None,
    ) -> Respuesta:
        inicio = time.monotonic()
        with transaction.atomic():
            conv, _ = Conversacion.objects.select_for_update().get_or_create(sesion=sesion)
            respuesta = self._resolver(conv, mensaje, intent_elegido, ficha_elegida)
            conv.mensajes += 1
            conv.save()

        if self.registrar:
            consulta = analitica.registrar(
                sesion=conv.sesion,
                proceso_id=respuesta.proceso_id,
                pregunta=mensaje,
                respuesta=respuesta.texto,
                intent=respuesta.intent,
                confianza=round(respuesta.confianza, 4),
                via=respuesta.via.value,
                fichas_citadas=[f["codigo"] for f in respuesta.fichas],
                derivada=respuesta.derivada,
                validacion_fallida=respuesta.validacion_fallida,
                datos_no_respaldados=respuesta.no_respaldados,
                motivo=respuesta.motivo,
                tokens_entrada=respuesta.tokens_entrada,
                tokens_salida=respuesta.tokens_salida,
                tokens_embedding=respuesta.tokens_embedding,
                costo_usd=generacion.costo_usd(
                    respuesta.tokens_entrada, respuesta.tokens_salida, respuesta.tokens_embedding
                ),
                latencia_ms=int((time.monotonic() - inicio) * 1000),
            )
            respuesta.consulta_id = consulta.id
        return respuesta

    # ------------------------------------------------------------- decisión
    def _resolver(self, conv, mensaje, intent_elegido, ficha_elegida) -> Respuesta:
        if ficha_elegida:
            ficha = self._ficha_publicada(codigo=ficha_elegida)
            if ficha:
                # Si la ficha se eligió para completar un intent («¿a qué correo…?»), se
                # responde solo la sección que ese intent pide.
                intent = Intent.objects.filter(nombre=intent_elegido, activo=True).first() if intent_elegido else None
                return self._responder_ficha(conv, ficha, intent=intent, confianza=1.0)

        if intent_elegido and Intent.objects.filter(nombre=intent_elegido, activo=True).exists():
            texto_normalizado = nlu.normalizar_consulta(mensaje)
            prediccion = nlu.Prediccion(
                intent=intent_elegido,
                confianza=1.0,
                entidades=nlu.extraer_entidades(texto_normalizado),
                texto_normalizado=texto_normalizado,
            )
        else:
            prediccion = nlu.clasificar(mensaje)

        # Respuesta a una aclaración pendiente: «la 3», «fase 2», «interno».
        if (
            conv.intent_pendiente
            and prediccion.entidades
            and (prediccion.confianza < self.umbrales.determinista or prediccion.intent == conv.intent_pendiente)
        ):
            prediccion.intent, prediccion.confianza = conv.intent_pendiente, 1.0
            prediccion.entidades = {**conv.entidades, **prediccion.entidades}

        traza = {
            "intent": prediccion.intent,
            "confianza": round(prediccion.confianza, 4),
            "alternativas": [(n, round(c, 4)) for n, c in prediccion.alternativas],
            "entidades": prediccion.entidades,
            "texto_normalizado": prediccion.texto_normalizado,
        }

        if prediccion.intent == INTENT_DERIVAR and prediccion.confianza >= self.umbrales.desambiguacion:
            respuesta = self._derivar(conv, motivo="solicitud_del_estudiante")
            respuesta.confianza = prediccion.confianza
        else:
            via = elegir_via(prediccion.confianza, conv.intentos_fallidos, self.umbrales)
            if via is Via.DERIVACION:
                respuesta = self._derivar(conv, motivo="intentos_fallidos")
            elif via is Via.DETERMINISTA:
                respuesta = self._determinista(conv, prediccion)
            elif via is Via.DESAMBIGUACION:
                respuesta = self._desambiguar(conv, prediccion)
            else:
                respuesta = self._rag(conv, mensaje, prediccion)

        respuesta.tokens_embedding += prediccion.tokens_embedding
        respuesta.traza = {**traza, **respuesta.traza, "via": respuesta.via.value}
        return respuesta

    # ------------------------------------------------------------------ vías
    def _determinista(self, conv, prediccion) -> Respuesta:
        intent = Intent.objects.select_related("proceso").get(nombre=prediccion.intent)
        conv.proceso_actual = intent.proceso
        fichas = list(
            intent.fichas.filter(version_publicada__isnull=False, reemplazada_por__isnull=True)
            .select_related("version_publicada")
            .order_by("fase", "codigo")
        )

        if not fichas:
            if intent.respuesta_fija:
                conv.intentos_fallidos = 0
                conv.intent_pendiente = ""
                return Respuesta(
                    texto=intent.respuesta_fija,
                    via=Via.DETERMINISTA,
                    intent=intent.nombre,
                    confianza=prediccion.confianza,
                    proceso_id=intent.proceso_id,
                    opciones=self._opciones_procesos() if intent.nombre == "GEN_saludo" else [],
                )
            # Intent sin ficha publicada: se intenta con la búsqueda restringida a su proceso.
            return self._rag(conv, prediccion.texto_normalizado, prediccion, procesos=[intent.proceso_id])

        ficha = self._elegir_ficha(fichas, prediccion.entidades)
        if ficha is None:
            conv.intent_pendiente = intent.nombre
            conv.entidades = prediccion.entidades
            pregunta = intent.si_falta_entidad or "¿Sobre qué fase o etapa del trámite desea información?"
            return Respuesta(
                texto=pregunta,
                via=Via.ACLARACION,
                intent=intent.nombre,
                confianza=prediccion.confianza,
                proceso_id=intent.proceso_id,
                opciones=[
                    {"etiqueta": f.version_publicada.contenido["titulo"], "ficha": f.codigo, "intent": intent.nombre}
                    for f in fichas[:8]
                ],
            )
        return self._responder_ficha(conv, ficha, intent=intent, confianza=prediccion.confianza)

    def _responder_ficha(self, conv, ficha: Ficha, intent: Intent | None, confianza: float) -> Respuesta:
        contenido = ficha.version_publicada.contenido
        conv.ficha_actual = ficha
        conv.proceso_actual_id = ficha.proceso_id
        conv.intent_pendiente = ""
        conv.entidades = {}
        conv.intentos_fallidos = 0
        texto = respuestas.componer(contenido, intent.secciones if intent else None, ficha.proceso_id)
        opciones = []
        siguiente = (contenido.get("siguiente_fase") or "").strip()
        if RE_CODIGO.fullmatch(siguiente):
            titulo = respuestas.titulo_de_codigo(siguiente, ficha.proceso_id)
            if titulo:
                opciones.append({"etiqueta": f"Siguiente: {titulo}", "ficha": siguiente})
        return Respuesta(
            texto=texto,
            via=Via.DETERMINISTA,
            intent=intent.nombre if intent else "",
            confianza=confianza,
            fichas=[{"codigo": ficha.codigo, "titulo": contenido["titulo"], "proceso": contenido.get("proceso")}],
            opciones=opciones,
            proceso_id=ficha.proceso_id,
        )

    def _desambiguar(self, conv, prediccion) -> Respuesta:
        nombres = [n for n, _ in prediccion.alternativas[:2]]
        intents = {i.nombre: i for i in Intent.objects.filter(nombre__in=nombres)}
        opciones = [{"etiqueta": (intents[n].descripcion or n)[:90], "intent": n} for n in nombres if n in intents]
        return Respuesta(
            texto=respuestas.PREGUNTA_DESAMBIGUACION,
            via=Via.DESAMBIGUACION,
            intent=prediccion.intent or "",
            confianza=prediccion.confianza,
            opciones=opciones,
        )

    def _rag(self, conv, mensaje, prediccion, procesos: list[int] | None = None) -> Respuesta:
        if procesos is None and prediccion.intent and prediccion.confianza >= 0.25:
            proceso_id = Intent.objects.filter(nombre=prediccion.intent).values_list("proceso_id", flat=True).first()
            procesos = [proceso_id] if proceso_id else None

        resultados = recuperacion.buscar(mensaje, prediccion.vector, prediccion.proveedor_vector, procesos)
        relevantes = [r for r in resultados if recuperacion.es_relevante(r)]
        if not relevantes and procesos:
            resultados = recuperacion.buscar(mensaje, prediccion.vector, prediccion.proveedor_vector, None)
            relevantes = [r for r in resultados if recuperacion.es_relevante(r)]

        if not relevantes:
            return self._fallo(conv, prediccion, motivo="sin_secciones_relevantes")

        fragmentos = [
            generacion.FragmentoContexto(
                codigo=r.seccion.ficha.codigo,
                titulo=r.seccion.version.contenido["titulo"],
                seccion=r.seccion.seccion.replace("_", " ").capitalize(),
                # La primera línea del texto indexado repite título y sección.
                texto=r.seccion.texto.split("\n", 1)[-1],
                pendiente=r.seccion.version.contenido.get("estado_dato") == Ficha.EstadoDato.PENDIENTE,
            )
            for r in relevantes
        ]

        disponible, motivo = generacion.llm_disponible()
        try:
            resultado = generacion.redactar(mensaje, fragmentos) if disponible else None
        except ErrorProveedor:
            resultado, motivo = None, "error_proveedor_llm"
        if resultado is None:
            # Sin LLM la respuesta se arma copiando las secciones: sigue sin inventar nada.
            usuario = generacion.armar_mensaje_usuario(mensaje, fragmentos)
            resultado = ResultadoLLM(LLMExtractivo().generar(generacion.SISTEMA, usuario, 600).texto)

        por_codigo = {r.seccion.ficha.codigo: r.seccion for r in relevantes}
        citados = [c for c in dict.fromkeys(RE_CODIGO.findall(resultado.texto)) if c in por_codigo]
        usados = citados or list(por_codigo)
        fuentes = [respuestas.texto_completo(por_codigo[c].version.contenido) for c in usados]
        verificacion = validacion.validar(resultado.texto, fuentes)

        if not verificacion.valida:
            derivacion = self._derivar(conv, motivo="validacion_fallida")
            derivacion.validacion_fallida = True
            derivacion.no_respaldados = verificacion.no_respaldados
            derivacion.tokens_entrada, derivacion.tokens_salida = resultado.tokens_entrada, resultado.tokens_salida
            return derivacion

        conv.intentos_fallidos = 0
        conv.intent_pendiente = ""
        primera = por_codigo[usados[0]]
        return Respuesta(
            texto=resultado.texto,
            via=Via.RAG,
            intent=prediccion.intent or "",
            confianza=prediccion.confianza,
            fichas=[
                {
                    "codigo": c,
                    "titulo": por_codigo[c].version.contenido["titulo"],
                    "proceso": por_codigo[c].version.contenido.get("proceso"),
                }
                for c in usados
            ],
            motivo=motivo,
            proceso_id=primera.proceso_id,
            tokens_entrada=resultado.tokens_entrada,
            tokens_salida=resultado.tokens_salida,
            traza={"secciones": [(r.seccion.ficha.codigo, r.seccion.seccion, round(r.puntaje, 4)) for r in relevantes]},
        )

    def _fallo(self, conv, prediccion, motivo: str) -> Respuesta:
        conv.intentos_fallidos += 1
        if conv.intentos_fallidos >= self.umbrales.intentos_antes_de_derivar:
            return self._derivar(conv, motivo=motivo)
        return Respuesta(
            texto=respuestas.NO_ENTENDIDO,
            via=Via.RAG,
            intent=prediccion.intent or "",
            confianza=prediccion.confianza,
            motivo=motivo,
            opciones=self._opciones_procesos(),
        )

    def _derivar(self, conv, motivo: str) -> Respuesta:
        conv.intentos_fallidos = 0
        conv.intent_pendiente = ""
        return Respuesta(
            texto=self.cfg.contacto_derivacion,
            via=Via.DERIVACION,
            intent=INTENT_DERIVAR,
            derivada=True,
            motivo=motivo,
            proceso_id=conv.proceso_actual_id,
        )

    # ------------------------------------------------------------- auxiliares
    @staticmethod
    def _elegir_ficha(fichas: list[Ficha], entidades: dict) -> Ficha | None:
        if len(fichas) == 1:
            return fichas[0]
        fase = entidades.get("fase")
        if fase is not None:
            coincidentes = [f for f in fichas if f.fase == fase]
            tipo = entidades.get("tipo_traslado")
            if tipo and len(coincidentes) > 1:
                marca = "_INT_" if tipo == "interno" else "_EXT_"
                coincidentes = [f for f in coincidentes if marca in f.codigo] or coincidentes
            if coincidentes:
                return coincidentes[0]
        return None

    @staticmethod
    def _ficha_publicada(codigo: str) -> Ficha | None:
        return (
            Ficha.objects.filter(codigo=codigo, version_publicada__isnull=False, reemplazada_por__isnull=True)
            .select_related("version_publicada")
            .first()
        )

    @staticmethod
    def _opciones_procesos() -> list[dict]:
        from apps.conocimiento.models import Proceso

        procesos = Proceso.objects.filter(activo=True, visible_en_portal=True).exclude(clave="general")
        return [{"etiqueta": p.nombre, "mensaje": f"Información sobre {p.nombre}"} for p in procesos[:6]]
