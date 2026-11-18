import pytest
from rest_framework.exceptions import ValidationError

from apps.conocimiento.models import Ficha
from apps.conocimiento.services import publicacion
from apps.recuperacion.models import SeccionIndexada
from comun.excepciones import ErrorDeNegocio
from conftest import crear_ficha

pytestmark = pytest.mark.django_db


def test_editar_una_ficha_publicada_no_cambia_lo_que_responde_el_asistente(ficha_publicada, editor):
    publicado = ficha_publicada.version_publicada.contenido["pago"]
    ficha_publicada.pago = "S/ 99.00"
    publicacion.marcar_editada(ficha_publicada, editor)
    ficha_publicada.save()
    ficha_publicada.refresh_from_db()
    assert ficha_publicada.estado_revision == Ficha.EstadoRevision.BORRADOR
    assert ficha_publicada.version_publicada.contenido["pago"] == publicado


def test_ciclo_completo_de_revision(ficha_publicada, editor, revisor):
    ficha_publicada.pago = "S/ 10.00"
    publicacion.marcar_editada(ficha_publicada, editor)
    ficha_publicada.save()

    publicacion.enviar_a_revision(ficha_publicada, editor)
    version = publicacion.aprobar(ficha_publicada, revisor)

    assert version.numero == 2
    assert version.contenido["pago"] == "S/ 10.00"
    assert ficha_publicada.estado_revision == Ficha.EstadoRevision.PUBLICADA


def test_quien_edita_no_puede_aprobar(ficha_publicada, revisor):
    ficha_publicada.pago = "S/ 10.00"
    publicacion.marcar_editada(ficha_publicada, revisor)
    ficha_publicada.save()
    publicacion.enviar_a_revision(ficha_publicada, revisor)
    with pytest.raises(ErrorDeNegocio):
        publicacion.aprobar(ficha_publicada, revisor)


def test_no_se_envia_a_revision_una_ficha_incompleta(proceso, editor):
    ficha = crear_ficha(proceso, codigo="BAC_P09", pago="", plazo="")
    with pytest.raises(ValidationError) as error:
        publicacion.enviar_a_revision(ficha, editor)
    assert set(error.value.detail) == {"pago", "plazo"}


def test_rechazo_exige_observaciones(ficha_publicada, editor, revisor):
    ficha_publicada.pago = "S/ 10.00"
    publicacion.marcar_editada(ficha_publicada, editor)
    ficha_publicada.save()
    publicacion.enviar_a_revision(ficha_publicada, editor)
    with pytest.raises(ValidationError):
        publicacion.rechazar(ficha_publicada, revisor, "  ")
    publicacion.rechazar(ficha_publicada, revisor, "Falta la resolución")
    assert ficha_publicada.estado_revision == Ficha.EstadoRevision.RECHAZADA


def test_publicar_retira_del_indice_las_secciones_anteriores(ficha_publicada, revisor):
    antes = SeccionIndexada.objects.filter(ficha=ficha_publicada, vigente=True).count()
    ficha_publicada.pago = "S/ 7.00"
    publicacion.publicar(ficha_publicada, revisor, indexar_en_segundo_plano=False)
    vigentes = SeccionIndexada.objects.filter(ficha=ficha_publicada, vigente=True)
    assert vigentes.count() == antes
    assert vigentes.get(seccion="pago").texto.endswith("S/ 7.00")
    assert SeccionIndexada.objects.filter(ficha=ficha_publicada, vigente=False).count() == antes


def test_revertir_publica_el_contenido_anterior_como_version_nueva(ficha_publicada, revisor):
    ficha_publicada.pago = "S/ 7.00"
    publicacion.publicar(ficha_publicada, revisor, indexar_en_segundo_plano=False)
    version = publicacion.revertir(ficha_publicada, 1, revisor)
    assert version.numero == 3
    assert version.contenido["pago"] == "S/ 5.00 en caja."
