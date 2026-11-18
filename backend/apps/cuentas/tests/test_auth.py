import pytest
from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db
COOKIE = settings.COOKIE_REFRESH["NOMBRE"]


def _login(api, username="editor", password="Clave-Segura-2026"):
    return api.post(reverse("auth-login"), {"username": username, "password": password}, format="json")


def test_login_entrega_access_en_el_cuerpo_y_refresh_en_cookie_httponly(api, editor):
    respuesta = _login(api)
    assert respuesta.status_code == 200
    assert "access" in respuesta.data and "refresh" not in respuesta.data
    cookie = respuesta.cookies[COOKIE]
    assert cookie["httponly"] and cookie["path"] == "/api/v1/auth/"


def test_refresh_rota_el_token_y_el_anterior_queda_invalido(api, editor):
    _login(api)
    anterior = api.cookies[COOKIE].value
    renovado = api.post(reverse("auth-refresh"))
    assert renovado.status_code == 200
    api.cookies[COOKIE] = anterior
    assert api.post(reverse("auth-refresh")).status_code == 401


def test_logout_invalida_el_refresh(api, editor):
    _login(api)
    token = api.cookies[COOKIE].value
    api.post(reverse("auth-logout"))
    api.cookies[COOKIE] = token
    assert api.post(reverse("auth-refresh")).status_code == 401


def test_bloqueo_tras_cinco_intentos_fallidos(api, editor):
    for _ in range(5):
        assert _login(api, password="incorrecta").status_code == 401
    assert _login(api).status_code == 429


def test_permisos_por_rol(como, lector, editor, superadmin):
    assert como(lector).get(reverse("ficha-list")).status_code == 200
    assert como(lector).post(reverse("ficha-list"), {}, format="json").status_code == 403
    assert como(editor).get(reverse("usuario-list")).status_code == 403
    assert como(superadmin).get(reverse("usuario-list")).status_code == 200


def test_superadmin_crea_cuentas_con_contrasena_segura(como, superadmin):
    debil = como(superadmin).post(
        reverse("usuario-list"), {"username": "nuevo", "password": "123", "rol": "editor"}, format="json"
    )
    assert debil.status_code == 400
    fuerte = como(superadmin).post(
        reverse("usuario-list"), {"username": "nuevo", "password": "Otra-Clave-2026", "rol": "editor"}, format="json"
    )
    assert fuerte.status_code == 201
