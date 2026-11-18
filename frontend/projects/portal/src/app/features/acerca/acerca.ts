import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-acerca',
  imports: [RouterLink],
  template: `
    <article class="contenedor texto">
      <h1>Acerca del Asistente Académico</h1>
      <p>
        El Asistente Académico orienta a los estudiantes del Programa Académico de Ingeniería de
        Sistemas e Informática sobre sus trámites: prácticas preprofesionales, convalidación de
        prácticas por experiencia laboral, grado de bachiller, título por tesis, título por trabajo
        de suficiencia profesional y traslados.
      </p>

      <h2>De dónde sale la información</h2>
      <p>
        Cada trámite está descrito en <strong>fichas</strong>: una por fase, con sus requisitos,
        pasos, pago, plazo, a dónde enviar los documentos y la fase siguiente. Las fichas se
        elaboraron a partir de los reglamentos, resoluciones y flujogramas oficiales, y la
        Coordinación del programa revisa y aprueba cada cambio antes de publicarlo.
      </p>

      <h2>Cómo responde</h2>
      <ul>
        <li>
          Las preguntas frecuentes se responden directamente con la ficha que corresponde, sin
          interpretación.
        </li>
        <li>
          Las preguntas abiertas se responden con un modelo de lenguaje que solo puede usar el texto
          de las fichas y debe citar su código.
        </li>
        <li>
          Antes de mostrar una respuesta, el sistema verifica que cada correo, monto, plazo o
          resolución que menciona exista en las fichas citadas. Si no es así, la respuesta se
          descarta y se le deriva a la Coordinación.
        </li>
      </ul>

      <h2>Privacidad</h2>
      <p>
        No necesita registrarse. Las conversaciones se guardan de forma anónima, sin nombre, DNI ni
        código, solo para mejorar el servicio, y se eliminan a los doce meses, conforme a la Ley N.°
        29733 de Protección de Datos Personales.
      </p>

      <p><a class="boton" routerLink="/asistente">Conversar con el asistente</a></p>
    </article>
  `,
  styles: `
    :host {
      display: block;
      padding-top: 28px;
    }
    .texto {
      max-width: 780px;
    }
    h2 {
      margin-top: 28px;
    }
    li {
      margin-bottom: 6px;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Acerca {}
