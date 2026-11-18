import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { FichaResumen } from 'shared';
import { ConocimientoApi } from '../../data-access/conocimiento-api';

/** Bandeja del revisor: fichas que esperan aprobación. */
@Component({
  selector: 'app-revision',
  imports: [RouterLink, DatePipe],
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Bandeja de revisión</h1>
        <p>
          Fichas que un editor envió a revisión. Ábralas para comparar con la versión publicada y
          aprobar o rechazar.
        </p>
      </div>
    </header>
    @let lista = fichas();
    @if (lista === null) {
      <p class="tenue">Cargando…</p>
    } @else {
      <div class="tabla-contenedor">
        <table class="tabla">
          <thead>
            <tr>
              <th>Código</th>
              <th>Título</th>
              <th>Proceso</th>
              <th>Versión actual</th>
              <th>Enviada por</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            @for (f of lista; track f.id) {
              <tr>
                <td class="mono">
                  <a [routerLink]="['/fichas', f.id]">{{ f.codigo }}</a>
                </td>
                <td>{{ f.titulo }}</td>
                <td class="tenue">{{ f.proceso_nombre }}</td>
                <td>{{ f.version ? 'v' + f.version : 'Nueva' }}</td>
                <td>{{ f.actualizada_por ?? '—' }}</td>
                <td class="tenue">{{ f.actualizada | date: 'dd/MM/yyyy HH:mm' }}</td>
              </tr>
            } @empty {
              <tr>
                <td colspan="6" class="vacio">No hay fichas pendientes de revisión.</td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Revision {
  private readonly api = inject(ConocimientoApi);

  protected readonly fichas = toSignal<FichaResumen[] | null>(
    this.api.fichas({ publicacion: 'en_revision' }).pipe(
      map((r) => r.results),
      catchError(() => of([])),
    ),
    { initialValue: null },
  );
}
