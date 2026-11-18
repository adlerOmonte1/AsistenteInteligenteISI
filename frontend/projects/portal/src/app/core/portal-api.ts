import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_URL, DetalleProceso, Documento, Paginado, Proceso, ResultadoBusqueda } from 'shared';

/** Endpoints públicos que consume el portal (sin login). */
@Injectable({ providedIn: 'root' })
export class PortalApi {
  private readonly http = inject(HttpClient);
  private readonly api = inject(API_URL);

  procesos() {
    return this.http.get<Proceso[]>(`${this.api}/procesos/`);
  }

  proceso(clave: string) {
    return this.http.get<DetalleProceso>(`${this.api}/procesos/${clave}/`);
  }

  documentos(filtros: { proceso?: string; tipo?: string; q?: string; page?: number } = {}) {
    let params = new HttpParams();
    for (const [clave, valor] of Object.entries(filtros)) {
      if (valor) params = params.set(clave, String(valor));
    }
    return this.http.get<Paginado<Documento>>(`${this.api}/documentos/`, { params });
  }

  buscar(q: string) {
    return this.http.get<{ resultados: ResultadoBusqueda[] }>(`${this.api}/buscar/`, {
      params: { q },
    });
  }
}
