import { ChangeDetectionStrategy, Component, inject, input } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, map, of, startWith, switchMap } from 'rxjs';
import { ResultadoBusqueda } from 'shared';
import { PortalApi } from '../../core/portal-api';

@Component({
  selector: 'app-buscar',
  imports: [RouterLink],
  template: `
    <div class="contenedor pila">
      <h1>Resultados para «{{ q() }}»</h1>
      @let e = estado();
      @if (e.cargando) {
        <p class="tenue">Buscando…</p>
      } @else {
        @for (r of e.resultados; track r.codigo) {
          <a
            class="tarjeta resultado"
            [routerLink]="['/tramites', r.proceso]"
            [fragment]="r.codigo"
          >
            <span class="insignia info">{{ r.proceso_nombre }}</span>
            <strong>{{ r.titulo }}</strong>
            <span class="tenue">{{ r.fragmento }}…</span>
          </a>
        } @empty {
          <div class="aviso">
            No encontramos fases que coincidan. Pruebe con otras palabras o
            <a routerLink="/asistente">pregúntele al asistente</a>.
          </div>
        }
      }
    </div>
  `,
  styles: `
    :host {
      display: block;
      padding-top: 28px;
    }
    .resultado {
      display: flex;
      flex-direction: column;
      gap: 6px;
      align-items: flex-start;
      text-decoration: none;
      color: inherit;
    }
    .resultado:hover {
      border-color: var(--udh-primario);
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Buscar {
  private readonly api = inject(PortalApi);

  /** Parámetro ?q= de la URL. */
  readonly q = input('');

  protected readonly estado = toSignal(
    toObservable(this.q).pipe(
      switchMap((q) =>
        this.api.buscar(q).pipe(
          map((r) => ({ cargando: false, resultados: r.resultados })),
          catchError(() => of({ cargando: false, resultados: [] as ResultadoBusqueda[] })),
          startWith({ cargando: true, resultados: [] as ResultadoBusqueda[] }),
        ),
      ),
    ),
    { initialValue: { cargando: true, resultados: [] as ResultadoBusqueda[] } },
  );
}
