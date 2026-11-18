import { DatePipe, DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, debounceTime, map, of, startWith, switchMap } from 'rxjs';
import { Consulta, MarkdownPipe, NOMBRES_VIA } from 'shared';
import { CalidadApi } from '../../../calidad/data-access/calidad-api';

/**
 * Historial anonimizado. Sirve para encontrar preguntas mal resueltas: las
 * derivadas y las calificadas como no útiles suelen señalar una ficha que falta
 * o un intent con pocos ejemplos.
 */
@Component({
  selector: 'app-conversaciones',
  imports: [DatePipe, DecimalPipe, MarkdownPipe],
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Conversaciones</h1>
        <p>
          Preguntas registradas sin datos personales. Se eliminan automáticamente a los 12 meses.
        </p>
      </div>
    </header>

    <div class="filtros">
      <select (change)="filtrar('via', $event)" aria-label="Vía">
        <option value="">Todas las vías</option>
        @for (v of vias; track v[0]) {
          <option [value]="v[0]">{{ v[1] }}</option>
        }
      </select>
      <select (change)="filtrar('derivada', $event)" aria-label="Derivación">
        <option value="">Derivadas y no derivadas</option>
        <option value="true">Solo derivadas</option>
      </select>
      <select (change)="filtrar('util', $event)" aria-label="Calificación">
        <option value="">Cualquier calificación</option>
        <option value="false">Calificadas no útiles</option>
        <option value="true">Calificadas útiles</option>
      </select>
      <input
        type="search"
        placeholder="Texto de la pregunta"
        (input)="filtrar('q', $event)"
        aria-label="Buscar"
      />
    </div>

    <div class="pila">
      @for (c of consultas(); track c.id) {
        <details class="tarjeta">
          <summary>
            <span class="tenue fecha">{{ c.creada | date: 'dd/MM HH:mm' }}</span>
            <span class="pregunta">{{ c.pregunta }}</span>
            <span class="insignia info">{{ nombresVia[c.via] ?? c.via }}</span>
            @if (c.derivada) {
              <span class="insignia peligro">derivada</span>
            }
            @if (c.util === false) {
              <span class="insignia alerta">no útil</span>
            } @else if (c.util) {
              <span class="insignia exito">útil</span>
            }
          </summary>
          <div class="detalle">
            <div class="contenido-markdown respuesta" [innerHTML]="c.respuesta | markdown"></div>
            <p class="tenue meta">
              intent {{ c.intent || '—' }} ({{ c.confianza | number: '1.2-2' }}) · fichas
              {{ c.fichas_citadas.join(', ') || '—' }} · {{ c.latencia_ms }} ms ·
              {{ c.tokens_entrada + c.tokens_salida }} tokens{{ c.motivo ? ' · ' + c.motivo : ''
              }}{{
                c.datos_no_respaldados.length
                  ? ' · no respaldados: ' + c.datos_no_respaldados.join(', ')
                  : ''
              }}
            </p>
          </div>
        </details>
      } @empty {
        <p class="vacio">
          {{ cargando() ? 'Cargando…' : 'No hay conversaciones con esos filtros.' }}
        </p>
      }
    </div>

    <div class="paginacion">
      <span>{{ total() }} consultas · página {{ filtros().page }}</span>
      <button class="boton secundario chico" (click)="pagina(-1)" [disabled]="filtros().page <= 1">
        Anterior
      </button>
      <button
        class="boton secundario chico"
        (click)="pagina(1)"
        [disabled]="filtros().page * 20 >= total()"
      >
        Siguiente
      </button>
    </div>
  `,
  styles: `
    summary {
      display: flex;
      gap: 10px;
      align-items: center;
      cursor: pointer;
    }
    .fecha {
      flex: none;
      font-size: 12.5px;
    }
    .pregunta {
      flex: 1;
    }
    .detalle {
      margin-top: 12px;
    }
    .respuesta {
      padding: 12px;
      background: var(--udh-superficie-alterna);
      border-radius: 8px;
    }
    .meta {
      font-size: 12.5px;
      margin: 8px 0 0;
    }
    details.tarjeta {
      padding: 12px 16px;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Conversaciones {
  private readonly api = inject(CalidadApi);
  protected readonly nombresVia = NOMBRES_VIA;
  protected readonly vias = Object.entries(NOMBRES_VIA);

  protected readonly filtros = signal({ via: '', derivada: '', util: '', q: '', page: 1 });
  private readonly respuesta = toSignal(
    toObservable(this.filtros).pipe(
      debounceTime(250),
      switchMap((f) =>
        this.api.conversaciones(f).pipe(
          map((r) => ({ consultas: r.results, total: r.count })),
          catchError(() => of({ consultas: [] as Consulta[], total: 0 })),
          startWith(null),
        ),
      ),
    ),
    { initialValue: null },
  );
  protected readonly consultas = computed(() => this.respuesta()?.consultas ?? []);
  protected readonly total = computed(() => this.respuesta()?.total ?? 0);
  protected readonly cargando = computed(() => this.respuesta() === null);

  protected filtrar(campo: 'via' | 'derivada' | 'util' | 'q', evento: Event) {
    const valor = (evento.target as HTMLInputElement).value;
    this.filtros.update((f) => ({ ...f, [campo]: valor, page: 1 }));
  }

  protected pagina(delta: number) {
    this.filtros.update((f) => ({ ...f, page: f.page + delta }));
  }
}
