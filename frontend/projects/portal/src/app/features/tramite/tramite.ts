import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  inject,
  input,
  signal,
} from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { Title } from '@angular/platform-browser';
import { RouterLink } from '@angular/router';
import { catchError, map, of, startWith, switchMap } from 'rxjs';
import {
  DetalleProceso,
  FichaPublicada,
  MarkdownPipe,
  SECCIONES,
  Seccion,
  TIPOS_DOCUMENTO,
  TITULOS_SECCION,
} from 'shared';
import { PortalApi } from '../../core/portal-api';

type Estado = { cargando: true } | { cargando: false; detalle: DetalleProceso | null };

@Component({
  selector: 'app-tramite',
  imports: [RouterLink, MarkdownPipe],
  templateUrl: './tramite.html',
  styleUrl: './tramite.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Tramite {
  private readonly api = inject(PortalApi);
  private readonly titulo = inject(Title);

  /** Parámetro de ruta :clave. */
  readonly clave = input.required<string>();

  protected readonly secciones = SECCIONES;
  protected readonly titulos = TITULOS_SECCION;
  protected readonly tipos = TIPOS_DOCUMENTO;
  protected readonly abierta = signal<string | null>(null);

  protected readonly estado = toSignal<Estado, Estado>(
    toObservable(this.clave).pipe(
      switchMap((clave) =>
        this.api.proceso(clave).pipe(
          map((detalle) => ({ cargando: false as const, detalle })),
          catchError(() => of({ cargando: false as const, detalle: null })),
          startWith({ cargando: true as const }),
        ),
      ),
    ),
    { initialValue: { cargando: true } },
  );

  protected readonly detalle = computed(() => {
    const e = this.estado();
    return e.cargando ? null : e.detalle;
  });

  constructor() {
    effect(() => {
      const d = this.detalle();
      if (d) {
        this.titulo.setTitle(`${d.proceso.nombre} · Asistente Académico UDH`);
        this.abierta.set(d.fichas[0]?.codigo ?? null);
      }
    });
  }

  protected alternar(ficha: FichaPublicada) {
    this.abierta.update((actual) => (actual === ficha.codigo ? null : ficha.codigo));
  }

  protected valor(ficha: FichaPublicada, seccion: Seccion): string {
    return ficha.contenido[seccion] ?? '';
  }

  protected tituloFase(codigo: string): string | null {
    const ficha = this.detalle()?.fichas.find((f) => f.codigo === codigo.trim());
    return ficha?.contenido.titulo ?? null;
  }
}
