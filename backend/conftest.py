import uuid
from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.conocimiento.models import EjemploIntent, Facultad, Ficha, Intent, Proceso, Programa
from apps.conocimiento.services.publicacion import publicar
from apps.cuentas.models import Usuario
from apps.nlu.services import embeber_ejemplos


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def programa(db):
    facultad = Facultad.objects.create(nombre="Facultad de Ingeniería")
    return Programa.objects.create(facultad=facultad, nombre="Ingeniería de Sistemas e Informática")


@pytest.fixture
def proceso(programa):
    return Proceso.objects.create(
        programa=programa, clave="bachiller_conv_ppp", nombre="Grado de Bachiller", prefijos=["BAC", "CPP"], orden=1
    )


def crear_ficha(proceso, codigo="BAC_P02", fase=2, **campos):
    valores = {
        "titulo": "Foto digital y entrega de fotos físicas",
        "fuente": "Flujograma oficial de Bachiller",
        "vigencia": date(2025, 11, 11),
        "estado_dato": Ficha.EstadoDato.CONFIRMADO,
        "requisitos": "- 2 fotos físicas de 4 cm x 5 cm.",
        "pasos": "1. Subir la foto digital.\n2. Entregar las fotos en la oficina.",
        "pago": "S/ 5.00 en caja.",
        "plazo": "Máximo 20 días hábiles.",
        "enviar_a": "secretaria.sistemas.hco@udh.edu.pe",
        "siguiente_fase": "BAC_P03",
    }
    valores.update(campos)
    return Ficha.objects.create(proceso=proceso, codigo=codigo, fase=fase, **valores)


@pytest.fixture
def ficha_publicada(proceso):
    ficha = crear_ficha(proceso)
    publicar(ficha, None, "prueba", indexar_en_segundo_plano=False)
    ficha.refresh_from_db()
    return ficha


@pytest.fixture
def intent_fotos(proceso, ficha_publicada):
    intent = Intent.objects.create(proceso=proceso, nombre="BAC_fotos", descripcion="Fotos para el bachiller")
    intent.fichas.add(ficha_publicada)
    ejemplos = [
        "cuántas fotos necesito para el bachiller",
        "de qué tamaño son las fotos del bachiller",
        "fotos para el grado de bachiller",
        "dónde entrego las fotos del bachiller",
        "medida de las fotos para bachiller",
    ]
    EjemploIntent.objects.bulk_create(EjemploIntent(intent=intent, texto=t) for t in ejemplos)
    embeber_ejemplos()
    return intent


def _usuario(rol, nombre=None):
    return Usuario.objects.create_user(username=nombre or rol, password="Clave-Segura-2026", rol=rol)


@pytest.fixture
def editor(db):
    return _usuario("editor")


@pytest.fixture
def revisor(db):
    return _usuario("revisor")


@pytest.fixture
def lector(db):
    return _usuario("lector")


@pytest.fixture
def superadmin(db):
    return _usuario("superadmin")


@pytest.fixture
def como():
    """Cliente autenticado con el usuario dado: ``como(editor)``."""

    def _cliente(usuario):
        cliente = APIClient()
        cliente.force_authenticate(usuario)
        return cliente

    return _cliente


@pytest.fixture
def sesion():
    return uuid.uuid4()
