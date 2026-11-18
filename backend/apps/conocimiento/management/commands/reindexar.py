from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.generacion.proveedores.base import ErrorProveedor
from apps.nlu.services import embeber_ejemplos
from apps.recuperacion.services import reindexar_todo


class Command(BaseCommand):
    help = (
        "Recalcula con el proveedor activo los embeddings de las secciones publicadas y de los ejemplos "
        "de intents. Es obligatorio después de cambiar EMBED_PROVEEDOR o EMBED_MODELO. Si la cuota del "
        "proveedor se agota, lo ya calculado se conserva: vuelva a ejecutarlo y continúa donde quedó."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reintentos",
            type=int,
            default=6,
            help="Veces que espera y repite ante un límite de cuota por minuto (429). Por defecto, 6.",
        )
        parser.add_argument("--todo", action="store_true", help="Recalcula también lo que ya usa el proveedor activo.")

    def handle(self, *args, **opciones):
        proveedor = settings.EMBEDDINGS["PROVEEDOR"]
        reintentos = opciones["reintentos"]
        self.stdout.write(f"Proveedor de embeddings: {proveedor}")

        def avance(etiqueta):
            def _escribir(hecho, total):
                self.stdout.write(f"  {etiqueta}: {hecho}/{total}")

            return _escribir

        try:
            secciones = reindexar_todo(
                solo_pendientes=not opciones["todo"], reintentos=reintentos, al_avanzar=avance("fichas")
            )
            self.stdout.write(f"Secciones indexadas: {secciones}")
            ejemplos = embeber_ejemplos(todos=True, reintentos=reintentos, al_avanzar=avance("ejemplos"))
            self.stdout.write(f"Ejemplos de intents: {ejemplos}")
        except ErrorProveedor as exc:
            raise CommandError(
                f"{exc}\nLo calculado hasta aquí quedó guardado: al volver a ejecutar `manage.py reindexar` "
                "continuará donde quedó."
            ) from exc
        self.stdout.write(self.style.SUCCESS("Índice completo con el proveedor activo."))
