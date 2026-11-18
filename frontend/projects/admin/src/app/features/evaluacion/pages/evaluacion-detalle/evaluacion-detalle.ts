import { DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, input, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, of, switchMap } from 'rxjs';
import { Evaluacion, MetricasEvaluacion } from 'shared';
import { CalidadApi } from '../../../calidad/data-access/calidad-api';

/** Resultado caso por caso de una ejecución del golden set. */
@Component({
  selector: 'app-evaluacion-detalle',
  imports: [RouterLink, DecimalPipe],
  template: `
    <header class="pagina-cabecera">
      <div>
        <a routerLink="/evaluacion">← Golden set</a>
        <h1>
          Evaluación {{ id()
          }}{{ evaluacion()?.proceso_nombre ? ' · ' + evaluacion()?.proceso_nombre : '' }}
        </h1>
        @if (metricas(); as m) {
          <p>
            Intent {{ m.exactitud_intent ?? '—' }} % · Ficha {{ m.exactitud_ficha ?? '—' }} % ·
            Clave {{ m.clave_contenida ?? '—' }} % · Inventados {{ m.datos_inventados }} ·
            {{ m.cumple_todas ? 'Cumple todas las metas' : 'No cumple todas las metas' }}
          </p>
        }
      </div>
      <label class="fila tenue"
        ><input type="checkbox" (change)="soloFallos.set($any($event.target).checked)" /> Solo
        fallos</label
      >
    </header>

    <div class="tabla-contenedor">
      <table class="tabla">
        <thead>
          <tr>
            <th>Caso</th>
            <th>Pregunta</th>
            <th>Intent esperado / obtenido</th>
            <th>Ficha esperada / obtenida</th>
            <th>Vía</th>
            <th>Clave</th>
          </tr>
        </thead>
        <tbody>
          @for (r of filas(); track r.id) {
            <tr [class.inventado]="r.dato_inventado">
              <td class="mono">{{ r.codigo }}</td>
              <td>
                {{ r.pregunta }}
                <details>
                  <summary class="tenue">Respuesta</summary>
                  <p class="respuesta">{{ r.respuesta }}</p>
                </details>
              </td>
              <td class="mono">
                <span>{{ r.intent_esperado || '—' }}</span><br />
                <span [class]="marca(r.acierto_intent)"
                  >{{ r.intent_obtenido || '—' }} ({{ r.confianza | number: '1.2-2' }})</span
                >
              </td>
              <td class="mono">
                <span>{{ r.ficha_esperada || '—' }}</span><br />
                <span [class]="marca(r.acierto_ficha)">{{
                  r.fichas_obtenidas.join(', ') || '—'
                }}</span>
              </td>
              <td>{{ r.via }}</td>
              <td>
                <span [class]="marca(r.clave_contenida)">{{
                  r.clave_contenida === null ? '—' : r.clave_contenida ? 'sí' : 'no'
                }}</span>
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="6" class="vacio">Sin resultados.</td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
  styles: `
    .ok {
      color: var(--udh-exito);
      font-weight: 600;
    }
    .mal {
      color: var(--udh-peligro);
      font-weight: 600;
    }
    .inventado {
      background: var(--udh-peligro-suave);
    }
    .respuesta {
      white-space: pre-wrap;
      font-size: 13px;
    }
    header a {
      font-size: 13px;
      text-decoration: none;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EvaluacionDetalle {
  private readonly api = inject(CalidadApi);

  readonly id = input.required<string>();
  protected readonly soloFallos = signal(false);

  protected readonly evaluacion = toSignal<Evaluacion | null>(
    toObservable(this.id).pipe(
      switchMap((id) => this.api.evaluacion(Number(id)).pipe(catchError(() => of(null)))),
    ),
    { initialValue: null },
  );

  protected readonly metricas = computed(() => {
    const m = this.evaluacion()?.metricas;
    return m && 'casos' in m ? (m as MetricasEvaluacion) : null;
  });

  protected readonly filas = computed(() => {
    const resultados = this.evaluacion()?.resultados ?? [];
    if (!this.soloFallos()) return resultados;
    return resultados.filter(
      (r) =>
        r.acierto_intent === false ||
        r.acierto_ficha === false ||
        r.clave_contenida === false ||
        r.dato_inventado,
    );
  });

  protected marca(acierto: boolean | null): string {
    return acierto === null ? '' : acierto ? 'ok' : 'mal';
  }
}
