import { describe, expect, it } from 'vitest';
import { interpretarBloque } from './chat-stream';

describe('interpretarBloque', () => {
  it('convierte un bloque SSE en un evento tipado', () => {
    expect(interpretarBloque('event: token\ndata: {"t": "Hola"}')).toEqual({
      tipo: 'token',
      t: 'Hola',
    });
  });

  it('lee el evento de fin con su consulta', () => {
    const evento = interpretarBloque(
      'event: fin\ndata: {"consultaId": 7, "via": "rag", "derivada": false}',
    );
    expect(evento).toEqual({ tipo: 'fin', consultaId: 7, via: 'rag', derivada: false });
  });

  it('ignora bloques incompletos o con JSON inválido', () => {
    expect(interpretarBloque('event: token')).toBeNull();
    expect(interpretarBloque('event: token\ndata: {roto')).toBeNull();
  });
});
