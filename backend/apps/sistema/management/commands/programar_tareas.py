from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Registra las tareas periódicas del worker (idempotente)."

    TAREAS = [
        {
            "name": "purgar-consultas-antiguas",
            "func": "apps.analitica.tasks.purgar_consultas_antiguas",
            "schedule_type": Schedule.DAILY,
        },
    ]

    def handle(self, *args, **opciones):
        for tarea in self.TAREAS:
            _, creada = Schedule.objects.update_or_create(name=tarea["name"], defaults=tarea)
            self.stdout.write(f"{'Creada' if creada else 'Actualizada'}: {tarea['name']}")
