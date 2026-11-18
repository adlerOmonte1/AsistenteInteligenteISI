import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { beforeEach, describe, expect, it } from 'vitest';
import { Usuario } from 'shared';
import { Auth } from './auth';

const editor: Usuario = {
  id: 1,
  username: 'editor',
  first_name: '',
  last_name: '',
  email: '',
  rol: 'editor',
  facultad: null,
};

describe('Auth', () => {
  let auth: Auth;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    auth = TestBed.inject(Auth);
    http = TestBed.inject(HttpTestingController);
  });

  it('guarda el access en memoria al iniciar sesión', () => {
    auth.login('editor', 'clave').subscribe();
    http.expectOne('/api/v1/auth/login/').flush({ access: 'abc', usuario: editor });
    expect(auth.access()).toBe('abc');
    expect(auth.autenticado()).toBe(true);
  });

  it('compara roles por jerarquía', () => {
    auth.login('editor', 'clave').subscribe();
    http.expectOne('/api/v1/auth/login/').flush({ access: 'abc', usuario: editor });
    expect(auth.tieneRol('lector')).toBe(true);
    expect(auth.tieneRol('editor')).toBe(true);
    expect(auth.tieneRol('revisor')).toBe(false);
  });

  it('comparte una sola renovación entre peticiones simultáneas', () => {
    auth.renovar().subscribe();
    auth.renovar().subscribe();
    http.expectOne('/api/v1/auth/refresh/').flush({ access: 'nuevo', usuario: editor });
    http.verify();
    expect(auth.access()).toBe('nuevo');
  });

  it('limpia la sesión si la renovación falla', () => {
    auth.renovar().subscribe();
    http
      .expectOne('/api/v1/auth/refresh/')
      .flush({ detalle: 'expiró' }, { status: 401, statusText: 'Unauthorized' });
    expect(auth.autenticado()).toBe(false);
  });
});
