import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';
import { Rol } from 'shared';
import { Auth } from './auth';

/** Exige sesión; si no la hay en memoria, intenta recuperarla desde la cookie. */
export const authGuard: CanActivateFn = () => {
  const auth = inject(Auth);
  const router = inject(Router);
  if (auth.autenticado()) return true;
  return auth.restaurar().pipe(map((ok) => ok || router.createUrlTree(['/login'])));
};

/**
 * Exige un rol mínimo, leído de `route.data.rol`. Es experiencia de usuario:
 * los permisos reales se validan siempre en el backend.
 */
export const rolGuard: CanActivateFn = (route) => {
  const auth = inject(Auth);
  const router = inject(Router);
  const minimo = route.data['rol'] as Rol | undefined;
  return !minimo || auth.tieneRol(minimo) || router.createUrlTree(['/dashboard']);
};

/** Evita mostrar el login a quien ya tiene sesión. */
export const invitadoGuard: CanActivateFn = () => {
  const auth = inject(Auth);
  const router = inject(Router);
  if (auth.autenticado()) return router.createUrlTree(['/dashboard']);
  return auth.restaurar().pipe(map((ok) => (ok ? router.createUrlTree(['/dashboard']) : true)));
};
