import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  inject,
  input,
  signal,
  viewChild,
} from '@angular/core';
import { API_URL } from '../api/api-url';
import { ConfiguracionPublica, MensajeChat, OpcionChat, PeticionChat } from '../models/chat.model';
import { MarkdownPipe } from '../utils/markdown';
import { ChatStream } from './chat-stream';
import { obtenerSesion, reiniciarSesion } from './session';

const BIENVENIDA_POR_DEFECTO =
  'Buen día. Soy el Asistente Académico del P.A. de Ingeniería de Sistemas e Informática. ¿En qué trámite le ayudo?';

let contador = 0;
const nuevoId = () => `m${Date.now()}-${contador++}`;

/**
 * Conversación con el asistente: lista de mensajes, opciones, fuentes,
 * calificación y caja de texto. La usan el widget <udh-chat> y la página
 * /asistente del portal; el encabezado lo pone quien la contiene (ng-content).
 */
@Component({
  selector: 'udh-chat-panel',
  imports: [MarkdownPipe],
  providers: [ChatStream],
  templateUrl: './chat-panel.html',
  styleUrl: './chat-panel.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPanel implements OnInit, OnDestroy {
  private readonly stream = inject(ChatStream);
  private readonly api = inject(API_URL);

  /** Sugerencias que se muestran antes del primer mensaje. */
  readonly sugerencias = input<string[]>([
    '¿Cuántas horas son las prácticas preprofesionales?',
    '¿Qué necesito para el grado de bachiller?',
    '¿Cuáles son las fases del título por tesis?',
  ]);

  protected readonly mensajes = signal<MensajeChat[]>([]);
  protected readonly enviando = signal(false);
  protected readonly avisoLegal = signal('');
  protected readonly texto = signal('');
  protected readonly maximo = 500;

  private sesion = obtenerSesion();
  private abortar?: AbortController;
  private readonly lista = viewChild<ElementRef<HTMLElement>>('lista');
  private readonly entrada = viewChild<ElementRef<HTMLTextAreaElement>>('entrada');

  async ngOnInit() {
    let bienvenida = BIENVENIDA_POR_DEFECTO;
    try {
      const r = await fetch(`${this.api}/configuracion/publica/`);
      if (r.ok) {
        const cfg = (await r.json()) as ConfiguracionPublica;
        bienvenida = cfg.bienvenida || bienvenida;
        this.avisoLegal.set(cfg.aviso_legal);
      }
    } catch {
      /* sin conexión: se usa el texto por defecto */
    }
    this.mensajes.set([{ id: nuevoId(), autor: 'asistente', texto: bienvenida }]);
  }

  ngOnDestroy() {
    this.abortar?.abort();
  }

  protected alEscribir(evento: Event) {
    this.texto.set((evento.target as HTMLTextAreaElement).value);
  }

  protected alPresionarTecla(evento: KeyboardEvent) {
    if (evento.key === 'Enter' && !evento.shiftKey) {
      evento.preventDefault();
      this.enviarTexto();
    }
  }

  protected enviarTexto() {
    const mensaje = this.texto().trim();
    if (!mensaje || this.enviando()) return;
    this.texto.set('');
    const caja = this.entrada()?.nativeElement;
    if (caja) caja.value = '';
    void this.enviar({ sesion: this.sesion, mensaje });
  }

  protected elegirOpcion(opcion: OpcionChat) {
    if (this.enviando()) return;
    void this.enviar({
      sesion: this.sesion,
      mensaje: opcion.mensaje ?? opcion.etiqueta,
      intent: opcion.intent,
      ficha: opcion.ficha,
    });
  }

  protected async calificar(mensaje: MensajeChat, util: boolean) {
    if (!mensaje.consultaId || mensaje.util != null) return;
    this.actualizar(mensaje.id, { util });
    try {
      await this.stream.calificar(mensaje.consultaId, this.sesion, util);
    } catch {
      /* la calificación es opcional */
    }
  }

  protected reiniciar() {
    this.abortar?.abort();
    this.sesion = reiniciarSesion();
    this.enviando.set(false);
    this.mensajes.update((lista) => lista.slice(0, 1));
  }

  private async enviar(peticion: PeticionChat) {
    this.enviando.set(true);
    const respuestaId = nuevoId();
    this.mensajes.update((lista) => [
      ...lista.map((m) => ({ ...m, opciones: undefined })),
      { id: nuevoId(), autor: 'estudiante', texto: peticion.mensaje },
      { id: respuestaId, autor: 'asistente', texto: '', escribiendo: true },
    ]);
    this.desplazar();

    this.abortar = new AbortController();
    try {
      for await (const evento of this.stream.enviar(peticion, this.abortar.signal)) {
        switch (evento.tipo) {
          case 'token':
            this.actualizar(respuestaId, (m) => ({ texto: m.texto + evento.t }));
            break;
          case 'opciones':
            this.actualizar(respuestaId, { opciones: evento.opciones });
            break;
          case 'fuentes':
            this.actualizar(respuestaId, { fuentes: evento.fichas });
            break;
          case 'fin':
            this.actualizar(respuestaId, {
              consultaId: evento.consultaId,
              via: evento.via,
              escribiendo: false,
            });
            break;
          case 'error':
            this.actualizar(respuestaId, {
              texto: evento.mensaje,
              error: true,
              escribiendo: false,
            });
            break;
        }
        this.desplazar();
      }
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        this.actualizar(respuestaId, {
          texto: 'No se pudo conectar con el asistente. Revise su conexión e intente de nuevo.',
          error: true,
        });
      }
    } finally {
      this.actualizar(respuestaId, { escribiendo: false });
      this.enviando.set(false);
      queueMicrotask(() => this.entrada()?.nativeElement.focus());
    }
  }

  private actualizar(
    id: string,
    cambios: Partial<MensajeChat> | ((m: MensajeChat) => Partial<MensajeChat>),
  ) {
    this.mensajes.update((lista) =>
      lista.map((m) =>
        m.id === id ? { ...m, ...(typeof cambios === 'function' ? cambios(m) : cambios) } : m,
      ),
    );
  }

  private desplazar() {
    requestAnimationFrame(() => {
      const el = this.lista()?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    });
  }
}
