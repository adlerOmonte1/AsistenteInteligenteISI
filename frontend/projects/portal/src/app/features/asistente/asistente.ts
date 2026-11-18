import { ChangeDetectionStrategy, Component } from '@angular/core';
import { ChatPanel } from 'shared';

@Component({
  selector: 'app-asistente',
  imports: [ChatPanel],
  template: `
    <div class="contenedor marco">
      <aside>
        <h1>Asistente Académico</h1>
        <p class="tenue">
          Pregunte por requisitos, pasos, pagos, plazos o a dónde enviar sus documentos. Las
          respuestas citan la ficha del trámite de la que provienen.
        </p>
        <div class="aviso">
          <strong>Recuerde</strong>
          <ul>
            <li>No escriba su DNI, código ni datos personales.</li>
            <li>Si un dato figura como «por confirmar», consúltelo con la Coordinación.</li>
            <li>La comunicación oficial de la Coordinación prevalece sobre este asistente.</li>
          </ul>
        </div>
      </aside>
      <udh-chat-panel class="tarjeta conversacion" />
    </div>
  `,
  styles: `
    .marco {
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 24px;
      padding-top: 24px;
      height: calc(100vh - 64px - 24px);
      min-height: 520px;
    }
    .conversacion {
      padding: 0;
      overflow: hidden;
      display: flex;
    }
    ul {
      margin: 6px 0 0;
      padding-left: 18px;
      font-size: 14px;
    }
    @media (max-width: 860px) {
      .marco {
        grid-template-columns: 1fr;
        height: auto;
      }
      aside .aviso {
        display: none;
      }
      .conversacion {
        height: calc(100vh - 220px);
      }
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Asistente {}
