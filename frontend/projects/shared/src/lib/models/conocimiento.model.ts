/** Modelos de la base de conocimiento, espejo de backend/apps/conocimiento/serializers.py. */

export const SECCIONES = [
  'requisitos',
  'pasos',
  'pago',
  'plazo',
  'enviar_a',
  'siguiente_fase',
] as const;
export type Seccion = (typeof SECCIONES)[number];

export const TITULOS_SECCION: Record<Seccion | 'informacion_adicional', string> = {
  requisitos: 'Requisitos',
  pasos: 'Pasos',
  pago: 'Pago',
  plazo: 'Plazo',
  enviar_a: 'Enviar a',
  siguiente_fase: 'Siguiente fase',
  informacion_adicional: 'Información adicional',
};

export type EstadoDato = 'confirmado' | 'pendiente';
export type EstadoRevision = 'borrador' | 'en_revision' | 'publicada' | 'rechazada';

export interface Proceso {
  id: number;
  programa: number;
  programa_nombre: string;
  clave: string;
  nombre: string;
  descripcion: string;
  prefijos: string[];
  orden: number;
  activo: boolean;
  visible_en_portal: boolean;
  total_fichas?: number;
  fichas_publicadas?: number;
}

/** Contenido inmutable de una versión publicada (VersionFicha.contenido). */
export interface ContenidoFicha extends Record<Seccion, string> {
  codigo: string;
  proceso: string;
  fase: number;
  titulo: string;
  fuente: string;
  vigencia: string;
  estado_dato: EstadoDato;
  informacion_adicional: string;
  palabras_clave: string[];
}

export interface FichaPublicada {
  codigo: string;
  version: number;
  publicada_en: string;
  contenido: ContenidoFicha;
}

export type TipoDocumento =
  'resolucion' | 'reglamento' | 'formato' | 'flujograma' | 'guia' | 'otro';

export const TIPOS_DOCUMENTO: Record<TipoDocumento, string> = {
  resolucion: 'Resolución',
  reglamento: 'Reglamento',
  formato: 'Formato o anexo',
  flujograma: 'Flujograma',
  guia: 'Guía',
  otro: 'Otro',
};

export interface Documento {
  id: number;
  proceso: number | null;
  proceso_clave: string | null;
  proceso_nombre: string | null;
  titulo: string;
  tipo: TipoDocumento;
  numero: string;
  fecha_emision: string | null;
  descripcion: string;
  url_externa: string;
  url: string | null;
  publico: boolean;
  creado: string;
}

export interface DetalleProceso {
  proceso: Proceso;
  fichas: FichaPublicada[];
  documentos: Documento[];
}

export interface ResultadoBusqueda {
  codigo: string;
  titulo: string;
  proceso: string;
  proceso_nombre: string;
  fragmento: string;
}

export interface Paginado<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
