import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Configuracion } from 'shared';
import { erroresDeCampo } from '../../../../core/http/error-interceptor';
import { Notificaciones } from '../../../../core/http/notificaciones';
import { SistemaApi } from '../../../usuarios/data-access/sistema-api';

/**
 * Parámetros del asistente que se ajustan sin redesplegar. El proveedor y el
 * modelo del LLM se cambian en las variables de entorno del servidor.
 */
@Component({
  selector: 'app-configuracion',
  imports: [DatePipe],
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Configuración</h1>
        <p>Los umbrales iniciales se calibran con el golden set antes de cambiarlos.</p>
      </div>
    </header>

    @if (cfg(); as c) {
      <form class="pila" (submit)="guardar($event)">
        <section class="tarjeta pila">
          <h2>Modelo de lenguaje</h2>
          <p class="tenue">
            Proveedor <strong>{{ c.proveedor_llm }}</strong> · modelo
            <strong>{{ c.modelo_llm }}</strong> · embeddings
            <strong>{{ c.proveedor_embeddings }}</strong>. Se cambian en el archivo
            <code>.env</code> del servidor.
          </p>
          <label class="fila"
            ><input type="checkbox" name="llm_habilitado" [checked]="c.llm_habilitado" /> Usar el
            LLM en la vía RAG</label
          >
          <label class="campo">
            <span>Límite de gasto mensual (USD)</span>
            <input
              type="number"
              step="0.5"
              min="0"
              name="limite_usd_mes"
              [value]="c.limite_usd_mes"
            />
            <small class="ayuda"
              >Al alcanzarlo, la vía RAG responde copiando las secciones de las fichas, sin llamar
              al modelo.</small
            >
          </label>
        </section>

        <section class="tarjeta">
          <h2>Enrutamiento</h2>
          <div class="rejilla-formulario">
            <label class="campo">
              <span>Umbral vía determinista</span>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                name="umbral_determinista"
                [value]="c.umbral_determinista"
              />
            </label>
            <label class="campo">
              <span>Umbral desambiguación</span>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                name="umbral_desambiguacion"
                [value]="c.umbral_desambiguacion"
              />
              @if (errores()['umbral_desambiguacion']) {
                <small class="error">{{ errores()['umbral_desambiguacion'] }}</small>
              }
            </label>
            <label class="campo">
              <span>Intentos fallidos antes de derivar</span>
              <input
                type="number"
                min="1"
                max="5"
                name="intentos_antes_de_derivar"
                [value]="c.intentos_antes_de_derivar"
              />
            </label>
          </div>
        </section>

        <section class="tarjeta pila">
          <h2>Textos del asistente</h2>
          <label class="campo"
            ><span>Mensaje de bienvenida</span
            ><textarea name="mensaje_bienvenida" rows="3" [value]="c.mensaje_bienvenida"></textarea>
          </label>
          <label class="campo">
            <span>Contacto al derivar</span>
            <textarea
              name="contacto_derivacion"
              rows="3"
              [value]="c.contacto_derivacion"
            ></textarea>
            <small class="ayuda"
              >Solo datos oficiales y confirmados: correo, teléfono u oficina de
              Coordinación.</small
            >
          </label>
          <label class="campo"
            ><span>Aviso legal</span
            ><textarea name="aviso_legal" rows="2" [value]="c.aviso_legal"></textarea>
          </label>
        </section>

        <div class="fila">
          <span class="tenue"
            >Última modificación: {{ c.actualizado | date: 'dd/MM/yyyy HH:mm' }}</span
          >
          <span class="espaciador"></span>
          <button class="boton" type="submit">Guardar configuración</button>
        </div>
      </form>
    } @else {
      <p class="tenue">Cargando…</p>
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfiguracionPagina {
  private readonly api = inject(SistemaApi);
  private readonly avisos = inject(Notificaciones);
  protected readonly cfg = signal<Configuracion | null>(null);
  protected readonly errores = signal<Record<string, string>>({});

  constructor() {
    this.api.configuracion().subscribe((c) => this.cfg.set(c));
  }

  protected guardar(evento: SubmitEvent) {
    evento.preventDefault();
    const d = new FormData(evento.target as HTMLFormElement);
    const datos: Partial<Configuracion> = {
      llm_habilitado: d.get('llm_habilitado') === 'on',
      limite_usd_mes: String(d.get('limite_usd_mes')),
      umbral_determinista: Number(d.get('umbral_determinista')),
      umbral_desambiguacion: Number(d.get('umbral_desambiguacion')),
      intentos_antes_de_derivar: Number(d.get('intentos_antes_de_derivar')),
      mensaje_bienvenida: String(d.get('mensaje_bienvenida')),
      contacto_derivacion: String(d.get('contacto_derivacion')),
      aviso_legal: String(d.get('aviso_legal')),
    };
    this.api.guardarConfiguracion(datos).subscribe({
      next: (c) => {
        this.cfg.set(c);
        this.errores.set({});
        this.avisos.exito('Configuración guardada.');
      },
      error: (e) => this.errores.set(erroresDeCampo(e)),
    });
  }
}
