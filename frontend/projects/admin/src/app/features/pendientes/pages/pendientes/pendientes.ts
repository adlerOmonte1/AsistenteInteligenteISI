import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of, startWith, switchMap } from 'rxjs';
import { Pendiente } from 'shared';
import { Notificaciones } from '../../../../core/http/notificaciones';
import { ConocimientoApi } from '../../../conocimiento/data-access/conocimiento-api';
import { PendientesApi } from '../../data-access/pendientes-api';

/**
 * Datos que faltan confirmar con Coordinación. Resolver un pendiente no cambia
 * ninguna ficha: después hay que editar la ficha afectada y publicarla.
 */
@Component({
  selector: 'app-pendientes',
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Pendientes con Coordinación</h1>
        <p>
          Preguntas abiertas sobre datos que la normativa no precisa. El asistente los informa como
          «no confirmados».
        </p>
      </div>
    </header>

    <div class="filtros">
      <select (change)="filtrar('proceso', $event)" aria-label="Proceso">
        <option value="">Todos los procesos</option>
        @for (p of procesos(); track p.id) {
          <option [value]="p.clave">{{ p.nombre }}</option>
        }
      </select>
      <select (change)="filtrar('resuelto', $event)" aria-label="Estado">
        <option value="false">Sin resolver</option>
        <option value="true">Resueltos</option>
        <option value="">Todos</option>
      </select>
    </div>

    <div class="pila">
      @for (p of pendientes(); track p.id) {
        <article class="tarjeta">
          <div class="fila">
            <strong class="mono">{{ p.codigo }}</strong>
            <span class="insignia">{{ p.proceso_clave }}</span>
            @for (f of p.fichas; track f) {
              <span class="insignia info mono">{{ f }}</span>
            }
            <span class="espaciador"></span>
            <span class="insignia" [class.exito]="p.resuelto" [class.alerta]="!p.resuelto">
              {{ p.resuelto ? 'Resuelto' : 'Pendiente' }}
            </span>
          </div>
          <p>{{ p.descripcion }}</p>
          @if (p.pregunta) {
            <p class="tenue"><strong>Pregunta:</strong> {{ p.pregunta }}</p>
          }
          <form class="resolver" (submit)="resolver($event, p)">
            <input
              type="text"
              name="resolucion"
              [value]="p.resolucion"
              placeholder="Respuesta de Coordinación y documento que la respalda"
            />
            <button class="boton chico" [class.secundario]="p.resuelto" type="submit">
              {{ p.resuelto ? 'Reabrir' : 'Marcar resuelto' }}
            </button>
          </form>
        </article>
      } @empty {
        <p class="vacio">{{ cargando() ? 'Cargando…' : 'No hay pendientes con esos filtros.' }}</p>
      }
    </div>
  `,
  styles: `
    article p {
      margin: 8px 0 0;
    }
    .resolver {
      display: flex;
      gap: 8px;
      margin-top: 10px;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Pendientes {
  private readonly api = inject(PendientesApi);
  private readonly avisos = inject(Notificaciones);
  protected readonly procesos = toSignal(
    inject(ConocimientoApi)
      .procesos()
      .pipe(catchError(() => of([]))),
    {
      initialValue: [],
    },
  );

  protected readonly filtros = signal({ proceso: '', resuelto: 'false', recarga: 0 });
  private readonly respuesta = toSignal(
    toObservable(this.filtros).pipe(
      switchMap(({ recarga: _, ...f }) =>
        this.api.listar({ ...f, page: 1 }).pipe(
          map((r) => r.results),
          catchError(() => of([] as Pendiente[])),
          startWith(null),
        ),
      ),
    ),
    { initialValue: null },
  );
  protected readonly pendientes = computed(() => this.respuesta() ?? []);
  protected readonly cargando = computed(() => this.respuesta() === null);

  protected filtrar(campo: 'proceso' | 'resuelto', evento: Event) {
    const valor = (evento.target as HTMLSelectElement).value;
    this.filtros.update((f) => ({ ...f, [campo]: valor }));
  }

  protected resolver(evento: SubmitEvent, p: Pendiente) {
    evento.preventDefault();
    const resolucion = String(
      new FormData(evento.target as HTMLFormElement).get('resolucion') ?? '',
    ).trim();
    if (!p.resuelto && !resolucion) {
      this.avisos.error('Anote la respuesta de Coordinación antes de marcarlo como resuelto.');
      return;
    }
    this.api.resolver(p.id, !p.resuelto, resolucion).subscribe(() => {
      this.avisos.exito(
        p.resuelto
          ? 'Pendiente reabierto.'
          : 'Pendiente resuelto. Recuerde actualizar las fichas afectadas.',
      );
      this.filtros.update((f) => ({ ...f, recarga: f.recarga + 1 }));
    });
  }
}
