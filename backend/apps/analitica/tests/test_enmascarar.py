from apps.analitica.services import enmascarar


def test_enmascara_dni_codigo_telefono_y_correo_personal():
    texto = "Mi DNI es 70123456, código 2019110234, cel 987 654 321, correo juan.perez@gmail.com"
    resultado = enmascarar(texto)
    assert "70123456" not in resultado
    assert "2019110234" not in resultado
    assert "987 654 321" not in resultado
    assert "gmail" not in resultado
    assert "[dni]" in resultado and "[codigo]" in resultado and "[telefono]" in resultado


def test_conserva_correos_institucionales_y_montos():
    texto = "¿Envío a secretaria.sistemas.hco@udh.edu.pe y pago S/ 5.00?"
    assert enmascarar(texto) == texto
