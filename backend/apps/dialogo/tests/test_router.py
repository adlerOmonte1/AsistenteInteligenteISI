import pytest

from apps.dialogo.router import Umbrales, Via, elegir_via

U = Umbrales(determinista=0.75, desambiguacion=0.40, intentos_antes_de_derivar=2)


@pytest.mark.parametrize(
    ("confianza", "intentos", "esperada"),
    [
        (0.90, 0, Via.DETERMINISTA),
        (0.75, 0, Via.DETERMINISTA),
        (0.74, 0, Via.DESAMBIGUACION),
        (0.40, 0, Via.DESAMBIGUACION),
        (0.39, 0, Via.RAG),
        (0.00, 1, Via.RAG),
        (0.99, 2, Via.DERIVACION),
    ],
)
def test_elegir_via_por_confianza_e_intentos(confianza, intentos, esperada):
    assert elegir_via(confianza, intentos, U) is esperada
