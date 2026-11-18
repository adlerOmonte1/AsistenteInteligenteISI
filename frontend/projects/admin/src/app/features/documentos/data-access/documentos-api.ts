import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_URL, Documento, Paginado } from 'shared';
import { parametros } from '../../../core/http/parametros';

@Injectable({ providedIn: 'root' })
export class DocumentosApi {
  private readonly http = inject(HttpClient);
  private readonly api = inject(API_URL);

  listar(filtros: { proceso?: string; page?: number }) {
    return this.http.get<Paginado<Documento>>(`${this.api}/admin/documentos/`, {
      params: parametros(filtros),
    });
  }

  /** Multipart: el archivo es opcional si se indica un enlace externo. */
  guardar(id: number | null, datos: FormData) {
    return id
      ? this.http.patch<Documento>(`${this.api}/admin/documentos/${id}/`, datos)
      : this.http.post<Documento>(`${this.api}/admin/documentos/`, datos);
  }

  eliminar(id: number) {
    return this.http.delete<void>(`${this.api}/admin/documentos/${id}/`);
  }
}
