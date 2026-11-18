/** Contrato de eventos SSE de POST /api/v1/chat/ (backend/apps/dialogo/views.py). */

export type Via = 'determinista' | 'desambiguacion' | 'rag' | 'derivacion' | 'aclaracion';

export interface OpcionChat {
  etiqueta: string;
  intent?: string;
  ficha?: string;
  mensaje?: string;
}

export interface FuenteFicha {
  codigo: string;
  titulo: string;
  proceso?: string;
}

export type EventoChat =
  | { tipo: 'token'; t: string }
  | { tipo: 'opciones'; opciones: OpcionChat[] }
  | { tipo: 'fuentes'; fichas: FuenteFicha[] }
  | { tipo: 'fin'; consultaId: number | null; via: Via; derivada: boolean }
  | { tipo: 'error'; mensaje: string };

export interface MensajeChat {
  id: string;
  autor: 'estudiante' | 'asistente';
  texto: string;
  opciones?: OpcionChat[];
  fuentes?: FuenteFicha[];
  consultaId?: number | null;
  via?: Via;
  util?: boolean | null;
  escribiendo?: boolean;
  error?: boolean;
}

export interface PeticionChat {
  sesion: string;
  mensaje: string;
  intent?: string;
  ficha?: string;
}

export interface ConfiguracionPublica {
  bienvenida: string;
  aviso_legal: string;
}
