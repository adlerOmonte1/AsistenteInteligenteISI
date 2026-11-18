import { DecimalPipe, JsonPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { MarkdownPipe, NOMBRES_VIA, RespuestaProbador } from 'shared';
import { CalidadApi } from '../../../calidad/data-access/calidad-api';

/**
 * Prueba una pregunta como si fuera un estudiante y muestra cómo se resolvió:
 * intent, confianza, vía, fichas y la traza completa. No se registra en métricas.
 */
@Component({
  selector: 'app-probador',
  imports: [MarkdownPipe, DecimalPipe, JsonPipe],
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Probador</h1>
        <p>
          Pruebe preguntas y vea por qué el asistente respondió así. Las pruebas no cuentan en las
          métricas.
        </p>
      </div>
    </header>

    <form class="tarjeta pregunta" (submit)="probar($event)">
      <input
        type="text"
        name="mensaje"
        maxlength="500"
        placeholder="¿A qué correo envío el plan de prácticas?"
        required
      />
      <label class="fila tenue"
        ><input type="checkbox" name="continuar" [checked]="!!sesion()" /> Continuar la
        conversación</label
      >
      <button class="boton" type="submit" [disabled]="cargando()">
        {{ cargando() ? 'Probando…' : 'Probar' }}
      </button>
    </form>

    @for (r of historial(); track $index) {
      <article class="tarjeta resultado">
        <p class="mensaje"><strong>Pregunta:</strong> {{ r.pregunta }}</p>
        <div class="fila">
          <span class="insignia info">{{ nombresVia[r.respuesta.via] ?? r.respuesta.via }}</span>
          <span class="insignia">{{ r.respuesta.intent || 'sin intent' }}</span>
          <span class="insignia">confianza {{ r.respuesta.confianza | number: '1.2-2' }}</span>
          @for (f of r.respuesta.fichas; track f.codigo) {
            <span class="insignia exito mono" [title]="f.titulo">{{ f.codigo }}</span>
          }
          @if (r.respuesta.motivo) {
            <span class="insignia alerta">{{ r.respuesta.motivo }}</span>
          }
          @if (r.respuesta.validacion_fallida) {
            <span class="insignia peligro"
              >validación fallida: {{ r.respuesta.no_respaldados.join(', ') }}</span
            >
          }
        </div>
        <div class="respuesta contenido-markdown" [innerHTML]="r.respuesta.texto | markdown"></div>
        @if (r.respuesta.opciones.length) {
          <p class="tenue">Opciones ofrecidas: {{ etiquetas(r.respuesta) }}</p>
        }
        <details>
          <summary>Traza</summary>
          <pre>{{ r.respuesta.traza | json }}</pre>
        </details>
      </article>
    }
  `,
  styles: `
    .pregunta {
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 12px;
      align-items: center;
      margin-bottom: 16px;
    }
    .resultado {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 12px;
    }
    .mensaje {
      margin: 0;
    }
    .respuesta {
      padding: 12px;
      background: var(--udh-superficie-alterna);
      border-radius: 8px;
    }
    pre {
      font-size: 12px;
      overflow-x: auto;
      background: #0f1d2e;
      color: #d6e2f0;
      padding: 12px;
      border-radius: 8px;
    }
    @media (max-width: 760px) {
      .pregunta {
        grid-template-columns: 1fr;
      }
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Probador {
  private readonly api = inject(CalidadApi);
  protected readonly nombresVia = NOMBRES_VIA;
  protected readonly cargando = signal(false);
  protected readonly sesion = signal<string | undefined>(undefined);
  protected readonly historial = signal<{ pregunta: string; respuesta: RespuestaProbador }[]>([]);

  protected probar(evento: SubmitEvent) {
    evento.preventDefault();
    const formulario = evento.target as HTMLFormElement;
    const datos = new FormData(formulario);
    const mensaje = String(datos.get('mensaje') ?? '').trim();
    if (!mensaje) return;
    const sesion = datos.get('continuar') === 'on' ? this.sesion() : undefined;
    this.cargando.set(true);
    this.api.probar(mensaje, sesion).subscribe({
      next: (respuesta) => {
        this.cargando.set(false);
        this.sesion.set(respuesta.sesion);
        this.historial.update((h) => [{ pregunta: mensaje, respuesta }, ...h].slice(0, 20));
        (formulario.elements.namedItem('mensaje') as HTMLInputElement).value = '';
      },
      error: () => this.cargando.set(false),
    });
  }

  protected etiquetas(r: RespuestaProbador): string {
    return r.opciones.map((o) => o.etiqueta).join(' · ');
  }
}
