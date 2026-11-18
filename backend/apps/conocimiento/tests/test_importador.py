from pathlib import Path

import pytest
from django.conf import settings

from apps.conocimiento.models import Ficha, Intent
from apps.conocimiento.services.importador import (
    Importador,
    _lista_fichas,
    leer_ficha_markdown,
    secciones_de_intent,
)

FICHA_CONTRATO = """---
id: BAC_P02
proceso: bachiller_conv_ppp
fase: 2
titulo: Fotos
fuente: Flujograma
vigencia: no indicada
estado: confirmado        # confirmado | pendiente
---
## Requisitos
- 2 fotos

## Pasos
1. Subir

## Pago
No indicado

## Plazo
No indicado

## Enviar a
Oficina

## Resultado
Fotos registradas

## Siguiente fase
BAC_P03
"""

FICHA_CON_DATOS = """---
id: TRA_INT_F02
fase: 2
titulo: Constancia
fuente: doc.md
vigencia: pendiente
estado: pendiente
siguiente_fase: TRA_INT_F03
datos:
  requisitos:
  - Ninguno
  pagos: []
  plazo: Hasta 3 días hábiles.
---
# TRA_INT_F02

## Descripción
Texto libre.
"""


def test_lee_secciones_del_contrato_y_separa_las_adicionales():
    meta, secciones, adicional = leer_ficha_markdown(FICHA_CONTRATO)
    assert meta["estado"] == "confirmado"
    assert secciones["siguiente_fase"] == "BAC_P03"
    assert "Resultado" in adicional


def test_usa_el_bloque_datos_cuando_faltan_secciones():
    _, secciones, adicional = leer_ficha_markdown(FICHA_CON_DATOS)
    assert secciones["requisitos"] == "- Ninguno"
    assert secciones["plazo"] == "Hasta 3 días hábiles."
    assert secciones["siguiente_fase"] == "TRA_INT_F03"
    assert "Texto libre" in adicional


def test_resuelve_ficha_relacionada_en_sus_variantes():
    codigos = ["TSP_F01", "TSP_F02", "BAC_P01"]
    assert _lista_fichas("BAC_P01", codigos) == ["BAC_P01"]
    assert _lista_fichas("[TSP_F01, TSP_F02]", codigos) == ["TSP_F01", "TSP_F02"]
    assert _lista_fichas("TSP_F0*", codigos) == ["TSP_F01", "TSP_F02"]
    assert _lista_fichas(None, codigos) == []


@pytest.mark.parametrize(
    ("nombre", "secciones"),
    [("CPP_costo", ["pago"]), ("PPP_correo_etapa", ["enviar_a"]), ("BAC_info_general", []), ("TRA_plazo", ["plazo"])],
)
def test_infiere_secciones_por_nombre_de_intent(nombre, secciones):
    assert secciones_de_intent(nombre) == secciones


@pytest.mark.django_db
def test_importa_la_base_de_conocimiento_del_repositorio():
    base = Path(settings.ASISTENTE["CARPETA_CONOCIMIENTO"]).parent
    reporte = Importador(base, solo=["bachiller_conv_ppp", "general"]).ejecutar()
    assert reporte.errores == 0
    assert Ficha.objects.filter(proceso__clave="bachiller_conv_ppp", version_publicada__isnull=False).count() == 11
    assert Intent.objects.get(nombre="GEN_saludo").proceso.clave == "general"
