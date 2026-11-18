import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';
import { CargaDocumento } from 'shared';
import { Notificaciones } from '../../../../core/http/notificaciones';
import { ConocimientoApi } from '../../data-access/conocimiento-api';

/**
 * Sube un reglamento o resolución (.docx/.pdf) para que el sistema proponga
 * fichas en borrador. Las propuestas se revisan como cualquier otra ficha.
 */
@Component({
  selector: 'app-cargas',
  imports: [RouterLink, DatePipe],
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Subir documento</h1>
        <p>
          El sistema lee el documento y propone fichas en borrador. Nada se publica sin revisión.
        </p>
      </div>
    </header>

    <form class="tarjeta formulario" (submit)="subir($event)">
      <label class="campo">
        <span>Proceso</span>
        <select name="proceso" required>
          @for (p of procesos(); track p.id) {
            <option [value]="p.id">{{ p.nombre }}</option>
          }
        </select>
      </label>
      <label class="campo">
        <span>Documento (.docx o .pdf, máximo 10 MB)</span>
        <input type="file" name="archivo" accept=".pdf,.docx" required />
      </label>
      <button class="boton" type="submit" [disabled]="subiendo()">
        {{ subiendo() ? 'Subiendo…' : 'Subir y proponer fichas' }}
      </button>
    </form>

    <h2>Cargas recientes</h2>
    <div class="pila">
      @for (c of cargas(); track c.id) {
        <div class="tarjeta">
          <div class="fila">
            <strong>{{ c.nombre_original }}</strong>
            <span
              class="insignia"
              [class.exito]="c.estado === 'completada'"
              [class.peligro]="c.estado === 'error'"
              [class.alerta]="c.estado === 'procesando'"
            >
              {{ c.estado }}
            </span>
            <span class="espaciador"></span>
            <small class="tenue">{{ c.creada | date: 'dd/MM/yyyy HH:mm' }}</small>
          </div>
          @if (c.mensaje) {
            <p class="tenue">{{ c.mensaje }}</p>
          }
          @for (f of c.fichas_propuestas; track f.id) {
            <a [routerLink]="['/fichas', f.id]" class="mono">{{ f.codigo }}</a> · {{ f.titulo
            }}<br />
          }
        </div>
      } @empty {
        <p class="tenue">Aún no se ha subido ningún documento.</p>
      }
    </div>
  `,
  styles: `
    .formulario {
      display: grid;
      grid-template-columns: 1fr 1.4fr auto;
      gap: 12px;
      align-items: end;
      margin-bottom: 24px;
    }
    @media (max-width: 860px) {
      .formulario {
        grid-template-columns: 1fr;
      }
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Cargas implements OnDestroy {
  private readonly api = inject(ConocimientoApi);
  private readonly avisos = inject(Notificaciones);
  private sondeo?: ReturnType<typeof setInterval>;

  protected readonly procesos = toSignal(this.api.procesos().pipe(catchError(() => of([]))), {
    initialValue: [],
  });
  protected readonly cargas = signal<CargaDocumento[]>([]);
  protected readonly subiendo = signal(false);

  constructor() {
    this.refrescar();
  }

  ngOnDestroy() {
    clearInterval(this.sondeo);
  }

  protected subir(evento: SubmitEvent) {
    evento.preventDefault();
    const formulario = evento.target as HTMLFormElement;
    const datos = new FormData(formulario);
    const archivo = datos.get('archivo') as File | null;
    if (!archivo?.size) return;
    if (archivo.size > 10 * 1024 * 1024) {
      this.avisos.error('El archivo supera los 10 MB.');
      return;
    }
    this.subiendo.set(true);
    this.api.subir(Number(datos.get('proceso')), archivo).subscribe({
      next: () => {
        this.subiendo.set(false);
        formulario.reset();
        this.avisos.info('Documento recibido. Las fichas propuestas aparecerán en unos segundos.');
        this.refrescar();
      },
      error: () => this.subiendo.set(false),
    });
  }

  private refrescar() {
    this.api.cargas().subscribe((r) => {
      this.cargas.set(r.results);
      clearInterval(this.sondeo);
      if (r.results.some((c) => c.estado === 'procesando'))
        this.sondeo = setInterval(() => this.refrescar(), 4000);
    });
  }
}
