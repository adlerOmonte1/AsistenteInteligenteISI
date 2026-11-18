"""Propuesta de fichas a partir de un documento subido (.docx o .pdf).

El LLM lee el documento y propone fichas con las seis secciones del contrato.
Las fichas quedan en borrador y pasan por la revisión de siempre: el sistema
nunca publica lo que propone el modelo.
"""

import json
import logging
import re
from pathlib import Path

from django.conf import settings

from apps.generacion.proveedores.base import ErrorProveedor
from apps.generacion.proveedores.fabrica import obtener_llm

from ..models import SECCIONES, CargaDocumento, Ficha

logger = logging.getLogger(__name__)
MAX_CARACTERES = 30_000
FIRMAS = {".pdf": b"%PDF", ".docx": b"PK\x03\x04"}

SISTEMA = (
    "Usted convierte normativa universitaria en fichas de conocimiento. Devuelva SOLO un arreglo JSON. "
    "Cada elemento describe una fase o etapa del trámite con las claves: fase (entero), titulo, fuente, "
    "requisitos, pasos, pago, plazo, enviar_a, siguiente_fase. Use texto Markdown en las secciones. "
    "Copie los datos tal como aparecen; si un dato no aparece escriba «No indicado». No invente nada."
)


def extension_valida(nombre: str, cabecera: bytes) -> bool:
    """Comprueba la extensión y la firma real del archivo (magic bytes)."""
    extension = Path(nombre).suffix.lower()
    firma = FIRMAS.get(extension)
    return firma is not None and cabecera.startswith(firma)


def extraer_texto(ruta: Path) -> str:
    if ruta.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        return "\n".join(pagina.extract_text() or "" for pagina in PdfReader(str(ruta)).pages)
    from docx import Document

    # Las tablas de los reglamentos contienen montos y plazos: se incluyen.
    documento = Document(str(ruta))
    partes = [p.text for p in documento.paragraphs]
    for tabla in documento.tables:
        for fila in tabla.rows:
            partes.append(" | ".join(celda.text.strip() for celda in fila.cells))
    return "\n".join(partes)


def _json_de_respuesta(texto: str) -> list[dict]:
    inicio, fin = texto.find("["), texto.rfind("]")
    if inicio == -1 or fin == -1:
        raise ValueError("el modelo no devolvió un arreglo JSON")
    datos = json.loads(texto[inicio : fin + 1])
    return [d for d in datos if isinstance(d, dict)]


def _codigo_libre(carga: CargaDocumento, n: int) -> str:
    prefijo = (carga.proceso.prefijos or ["DOC"])[0]
    base = f"{prefijo}_B{n:02d}"
    sufijo = n
    while Ficha.objects.filter(proceso=carga.proceso, codigo=base).exists():
        sufijo += 1
        base = f"{prefijo}_B{sufijo:02d}"
    return base


def procesar(carga_id: int) -> str:
    carga = CargaDocumento.objects.select_related("proceso").get(pk=carga_id)
    try:
        texto = extraer_texto(Path(carga.archivo.path))[:MAX_CARACTERES]
        if not texto.strip():
            raise ValueError("el documento no tiene texto extraíble (¿es un escaneo?)")

        if settings.LLM["PROVEEDOR"] == "local":
            propuestas = [
                {
                    "fase": 0,
                    "titulo": f"Contenido de {carga.nombre_original}",
                    "fuente": carga.nombre_original,
                    "pasos": texto[:4000],
                }
            ]
        else:
            resultado = obtener_llm().generar(SISTEMA, f"DOCUMENTO:\n{texto}", max_tokens=4000)
            propuestas = _json_de_respuesta(resultado.texto)

        creadas = []
        for n, p in enumerate(propuestas, start=1):
            ficha = Ficha(
                proceso=carga.proceso,
                codigo=_codigo_libre(carga, n),
                fase=int(p.get("fase") or 0) if str(p.get("fase") or "0").isdigit() else 0,
                titulo=str(p.get("titulo") or f"Fase propuesta {n}")[:300],
                fuente=str(p.get("fuente") or carga.nombre_original),
                vigencia_texto="no indicada",
                estado_dato=Ficha.EstadoDato.PENDIENTE,
                actualizada_por=carga.creada_por,
            )
            for seccion in SECCIONES:
                setattr(ficha, seccion, str(p.get(seccion) or "No indicado"))
            ficha.save()
            creadas.append(ficha)
        carga.fichas_propuestas.set(creadas)
        carga.estado = CargaDocumento.Estado.COMPLETADA
        carga.mensaje = f"Se propusieron {len(creadas)} fichas en borrador. Revíselas antes de enviarlas a revisión."
    except (ErrorProveedor, ValueError, json.JSONDecodeError) as exc:
        carga.estado = CargaDocumento.Estado.ERROR
        carga.mensaje = re.sub(r"\s+", " ", str(exc))[:500]
        logger.warning("Carga %s fallida: %s", carga_id, exc)
    carga.save()
    return carga.estado
