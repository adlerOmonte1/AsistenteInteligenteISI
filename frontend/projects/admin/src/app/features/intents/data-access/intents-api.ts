import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_URL, Intent, Paginado } from 'shared';
import { parametros } from '../../../core/http/parametros';

export type DatosIntent = Partial<Omit<Intent, 'lista_ejemplos'>> & { ejemplos?: string[] };

@Injectable({ providedIn: 'root' })
export class IntentsApi {
  private readonly http = inject(HttpClient);
  private readonly api = inject(API_URL);

  listar(filtros: { proceso?: string; q?: string; page?: number }) {
    return this.http.get<Paginado<Intent>>(`${this.api}/intents/`, { params: parametros(filtros) });
  }

  crear(datos: DatosIntent) {
    return this.http.post<Intent>(`${this.api}/intents/`, datos);
  }

  guardar(id: number, datos: DatosIntent) {
    return this.http.patch<Intent>(`${this.api}/intents/${id}/`, datos);
  }
}
