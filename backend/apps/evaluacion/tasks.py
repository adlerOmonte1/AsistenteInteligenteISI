from . import services


def ejecutar_evaluacion(evaluacion_id: int):
    return services.ejecutar(evaluacion_id).estado
