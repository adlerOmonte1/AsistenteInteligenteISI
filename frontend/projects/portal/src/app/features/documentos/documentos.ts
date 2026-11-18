import { ChangeDetectionStrategy, Component, computed, inject, input, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { catchError, combineLatest, debounceTime, map, of, startWith, switchMap } from 'rxjs';
import { Documento, TIPOS_DOCUMENTO, TipoDocumento } from 'shared';
import { PortalApi } from '../../core/portal-api';

/** Biblioteca normativa: resoluciones, reglamentos, formatos y guías de cada trámite. */
@Component({
  selector: 'app-documentos',
  templateUrl: './documentos.html',
  styleUrl: './documentos.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Documentos {
  private readonly api = inject(PortalApi);
  private readonly router = inject(Router);

  /** Filtro inicial desde la URL (?proceso=ppp). */
  readonly proceso = input<string>('');

  protected readonly tipos = Object.entries(TIPOS_DOCUMENTO) as [TipoDocumento, string][];
  protected readonly nombresTipo = TIPOS_DOCUMENTO;
  protected readonly tipo = signal('');
  protected readonly q = signal('');

  protected readonly procesos = toSignal(this.api.procesos().pipe(catchError(() => of([]))), {
    initialValue: [],
  });

  private readonly resultado = toSignal(
    combineLatest([
      toObservable(this.proceso),
      toObservable(this.tipo),
      toObservable(this.q).pipe(debounceTime(300)),
    ]).pipe(
      switchMap(([proceso, tipo, q]) =>
        this.api.documentos({ proceso, tipo, q }).pipe(
          map((r) => ({ cargando: false, documentos: r.results, total: r.count, error: false })),
          catchError(() =>
            of({ cargando: false, documentos: [] as Documento[], total: 0, error: true }),
          ),
          startWith({ cargando: true, documentos: [] as Documento[], total: 0, error: false }),
        ),
      ),
    ),
    { initialValue: { cargando: true, documentos: [] as Documento[], total: 0, error: false } },
  );

  protected readonly cargando = computed(() => this.resultado().cargando);
  protected readonly documentos = computed(() => this.resultado().documentos);
  protected readonly total = computed(() => this.resultado().total);
  protected readonly error = computed(() => this.resultado().error);

  protected cambiarProceso(evento: Event) {
    const proceso = (evento.target as HTMLSelectElement).value;
    void this.router.navigate([], {
      queryParams: { proceso: proceso || null },
      queryParamsHandling: 'merge',
    });
  }

  protected cambiarTipo(evento: Event) {
    this.tipo.set((evento.target as HTMLSelectElement).value);
  }

  protected cambiarTexto(evento: Event) {
    this.q.set((evento.target as HTMLInputElement).value.trim());
  }
}
