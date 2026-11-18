/** Modelos del panel de administración, espejo de los serializers del backend. */

import { ContenidoFicha, EstadoDato, EstadoRevision, Seccion } from './conocimiento.model';

export type Rol = 'superadmin' | 'revisor' | 'editor' | 'lector';

export const NOMBRES_ROL: Record<Rol, string> = {
  superadmin: 'Centro de Cómputo',
  revisor: 'Revisor',
  editor: 'Editor',
  lector: 'Lector',
};

export interface Usuario {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  rol: Rol;
  facultad: number | null;
  facultad_nombre?: string | null;
  is_active?: boolean;
  last_login?: string | null;
}

export interface Sesion {
  access: string;
  usuario: Usuario;
}

export interface ErrorApi {
  detalle: string;
  errores: Record<string, string[] | string>;
}

export interface FichaResumen {
  id: number;
  codigo: string;
  proceso: number;
  proceso_clave: string;
  proceso_nombre: string;
  fase: number;
  titulo: string;
  estado_dato: EstadoDato;
  estado_revision: EstadoRevision;
  version: number | null;
  actualizada: string;
  actualizada_por: string | null;
}

export interface Ficha extends Record<Seccion, string> {
  id: number;
  proceso: number;
  proceso_clave: string;
  proceso_nombre: string;
  codigo: string;
  fase: number;
  titulo: string;
  fuente: string;
  vigencia: string | null;
  vigencia_texto: string;
  estado_dato: EstadoDato;
  informacion_adicional: string;
  palabras_clave: string[];
  estado_revision: EstadoRevision;
  observaciones: string;
  version: number | null;
  tiene_cambios_sin_publicar: boolean;
  reemplazada_por: number | null;
  creada: string;
  actualizada: string;
  actualizada_por: string | null;
}

export interface VersionFicha {
  id: number;
  numero: number;
  contenido: ContenidoFicha;
  nota: string;
  publicada_en: string;
  publicada_por: string | null;
}

export interface Intent {
  id: number;
  proceso: number;
  proceso_clave: string;
  nombre: string;
  descripcion: string;
  fichas: string[];
  secciones: Seccion[];
  entidades: unknown[];
  si_falta_entidad: string;
  respuesta_fija: string;
  activo: boolean;
  lista_ejemplos: { id: number; texto: string }[];
  actualizado: string;
}

export interface Pendiente {
  id: number;
  proceso: number;
  proceso_clave: string;
  codigo: string;
  descripcion: string;
  pregunta: string;
  fichas: string[];
  resuelto: boolean;
  resolucion: string;
  resuelto_en: string | null;
  creado: string;
}

export interface CargaDocumento {
  id: number;
  proceso: number;
  nombre_original: string;
  estado: 'procesando' | 'completada' | 'error';
  mensaje: string;
  fichas_propuestas: FichaResumen[];
  creada: string;
}

export interface MetricasEvaluacion {
  casos: number;
  exactitud_intent: number | null;
  exactitud_ficha: number | null;
  clave_contenida: number | null;
  datos_inventados: number;
  por_via: Record<string, number>;
  cumple: Record<string, boolean>;
  cumple_todas: boolean;
}

export interface Evaluacion {
  id: number;
  proceso: string | null;
  proceso_nombre: string | null;
  estado: 'pendiente' | 'ejecutando' | 'completada' | 'error';
  motivo: 'manual' | 'revision' | 'humo';
  limite_casos: number | null;
  metricas: MetricasEvaluacion | Record<string, never>;
  mensaje: string;
  creada: string;
  finalizada: string | null;
  resultados?: ResultadoCaso[];
}

export interface ResultadoCaso {
  id: number;
  codigo: string;
  pregunta: string;
  intent_esperado: string;
  ficha_esperada: string;
  respuesta_clave: string;
  intent_obtenido: string;
  confianza: number;
  fichas_obtenidas: string[];
  via: string;
  respuesta: string;
  acierto_intent: boolean | null;
  acierto_ficha: boolean | null;
  clave_contenida: boolean | null;
  dato_inventado: boolean;
}

export interface Consulta {
  id: number;
  sesion: string;
  proceso_nombre: string | null;
  pregunta: string;
  respuesta: string;
  intent: string;
  confianza: number;
  via: string;
  fichas_citadas: string[];
  derivada: boolean;
  validacion_fallida: boolean;
  datos_no_respaldados: string[];
  motivo: string;
  tokens_entrada: number;
  tokens_salida: number;
  costo_usd: string;
  latencia_ms: number;
  util: boolean | null;
  creada: string;
}

export interface ResumenMetricas {
  desde: string;
  hasta: string;
  total: number;
  sesiones: number;
  por_via: Record<string, number>;
  porcentaje_por_via: Record<string, number>;
  porcentaje_derivadas: number;
  porcentaje_utiles: number;
  calificadas: number;
  fallas_validacion: number;
  costo_periodo_usd: number;
  costo_mes_usd: number;
  latencia_promedio_ms: number;
  por_dia: { fecha: string; consultas: number }[];
  top_intents: { intent: string; n: number }[];
  por_proceso: { proceso: string; consultas: number }[];
}

export interface RespuestaProbador {
  sesion: string;
  texto: string;
  via: string;
  intent: string;
  confianza: number;
  fichas: { codigo: string; titulo: string }[];
  opciones: { etiqueta: string }[];
  derivada: boolean;
  motivo: string;
  validacion_fallida: boolean;
  no_respaldados: string[];
  traza: Record<string, unknown>;
}

export interface Configuracion {
  umbral_determinista: number;
  umbral_desambiguacion: number;
  intentos_antes_de_derivar: number;
  limite_usd_mes: string;
  llm_habilitado: boolean;
  mensaje_bienvenida: string;
  contacto_derivacion: string;
  aviso_legal: string;
  actualizado: string;
  proveedor_llm: string;
  modelo_llm: string;
  proveedor_embeddings: string;
}

export const ESTADOS_REVISION: Record<EstadoRevision, { texto: string; clase: string }> = {
  borrador: { texto: 'Borrador', clase: '' },
  en_revision: { texto: 'En revisión', clase: 'alerta' },
  publicada: { texto: 'Publicada', clase: 'exito' },
  rechazada: { texto: 'Rechazada', clase: 'peligro' },
};

export const NOMBRES_VIA: Record<string, string> = {
  determinista: 'Determinista',
  desambiguacion: 'Desambiguación',
  rag: 'RAG',
  derivacion: 'Derivación',
  aclaracion: 'Aclaración',
};
