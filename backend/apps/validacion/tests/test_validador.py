from apps.validacion.services import extraer_datos, validar

FUENTE = (
    "Pago: S/ 5.00 en caja. Plazo: máximo 20 días hábiles. "
    "Enviar a secretaria.sistemas.hco@udh.edu.pe. Fuente: Res. N.° 2367-2025-R-CU-UDH."
)


def test_extrae_los_cuatro_tipos_de_dato():
    datos = extraer_datos(FUENTE)
    assert datos["correos"] == {"secretaria.sistemas.hco@udh.edu.pe"}
    assert datos["montos"] == {"5.00"}
    assert datos["plazos"] == {"20 dia"}
    assert datos["resoluciones"] == {"2367-2025-R-CU-UDH"}


def test_respuesta_respaldada_es_valida_aunque_cambie_el_formato():
    respuesta = "Debe pagar S/5 y enviarlo a Secretaria.Sistemas.Hco@udh.edu.pe en 20 dias."
    assert validar(respuesta, [FUENTE]).valida


def test_monto_inventado_se_rechaza():
    resultado = validar("El trámite cuesta S/ 50.00.", [FUENTE])
    assert not resultado.valida
    assert resultado.no_respaldados == ["montos:50.00"]


def test_correo_y_plazo_inventados_se_rechazan():
    resultado = validar("Escriba a coordinacion@udh.edu.pe; responden en 3 meses.", [FUENTE])
    assert set(resultado.no_respaldados) == {"correos:coordinacion@udh.edu.pe", "plazos:3 mes"}


def test_resolucion_inventada_se_rechaza():
    assert not validar("Según la Res. N.° 999-2024-R-CU-UDH.", [FUENTE]).valida


def test_respuesta_sin_datos_criticos_es_valida():
    assert validar("Consulte con la Coordinación del programa.", [FUENTE]).valida
