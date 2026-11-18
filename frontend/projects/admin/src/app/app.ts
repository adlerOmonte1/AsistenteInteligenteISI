import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Notificaciones } from './core/http/notificaciones';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  template: `
    <router-outlet />
    <div class="avisos" aria-live="polite">
      @for (n of avisos.lista(); track n.id) {
        <div class="aviso-flotante" [class]="n.tipo" role="status">
          <span>{{ n.texto }}</span>
          <button type="button" (click)="avisos.cerrar(n.id)" aria-label="Cerrar">✕</button>
        </div>
      }
    </div>
  `,
  styles: `
    .avisos {
      position: fixed;
      right: 16px;
      bottom: 16px;
      z-index: 100;
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-width: 380px;
    }
    .aviso-flotante {
      display: flex;
      gap: 10px;
      align-items: flex-start;
      padding: 12px 14px;
      border-radius: 8px;
      background: var(--udh-grafito);
      color: #fff;
      box-shadow: 0 8px 24px rgb(0 0 0 / 20%);
      font-size: 14px;
    }
    .aviso-flotante span {
      flex: 1;
    }
    .aviso-flotante.exito {
      background: var(--udh-exito);
    }
    .aviso-flotante.peligro {
      background: var(--udh-peligro);
    }
    button {
      border: 0;
      background: none;
      color: inherit;
      cursor: pointer;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  protected readonly avisos = inject(Notificaciones);
}
