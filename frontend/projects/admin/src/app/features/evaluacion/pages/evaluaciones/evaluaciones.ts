import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';
import { Evaluacion, MetricasEvaluacion } from 'shared';
import { Notificaciones } from '../../../../core/http/notificaciones';
import { CalidadApi } from '../../../calidad/data-access/calidad-api';
import { ConocimientoApi } from '../../../conocimiento/data-access/conocimiento-api';

const MOTIVOS: Record<string, string> = {
  manual: 'Manual',
  revision: 'Revisión',
  humo: 'Prueba de humo',
};

/** Golden set: ejecuta las preguntas de prueba y compara con las metas del sistema. */
@Component({
  selector: 'app-evaluaciones',
  imports: [RouterLink, DatePipe],
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Golden set</h1>
        <p>Metas: intent ≥ 90 %, ficha ≥ 90 %, respuesta clave ≥ 95 % y cero datos inventados.</p>
      </div>
      <form class="fila" (submit)="ejecutar($event)">
        <select name="proceso" aria-label="Proceso">
          <option value="">Todos los procesos</option>
          @for (p of procesos(); track p.id) {
            <option [value]="p.clave">{{ p.nombre }}</option>
          }
        </select>
        <button class="boton" type="submit">Ejecutar</button>
      </form>
    </header>

    <div class="tabla-contenedor">
      <table class="tabla">
        <thead>
          <tr>
            <th>#</th>
            <th>Proceso</th>
            <th>Motivo</th>
            <th>Estado</th>
            <th>Casos</th>
            <th>Intent</th>
            <th>Ficha</th>
            <th>Clave</th>
            <th>Inventados</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          @for (e of evaluaciones(); track e.id) {
            @let m = metricas(e);
            <tr>
              <td>
                <a [routerLink]="['/evaluacion', e.id]">{{ e.id }}</a>
              </td>
              <td>{{ e.proceso_nombre ?? 'Todos' }}</td>
              <td class="tenue">{{ motivos[e.motivo] }}</td>
              <td>
                <span
                  class="insignia"
                  [class.exito]="e.estado === 'completada'"
                  [class.alerta]="e.estado === 'ejecutando' || e.estado === 'pendiente'"
                  [class.peligro]="e.estado === 'error'"
                  >{{ e.estado }}</span
                >
              </td>
              <td>{{ m?.casos ?? '—' }}</td>
              <td [class.falla]="m && !m.cumple['exactitud_intent']">
                {{ porcentaje(m?.exactitud_intent) }}
              </td>
              <td [class.falla]="m && !m.cumple['exactitud_ficha']">
                {{ porcentaje(m?.exactitud_ficha) }}
              </td>
              <td [class.falla]="m && !m.cumple['clave_contenida']">
                {{ porcentaje(m?.clave_contenida) }}
              </td>
              <td [class.falla]="m && m.datos_inventados > 0">{{ m?.datos_inventados ?? '—' }}</td>
              <td class="tenue">{{ e.creada | date: 'dd/MM HH:mm' }}</td>
            </tr>
          } @empty {
            <tr>
              <td colspan="10" class="vacio">Aún no se ha ejecutado ninguna evaluación.</td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
  styles: `
    .falla {
      color: var(--udh-peligro);
      font-weight: 700;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Evaluaciones implements OnDestroy {
  private readonly api = inject(CalidadApi);
  private readonly avisos = inject(Notificaciones);
  private sondeo?: ReturnType<typeof setInterval>;

  protected readonly motivos = MOTIVOS;
  protected readonly procesos = toSignal(
    inject(ConocimientoApi)
      .procesos()
      .pipe(catchError(() => of([]))),
    {
      initialValue: [],
    },
  );
  protected readonly evaluaciones = signal<Evaluacion[]>([]);

  constructor() {
    this.refrescar();
  }

  ngOnDestroy() {
    clearInterval(this.sondeo);
  }

  protected metricas(e: Evaluacion): MetricasEvaluacion | null {
    return 'casos' in e.metricas ? (e.metricas as MetricasEvaluacion) : null;
  }

  protected porcentaje(valor: number | null | undefined): string {
    return valor == null ? '—' : `${valor} %`;
  }

  protected ejecutar(evento: SubmitEvent) {
    evento.preventDefault();
    const proceso =
      String(new FormData(evento.target as HTMLFormElement).get('proceso') || '') || null;
    this.api.evaluar(proceso).subscribe(() => {
      this.avisos.info('Evaluación en curso. Los resultados aparecerán en unos segundos.');
      this.refrescar();
    });
  }

  private refrescar() {
    this.api.evaluaciones().subscribe((r) => {
      this.evaluaciones.set(r.results);
      clearInterval(this.sondeo);
      if (r.results.some((e) => e.estado === 'pendiente' || e.estado === 'ejecutando')) {
        this.sondeo = setInterval(() => this.refrescar(), 3000);
      }
    });
  }
}
