import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_URL, Paginado, Pendiente } from 'shared';
import { parametros } from '../../../core/http/parametros';

@Injectable({ providedIn: 'root' })
export class PendientesApi {
  private readonly http = inject(HttpClient);
  private readonly api = inject(API_URL);

  listar(filtros: { proceso?: string; resuelto?: string; page?: number }) {
    return this.http.get<Paginado<Pendiente>>(`${this.api}/pendientes/`, {
      params: parametros(filtros),
    });
  }

  resolver(id: number, resuelto: boolean, resolucion: string) {
    return this.http.patch<Pendiente>(`${this.api}/pendientes/${id}/`, { resuelto, resolucion });
  }
}
