import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  computed,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, debounceTime, map, of, startWith, switchMap } from 'rxjs';
import { Intent, SECCIONES, TITULOS_SECCION } from 'shared';
import { erroresDeCampo } from '../../../../core/http/error-interceptor';
import { Notificaciones } from '../../../../core/http/notificaciones';
import { ConocimientoApi } from '../../../conocimiento/data-access/conocimiento-api';
import { DatosIntent, IntentsApi } from '../../data-access/intents-api';

/**
 * Intents: qué quiere saber el estudiante y con qué ficha se responde. Los
 * ejemplos alimentan el clasificador; agregar ejemplos basta para mejorarlo.
 */
@Component({
  selector: 'app-intents',
  templateUrl: './intents.html',
  styleUrl: './intents.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Intents {
  private readonly api = inject(IntentsApi);
  private readonly avisos = inject(Notificaciones);
  protected readonly procesos = toSignal(
    inject(ConocimientoApi)
      .procesos()
      .pipe(catchError(() => of([]))),
    {
      initialValue: [],
    },
  );
  protected readonly secciones = SECCIONES;
  protected readonly titulos = TITULOS_SECCION;

  protected readonly filtros = signal({ proceso: '', q: '', page: 1, recarga: 0 });
  private readonly respuesta = toSignal(
    toObservable(this.filtros).pipe(
      debounceTime(200),
      switchMap(({ recarga: _, ...f }) =>
        this.api.listar(f).pipe(
          map((r) => ({ intents: r.results, total: r.count })),
          catchError(() => of({ intents: [] as Intent[], total: 0 })),
          startWith(null),
        ),
      ),
    ),
    { initialValue: null },
  );
  protected readonly intents = computed(() => this.respuesta()?.intents ?? []);
  protected readonly cargando = computed(() => this.respuesta() === null);
  protected readonly total = computed(() => this.respuesta()?.total ?? 0);

  protected readonly editando = signal<Intent | null>(null);
  /** El formulario se vuelve a crear en cada apertura para no arrastrar lo escrito antes. */
  protected readonly abierto = signal(false);
  protected readonly errores = signal<Record<string, string>>({});
  private readonly dialogo = viewChild<ElementRef<HTMLDialogElement>>('dialogo');

  protected filtrar(campo: 'proceso' | 'q', evento: Event) {
    const valor = (evento.target as HTMLInputElement).value;
    this.filtros.update((f) => ({ ...f, [campo]: valor, page: 1 }));
  }

  protected abrir(intent: Intent | null) {
    this.editando.set(intent);
    this.errores.set({});
    this.abierto.set(true);
    this.dialogo()?.nativeElement.showModal();
  }

  protected cerrar() {
    this.dialogo()?.nativeElement.close();
    this.abierto.set(false);
  }

  protected ejemplosComoTexto(intent: Intent | null): string {
    return intent?.lista_ejemplos.map((e) => e.texto).join('\n') ?? '';
  }

  protected guardar(evento: SubmitEvent) {
    evento.preventDefault();
    const d = new FormData(evento.target as HTMLFormElement);
    const datos: DatosIntent = {
      proceso: Number(d.get('proceso')),
      nombre: String(d.get('nombre')).trim(),
      descripcion: String(d.get('descripcion')).trim(),
      fichas: String(d.get('fichas'))
        .split(',')
        .map((c) => c.trim())
        .filter(Boolean),
      secciones: d.getAll('secciones').map(String) as Intent['secciones'],
      si_falta_entidad: String(d.get('si_falta_entidad')).trim(),
      respuesta_fija: String(d.get('respuesta_fija')).trim(),
      activo: d.get('activo') === 'on',
      ejemplos: String(d.get('ejemplos'))
        .split('\n')
        .map((e) => e.trim())
        .filter(Boolean),
    };
    const actual = this.editando();
    const peticion = actual ? this.api.guardar(actual.id, datos) : this.api.crear(datos);
    peticion.subscribe({
      next: () => {
        this.cerrar();
        this.avisos.exito('Intent guardado. Los ejemplos se procesan en segundo plano.');
        this.filtros.update((f) => ({ ...f, recarga: f.recarga + 1 }));
      },
      error: (e) => this.errores.set(erroresDeCampo(e)),
    });
  }
}
