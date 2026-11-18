"""Reglas del contrato de fichas aplicadas a una ficha de la base de datos.

Son las mismas reglas que ``knowledge-base/herramientas/validar_contrato.py``
aplica a los archivos Markdown. Una ficha que no las cumple no puede enviarse
a revisión.
"""

import re

from ..models import SECCIONES, TITULOS_SECCION, Ficha

RE_CODIGO = re.compile(r"^[A-Z]{3}_([A-Z]{3}_)?[A-Z]\d{2}$")


def errores_de_ficha(ficha: Ficha) -> dict[str, str]:
    errores: dict[str, str] = {}
    if not RE_CODIGO.match(ficha.codigo or ""):
        errores["codigo"] = "El código debe tener la forma PREFIJO_X00 (p. ej. BAC_P02)."
    else:
        prefijo = ficha.codigo[:3]
        permitidos = ficha.proceso.prefijos or []
        if permitidos and prefijo not in permitidos:
            errores["codigo"] = f"El prefijo {prefijo} no pertenece al proceso {ficha.proceso.nombre}."
    if not (ficha.titulo or "").strip():
        errores["titulo"] = "El título es obligatorio."
    if not (ficha.fuente or "").strip():
        errores["fuente"] = "Indique la norma o documento que respalda la ficha."
    if ficha.vigencia is None and (ficha.vigencia_texto or "").strip().lower() not in ("no indicada", ""):
        errores["vigencia"] = "Use una fecha AAAA-MM-DD o «no indicada»."
    for seccion in SECCIONES:
        if not (getattr(ficha, seccion) or "").strip():
            errores[seccion] = f"La sección «{TITULOS_SECCION[seccion]}» no puede quedar vacía; use «No indicado»."
    return errores
