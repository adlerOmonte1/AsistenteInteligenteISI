import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  ViewEncapsulation,
  inject,
  input,
  signal,
} from '@angular/core';
import { API_URL, ChatPanel, MarcaUdh } from 'shared';

/**
 * Elemento <udh-chat>: botón flotante que abre la conversación.
 *
 *   <script src="https://<dominio>/widget/main.js" defer></script>
 *   <udh-chat api="https://<dominio>/api/v1"></udh-chat>
 *
 * Usa Shadow DOM: sus estilos no afectan a la página que lo inserta ni al revés.
 */
@Component({
  selector: 'udh-chat-widget',
  imports: [ChatPanel, MarcaUdh],
  templateUrl: './chat-widget.html',
  styleUrl: './chat-widget.scss',
  encapsulation: ViewEncapsulation.ShadowDom,
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: API_URL,
      useFactory: () => {
        const host = inject(ElementRef).nativeElement as HTMLElement;
        return (host.getAttribute('api') || '/api/v1').replace(/\/$/, '');
      },
    },
  ],
})
export class ChatWidget {
  /** Texto del encabezado. */
  readonly titulo = input('Asistente Académico');
  /** Subtítulo del encabezado. */
  readonly subtitulo = input('P.A. Ingeniería de Sistemas e Informática');
  /** "abierto" para mostrar la conversación al cargar. */
  readonly estado = input<string>('cerrado');

  /** El logotipo se sirve junto a main.js, en el dominio del asistente, no en el de la página. */
  protected readonly logo = new URL('marca/logo-udh.png', import.meta.url).href;
  protected readonly abierto = signal(false);
  protected readonly usado = signal(false);

  constructor() {
    queueMicrotask(() => {
      if (this.estado() === 'abierto') this.abrir();
    });
  }

  protected abrir() {
    this.abierto.set(true);
    this.usado.set(true);
  }

  protected cerrar() {
    this.abierto.set(false);
  }

  protected alPresionarTecla(evento: KeyboardEvent) {
    if (evento.key === 'Escape') this.cerrar();
  }
}
