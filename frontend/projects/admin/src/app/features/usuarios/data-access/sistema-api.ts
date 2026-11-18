import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_URL, Configuracion, Paginado, Usuario } from 'shared';

export type DatosUsuario = Partial<Usuario> & { password?: string };

/** Cuentas del panel y configuración del asistente (solo Centro de Cómputo). */
@Injectable({ providedIn: 'root' })
export class SistemaApi {
  private readonly http = inject(HttpClient);
  private readonly api = inject(API_URL);

  usuarios() {
    return this.http.get<Paginado<Usuario>>(`${this.api}/usuarios/`);
  }

  guardarUsuario(id: number | null, datos: DatosUsuario) {
    return id
      ? this.http.patch<Usuario>(`${this.api}/usuarios/${id}/`, datos)
      : this.http.post<Usuario>(`${this.api}/usuarios/`, datos);
  }

  facultades() {
    return this.http.get<{ id: number; nombre: string }[]>(`${this.api}/facultades/`);
  }

  configuracion() {
    return this.http.get<Configuracion>(`${this.api}/configuracion/`);
  }

  guardarConfiguracion(datos: Partial<Configuracion>) {
    return this.http.patch<Configuracion>(`${this.api}/configuracion/`, datos);
  }
}
