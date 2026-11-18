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
import { catchError, map, of, startWith, switchMap } from 'rxjs';
import { Documento, TIPOS_DOCUMENTO, TipoDocumento } from 'shared';
import { erroresDeCampo } from '../../../../core/http/error-interceptor';
import { Notificaciones } from '../../../../core/http/notificaciones';
import { ConocimientoApi } from '../../../conocimiento/data-access/conocimiento-api';
import { DocumentosApi } from '../../data-access/documentos-api';

/** Biblioteca normativa que se publica en el portal. */
@Component({
  selector: 'app-documentos-panel',
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Documentos del portal</h1>
        <p>
          Resoluciones, reglamentos, formatos y guías que los estudiantes descargan desde el portal.
        </p>
      </div>
      <button class="boton" type="button" (click)="abrir(null)">Agregar documento</button>
    </header>

    <div class="tabla-contenedor">
      <table class="tabla">
        <thead>
          <tr>
            <th>Título</th>
            <th>Tipo</th>
            <th>Número</th>
            <th>Proceso</th>
            <th>Visible</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          @for (d of documentos(); track d.id) {
            <tr>
              <td>
                @if (d.url) {
                  <a [href]="d.url" target="_blank" rel="noopener">{{ d.titulo }}</a>
                } @else {
                  {{ d.titulo }}
                }
              </td>
              <td>{{ tipos[d.tipo] }}</td>
              <td class="tenue">{{ d.numero || '—' }}</td>
              <td class="tenue">{{ d.proceso_nombre ?? 'General' }}</td>
              <td>
                <span class="insignia" [class.exito]="d.publico">{{
                  d.publico ? 'Público' : 'Oculto'
                }}</span>
              </td>
              <td class="fila">
                <button class="boton secundario chico" type="button" (click)="abrir(d)">
                  Editar
                </button>
                <button class="boton peligro chico" type="button" (click)="eliminar(d)">
                  Quitar
                </button>
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="6" class="vacio">
                {{ cargando() ? 'Cargando…' : 'Aún no hay documentos.' }}
              </td>
            </tr>
          }
        </tbody>
      </table>
    </div>

    <dialog class="modal" #dialogo>
      @if (abierto()) {
        @let d = editando();
        <form (submit)="guardar($event)">
          <h2>{{ d ? 'Editar documento' : 'Agregar documento' }}</h2>
          <label class="campo">
            <span>Título</span>
            <input type="text" name="titulo" [value]="d?.titulo ?? ''" required />
          </label>
          <div class="rejilla-formulario">
            <label class="campo">
              <span>Tipo</span>
              <select name="tipo">
                @for (t of listaTipos; track t[0]) {
                  <option [value]="t[0]" [selected]="t[0] === d?.tipo">{{ t[1] }}</option>
                }
              </select>
            </label>
            <label class="campo">
              <span>Proceso</span>
              <select name="proceso">
                <option value="">General</option>
                @for (p of procesos(); track p.id) {
                  <option [value]="p.id" [selected]="p.id === d?.proceso">{{ p.nombre }}</option>
                }
              </select>
            </label>
            <label class="campo">
              <span>Número</span>
              <input
                type="text"
                name="numero"
                [value]="d?.numero ?? ''"
                placeholder="Res. N.° 2367-2025-R-CU-UDH"
              />
            </label>
            <label class="campo">
              <span>Fecha de emisión</span>
              <input type="date" name="fecha_emision" [value]="d?.fecha_emision ?? ''" />
            </label>
          </div>
          <label class="campo">
            <span>Descripción</span>
            <textarea name="descripcion" rows="2" [value]="d?.descripcion ?? ''"></textarea>
          </label>
          <label class="campo">
            <span
              >Archivo (.pdf o .docx){{ d ? ' — déjelo vacío para conservar el actual' : '' }}</span
            >
            <input type="file" name="archivo" accept=".pdf,.docx" />
            @if (errores()['archivo']) {
              <small class="error">{{ errores()['archivo'] }}</small>
            }
          </label>
          <label class="campo">
            <span>…o enlace externo</span>
            <input
              type="text"
              name="url_externa"
              [value]="d?.url_externa ?? ''"
              placeholder="https://"
            />
          </label>
          <label class="fila"
            ><input type="checkbox" name="publico" [checked]="d?.publico ?? true" /> Visible en el
            portal</label
          >
          <div class="acciones">
            <button class="boton secundario" type="button" (click)="cerrar()">Cancelar</button>
            <button class="boton" type="submit">Guardar</button>
          </div>
        </form>
      }
    </dialog>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Documentos {
  private readonly api = inject(DocumentosApi);
  private readonly avisos = inject(Notificaciones);
  protected readonly procesos = toSignal(
    inject(ConocimientoApi)
      .procesos()
      .pipe(catchError(() => of([]))),
    {
      initialValue: [],
    },
  );
  protected readonly tipos = TIPOS_DOCUMENTO;
  protected readonly listaTipos = Object.entries(TIPOS_DOCUMENTO) as [TipoDocumento, string][];

  private readonly recarga = signal(0);
  private readonly respuesta = toSignal(
    toObservable(this.recarga).pipe(
      switchMap(() =>
        this.api.listar({}).pipe(
          map((r) => r.results),
          catchError(() => of([] as Documento[])),
          startWith(null),
        ),
      ),
    ),
    { initialValue: null },
  );
  protected readonly documentos = computed(() => this.respuesta() ?? []);
  protected readonly cargando = computed(() => this.respuesta() === null);

  protected readonly editando = signal<Documento | null>(null);
  protected readonly abierto = signal(false);
  protected readonly errores = signal<Record<string, string>>({});
  private readonly dialogo = viewChild<ElementRef<HTMLDialogElement>>('dialogo');

  protected abrir(documento: Documento | null) {
    this.editando.set(documento);
    this.errores.set({});
    this.abierto.set(true);
    this.dialogo()?.nativeElement.showModal();
  }

  protected cerrar() {
    this.dialogo()?.nativeElement.close();
    this.abierto.set(false);
  }

  protected guardar(evento: SubmitEvent) {
    evento.preventDefault();
    const datos = new FormData(evento.target as HTMLFormElement);
    datos.set('publico', datos.get('publico') === 'on' ? 'true' : 'false');
    const archivo = datos.get('archivo') as File | null;
    if (!archivo?.size) datos.delete('archivo');
    if (!datos.get('fecha_emision')) datos.delete('fecha_emision');
    this.api.guardar(this.editando()?.id ?? null, datos).subscribe({
      next: () => {
        this.cerrar();
        this.avisos.exito('Documento guardado.');
        this.recarga.update((n) => n + 1);
      },
      error: (e) => this.errores.set(erroresDeCampo(e)),
    });
  }

  protected eliminar(documento: Documento) {
    if (!confirm(`¿Quitar «${documento.titulo}» del portal?`)) return;
    this.api.eliminar(documento.id).subscribe(() => {
      this.avisos.exito('Documento quitado.');
      this.recarga.update((n) => n + 1);
    });
  }
}
