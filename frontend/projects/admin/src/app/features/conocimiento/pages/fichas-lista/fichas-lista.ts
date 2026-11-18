import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, debounceTime, map, of, startWith, switchMap } from 'rxjs';
import { ESTADOS_REVISION, FichaResumen } from 'shared';
import { Auth } from '../../../../core/auth/auth';
import { ConocimientoApi, FiltrosFichas } from '../../data-access/conocimiento-api';

@Component({
  selector: 'app-fichas-lista',
  imports: [RouterLink, DatePipe],
  templateUrl: './fichas-lista.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FichasLista {
  private readonly api = inject(ConocimientoApi);
  protected readonly auth = inject(Auth);
  protected readonly estados = ESTADOS_REVISION;

  protected readonly filtros = signal<FiltrosFichas>({ page: 1 });
  protected readonly procesos = toSignal(this.api.procesos().pipe(catchError(() => of([]))), {
    initialValue: [],
  });

  private readonly respuesta = toSignal(
    toObservable(this.filtros).pipe(
      debounceTime(200),
      switchMap((f) =>
        this.api.fichas(f).pipe(
          map((r) => ({ cargando: false, fichas: r.results, total: r.count })),
          catchError(() => of({ cargando: false, fichas: [] as FichaResumen[], total: 0 })),
          startWith({ cargando: true, fichas: [] as FichaResumen[], total: 0 }),
        ),
      ),
    ),
    { initialValue: { cargando: true, fichas: [] as FichaResumen[], total: 0 } },
  );

  protected readonly cargando = computed(() => this.respuesta().cargando);
  protected readonly fichas = computed(() => this.respuesta().fichas);
  protected readonly total = computed(() => this.respuesta().total);
  protected readonly paginas = computed(() => Math.max(1, Math.ceil(this.total() / 20)));

  protected filtrar(campo: keyof FiltrosFichas, evento: Event) {
    const valor = (evento.target as HTMLInputElement | HTMLSelectElement).value;
    this.filtros.update((f) => ({ ...f, [campo]: valor, page: 1 }));
  }

  protected pagina(delta: number) {
    this.filtros.update((f) => ({ ...f, page: (f.page ?? 1) + delta }));
  }
}
