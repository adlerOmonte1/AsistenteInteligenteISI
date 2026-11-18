"""Textos que arma la vía determinista a partir de una versión publicada de ficha."""

from apps.conocimiento.models import SECCIONES, TITULOS_SECCION, Ficha

AVISO_PENDIENTE = (
    "Parte de esta información aún no ha sido confirmada por la Coordinación del programa. "
    "Le recomendamos verificarla antes de iniciar el trámite."
)
NO_INDICADO = "No se indica en las fuentes oficiales del programa; consúltelo con la Coordinación."
NO_ENTENDIDO = (
    "No encontré información sobre eso en la normativa del programa. ¿Podría reformular su consulta "
    "indicando el trámite (prácticas, bachiller, título o traslado) y la fase?"
)
PREGUNTA_DESAMBIGUACION = "¿Su consulta se refiere a alguno de estos temas?"


def _es_no_indicado(valor: str) -> bool:
    return valor.strip().lower().startswith(("no indicado", "no indicada"))


def titulo_de_codigo(codigo: str, proceso_id: int | None = None) -> str | None:
    qs = Ficha.objects.filter(codigo=codigo.strip(), version_publicada__isnull=False)
    if proceso_id:
        qs = qs.filter(proceso_id=proceso_id)
    ficha = qs.first()
    return ficha.version_publicada.contenido.get("titulo") if ficha else None


def componer(contenido: dict, secciones: list[str] | None = None, proceso_id: int | None = None) -> str:
    elegidas = [s for s in (secciones or SECCIONES) if s in SECCIONES] or list(SECCIONES)
    partes = [f"**{contenido['titulo']}** ({contenido['codigo']})"]
    if contenido.get("estado_dato") == Ficha.EstadoDato.PENDIENTE:
        partes.append(f"_{AVISO_PENDIENTE}_")

    for seccion in elegidas:
        valor = (contenido.get(seccion) or "").strip()
        if not valor:
            continue
        if seccion == "siguiente_fase":
            titulo = titulo_de_codigo(valor, proceso_id)
            valor = f"{titulo} ({valor})" if titulo else valor
        elif _es_no_indicado(valor):
            valor = NO_INDICADO
        partes.append(f"**{TITULOS_SECCION[seccion]}:**\n{valor}")

    # En una respuesta puntual (solo «Pago», por ejemplo) la información adicional sobra.
    if not secciones and (contenido.get("informacion_adicional") or "").strip():
        partes.append(f"**{TITULOS_SECCION['informacion_adicional']}:**\n{contenido['informacion_adicional'].strip()}")

    partes.append(f"_Fuente: {contenido.get('fuente', 'no indicada')}._")
    return "\n\n".join(partes)


def texto_completo(contenido: dict) -> str:
    """Todo el texto de una versión, para validar los datos de una respuesta RAG."""
    campos = ["titulo", "fuente", *SECCIONES, "informacion_adicional"]
    return "\n".join(str(contenido.get(c, "")) for c in campos)
