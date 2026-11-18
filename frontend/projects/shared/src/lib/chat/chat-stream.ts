import { Injectable, inject } from '@angular/core';
import { API_URL } from '../api/api-url';
import { EventoChat, PeticionChat } from '../models/chat.model';

/**
 * Cliente del canal SSE del chat.
 *
 * Se usa fetch + ReadableStream porque EventSource solo admite GET y el chat
 * envía el mensaje por POST.
 */
// Se provee en ChatPanel para que tome el API_URL del elemento que lo contiene (widget).
@Injectable()
export class ChatStream {
  private readonly api = inject(API_URL);

  async *enviar(peticion: PeticionChat, senal?: AbortSignal): AsyncGenerator<EventoChat> {
    const respuesta = await fetch(`${this.api}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
      body: JSON.stringify(peticion),
      signal: senal,
    });

    if (!respuesta.ok || !respuesta.body) {
      yield { tipo: 'error', mensaje: await mensajeDeError(respuesta) };
      return;
    }

    const lector = respuesta.body.pipeThrough(new TextDecoderStream()).getReader();
    let pendiente = '';
    while (true) {
      const { value, done } = await lector.read();
      if (done) break;
      pendiente += value;
      let corte = pendiente.indexOf('\n\n');
      while (corte !== -1) {
        const evento = interpretarBloque(pendiente.slice(0, corte));
        pendiente = pendiente.slice(corte + 2);
        if (evento) yield evento;
        corte = pendiente.indexOf('\n\n');
      }
    }
  }

  async calificar(consultaId: number, sesion: string, util: boolean): Promise<void> {
    await fetch(`${this.api}/chat/${consultaId}/feedback/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sesion, util }),
    });
  }
}

export function interpretarBloque(bloque: string): EventoChat | null {
  let tipo = '';
  let datos = '';
  for (const linea of bloque.split('\n')) {
    if (linea.startsWith('event:')) tipo = linea.slice(6).trim();
    else if (linea.startsWith('data:')) datos += linea.slice(5).trim();
  }
  if (!tipo || !datos) return null;
  try {
    return { tipo, ...JSON.parse(datos) } as EventoChat;
  } catch {
    return null;
  }
}

async function mensajeDeError(respuesta: Response): Promise<string> {
  if (respuesta.status === 429) {
    return 'Ha enviado muchos mensajes seguidos. Espere unos minutos e intente de nuevo.';
  }
  try {
    const cuerpo = await respuesta.json();
    if (cuerpo?.detalle) return cuerpo.detalle;
  } catch {
    /* respuesta sin JSON */
  }
  return 'El servicio no está disponible en este momento. Intente nuevamente en unos minutos.';
}
