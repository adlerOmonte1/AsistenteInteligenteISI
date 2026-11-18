import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, finalize, map, of, shareReplay, tap } from 'rxjs';
import { API_URL, Rol, Sesion, Usuario } from 'shared';

const JERARQUIA: Record<Rol, number> = { lector: 1, editor: 2, revisor: 3, superadmin: 4 };

/**
 * Sesión del panel.
 *
 * El access token vive solo en memoria (este signal); nunca en localStorage.
 * El refresh viaja en una cookie HttpOnly que el navegador envía a
 * /api/v1/auth/ y que JavaScript no puede leer.
 */
@Injectable({ providedIn: 'root' })
export class Auth {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly api = inject(API_URL);

  private readonly _usuario = signal<Usuario | null>(null);
  private readonly _access = signal<string | null>(null);
  private renovando$: Observable<string | null> | null = null;

  readonly usuario = this._usuario.asReadonly();
  readonly access = this._access.asReadonly();
  readonly autenticado = computed(() => this._usuario() !== null);

  login(username: string, password: string) {
    return this.http
      .post<Sesion>(`${this.api}/auth/login/`, { username, password }, { withCredentials: true })
      .pipe(tap((s) => this.guardar(s)));
  }

  /** Renueva el access con la cookie. Varias peticiones simultáneas comparten una sola renovación. */
  renovar(): Observable<string | null> {
    this.renovando$ ??= this.http
      .post<Sesion>(`${this.api}/auth/refresh/`, {}, { withCredentials: true })
      .pipe(
        tap((s) => this.guardar(s)),
        map((s) => s.access),
        catchError(() => {
          this.limpiar();
          return of(null);
        }),
        finalize(() => (this.renovando$ = null)),
        shareReplay(1),
      );
    return this.renovando$;
  }

  /** Al cargar la app se intenta recuperar la sesión desde la cookie. */
  restaurar(): Observable<boolean> {
    return this.renovar().pipe(map((token) => token !== null));
  }

  logout() {
    this.http
      .post(`${this.api}/auth/logout/`, {}, { withCredentials: true })
      .subscribe({ error: () => undefined });
    this.limpiar();
    void this.router.navigate(['/login']);
  }

  tieneRol(minimo: Rol): boolean {
    const usuario = this._usuario();
    return !!usuario && JERARQUIA[usuario.rol] >= JERARQUIA[minimo];
  }

  private guardar(sesion: Sesion) {
    this._access.set(sesion.access);
    this._usuario.set(sesion.usuario);
  }

  private limpiar() {
    this._access.set(null);
    this._usuario.set(null);
  }
}
