import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { Router, RouterLink } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { Proceso } from 'shared';
import { PortalApi } from '../../core/portal-api';

type Estado = { cargando: true } | { cargando: false; procesos: Proceso[]; error: boolean };

@Component({
  selector: 'app-inicio',
  imports: [RouterLink],
  templateUrl: './inicio.html',
  styleUrl: './inicio.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Inicio {
  private readonly api = inject(PortalApi);
  private readonly router = inject(Router);

  protected readonly termino = signal('');
  protected readonly estado = toSignal<Estado, Estado>(
    this.api.procesos().pipe(
      map((procesos) => ({ cargando: false as const, procesos, error: false })),
      catchError(() => of({ cargando: false as const, procesos: [], error: true })),
    ),
    { initialValue: { cargando: true } },
  );

  protected buscar(evento: Event) {
    evento.preventDefault();
    const q = this.termino().trim();
    if (q.length >= 3) void this.router.navigate(['/buscar'], { queryParams: { q } });
  }

  protected alEscribir(evento: Event) {
    this.termino.set((evento.target as HTMLInputElement).value);
  }
}
