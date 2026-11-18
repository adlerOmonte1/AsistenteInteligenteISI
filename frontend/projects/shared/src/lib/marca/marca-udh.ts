import { ChangeDetectionStrategy, Component, input, signal } from '@angular/core';

/**
 * Logotipo oficial de la Universidad de Huánuco.
 *
 * Usa el archivo publicado por la universidad (assets/marca/logo-udh.png). No se
 * redibuja ni se aproxima: si el archivo no está, se muestra el nombre en texto.
 * El logotipo tiene letras grafito, así que solo se coloca sobre fondo claro.
 */
@Component({
  selector: 'udh-marca',
  template: `
    @if (!fallo()) {
      <img
        [src]="src()"
        alt="Universidad de Huánuco"
        [style.height.px]="alto()"
        (error)="fallo.set(true)"
        decoding="async"
      />
    } @else {
      <span class="nombre" [style.font-size.px]="alto() * 0.42">Universidad de Huánuco</span>
    }
  `,
  styles: `
    :host {
      display: inline-flex;
      align-items: center;
    }
    img {
      display: block;
      width: auto;
    }
    .nombre {
      font-weight: 700;
      color: #2b2b2b;
      white-space: nowrap;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MarcaUdh {
  /** Ruta del archivo; el widget la pasa absoluta porque se inserta en otros dominios. */
  readonly src = input('marca/logo-udh.png');
  /** Alto en píxeles; el ancho se ajusta solo. */
  readonly alto = input(40);

  protected readonly fallo = signal(false);
}
