import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import {
  API_URL,
  Consulta,
  Evaluacion,
  Paginado,
  RespuestaProbador,
  ResumenMetricas,
} from 'shared';
import { parametros } from '../../../core/http/parametros';

/** Endpoints de calidad: métricas, probador, golden set y conversaciones. */
@Injectable({ providedIn: 'root' })
export class CalidadApi {
  private readonly http = inject(HttpClient);
  private readonly api = inject(API_URL);

  resumen(desde?: string, hasta?: string) {
    return this.http.get<ResumenMetricas>(`${this.api}/metricas/resumen/`, {
      params: parametros({ desde, hasta }),
    });
  }

  probar(mensaje: string, sesion?: string) {
    return this.http.post<RespuestaProbador>(`${this.api}/probador/`, { mensaje, sesion });
  }

  evaluaciones(page = 1) {
    return this.http.get<Paginado<Evaluacion>>(`${this.api}/evaluaciones/`, {
      params: parametros({ page }),
    });
  }

  evaluacion(id: number) {
    return this.http.get<Evaluacion>(`${this.api}/evaluaciones/${id}/`);
  }

  evaluar(proceso: string | null) {
    return this.http.post<Evaluacion>(`${this.api}/evaluaciones/`, { proceso });
  }

  conversaciones(filtros: Record<string, string | number>) {
    return this.http.get<Paginado<Consulta>>(`${this.api}/conversaciones/`, {
      params: parametros(filtros),
    });
  }
}
