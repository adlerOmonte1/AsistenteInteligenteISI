import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import {
  API_URL,
  CargaDocumento,
  Ficha,
  FichaResumen,
  Paginado,
  Proceso,
  VersionFicha,
} from 'shared';
import { parametros } from '../../../core/http/parametros';

export interface FiltrosFichas {
  proceso?: string;
  estado?: string;
  publicacion?: string;
  q?: string;
  page?: number;
}

@Injectable({ providedIn: 'root' })
export class ConocimientoApi {
  private readonly http = inject(HttpClient);
  private readonly api = inject(API_URL);

  procesos() {
    return this.http.get<Proceso[]>(`${this.api}/admin/procesos/`);
  }

  fichas(filtros: FiltrosFichas = {}) {
    return this.http.get<Paginado<FichaResumen>>(`${this.api}/fichas/`, {
      params: parametros({ ...filtros }),
    });
  }

  ficha(id: number) {
    return this.http.get<Ficha>(`${this.api}/fichas/${id}/`);
  }

  crear(datos: Partial<Ficha>) {
    return this.http.post<Ficha>(`${this.api}/fichas/`, datos);
  }

  guardar(id: number, datos: Partial<Ficha>) {
    return this.http.patch<Ficha>(`${this.api}/fichas/${id}/`, datos);
  }

  enviarARevision(id: number) {
    return this.http.post<Ficha>(`${this.api}/fichas/${id}/enviar-revision/`, {});
  }

  aprobar(id: number, observaciones = '') {
    return this.http.post<Ficha>(`${this.api}/fichas/${id}/aprobar/`, { observaciones });
  }

  rechazar(id: number, observaciones: string) {
    return this.http.post<Ficha>(`${this.api}/fichas/${id}/rechazar/`, { observaciones });
  }

  revertir(id: number, numero: number) {
    return this.http.post<Ficha>(`${this.api}/fichas/${id}/revertir/`, { numero });
  }

  historial(id: number) {
    return this.http.get<VersionFicha[]>(`${this.api}/fichas/${id}/historial/`);
  }

  cargas() {
    return this.http.get<Paginado<CargaDocumento>>(`${this.api}/cargas/`);
  }

  subir(proceso: number, archivo: File) {
    const datos = new FormData();
    datos.append('proceso', String(proceso));
    datos.append('archivo', archivo);
    return this.http.post<CargaDocumento>(`${this.api}/cargas/`, datos);
  }
}
