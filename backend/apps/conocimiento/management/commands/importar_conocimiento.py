from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.conocimiento.services.importador import Importador
from apps.generacion.proveedores.base import ErrorProveedor
from apps.nlu.services import embeber_ejemplos


class Command(BaseCommand):
    help = "Carga knowledge-base/ (fichas, intents, golden set, pendientes y plantillas) en la base de datos."

    def add_arguments(self, parser):
        parser.add_argument("--carpeta", default=None, help="Raíz de knowledge-base (por defecto, la del repositorio).")
        parser.add_argument("--proceso", action="append", help="Importar solo este proceso (se puede repetir).")
        parser.add_argument("--sin-publicar", action="store_true", help="Deja las fichas en borrador.")
        parser.add_argument("--estricto", action="store_true", help="No publica fichas que incumplan el contrato.")
        parser.add_argument("--dry-run", action="store_true", help="Muestra el reporte y deshace todos los cambios.")
        parser.add_argument("--detalle", action="store_true", help="Muestra todos los avisos.")
        parser.add_argument(
            "--sin-indexar",
            action="store_true",
            help="Publica sin calcular embeddings (no gasta cuota del proveedor). Luego ejecute `reindexar`.",
        )

    def handle(self, *args, **opciones):
        base = Path(opciones["carpeta"]) if opciones["carpeta"] else settings.ASISTENTE["CARPETA_CONOCIMIENTO"].parent
        if not (base / "catalogo.yaml").is_file():
            raise CommandError(f"No se encontró {base / 'catalogo.yaml'}")

        importador = Importador(
            base,
            publicar=not opciones["sin_publicar"],
            estricto=opciones["estricto"],
            solo=opciones["proceso"],
            # La simulación nunca llama al proveedor: no tiene sentido gastar cuota en algo que se deshace.
            indexar=not (opciones["sin_indexar"] or opciones["dry_run"]),
        )
        with transaction.atomic():
            reporte = importador.ejecutar()
            try:
                ejemplos = 0 if opciones["sin_indexar"] or opciones["dry_run"] else embeber_ejemplos()
            except ErrorProveedor as exc:
                # Sin cuota o sin conexión: los ejemplos quedan sin vector y `reindexar` los completa luego.
                ejemplos = 0
                self.stdout.write(self.style.WARNING(f"Embeddings de ejemplos pendientes: {exc}"))
            self._imprimir(reporte, ejemplos, opciones["detalle"])
            if opciones["dry_run"]:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING("Simulación: no se guardó ningún cambio."))
        # Los procesos sin errores ya quedaron guardados; el código de salida avisa al CI.
        if reporte.errores:
            raise CommandError(f"La importación terminó con {reporte.errores} errores.")

    def _imprimir(self, reporte, ejemplos, detalle):
        self.stdout.write("")
        cabecera = (
            f"{'proceso':<24}{'fichas':>7}{'publ.':>7}{'intents':>9}{'ejempl.':>9}"
            f"{'golden':>8}{'pend.':>7}{'avisos':>8}{'errores':>9}"
        )
        self.stdout.write(cabecera)
        self.stdout.write("-" * len(cabecera))
        for p in reporte.procesos:
            self.stdout.write(
                f"{p.clave:<24}{p.fichas:>7}{p.publicadas:>7}{p.intents:>9}{p.ejemplos:>9}{p.casos:>8}"
                f"{p.pendientes:>7}{len(p.avisos):>8}{len(p.errores):>9}"
            )
        self.stdout.write("")
        for p in reporte.procesos:
            for error in p.errores:
                self.stdout.write(self.style.ERROR(f"[{p.clave}] {error}"))
            avisos = p.avisos if detalle else p.avisos[:5]
            for aviso in avisos:
                self.stdout.write(self.style.WARNING(f"[{p.clave}] {aviso}"))
            if not detalle and len(p.avisos) > 5:
                self.stdout.write(f"[{p.clave}] … {len(p.avisos) - 5} avisos más (use --detalle)")
        self.stdout.write(f"\nEmbeddings calculados para {ejemplos} ejemplos de intents.")
        estilo = self.style.ERROR if reporte.errores else self.style.SUCCESS
        self.stdout.write(estilo(f"Errores: {reporte.errores} · avisos: {reporte.avisos}"))
