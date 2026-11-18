import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { Auth } from './auth';

const conToken = (req: HttpRequest<unknown>, token: string | null) =>
  token ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;

/** Agrega el Bearer y, ante un 401, renueva el token una sola vez y reintenta. */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(Auth);
  if (req.url.includes('/auth/')) return next(req);

  return next(conToken(req, auth.access())).pipe(
    catchError((error: unknown) => {
      if (!(error instanceof HttpErrorResponse) || error.status !== 401)
        return throwError(() => error);
      return auth.renovar().pipe(
        switchMap((token) => {
          if (!token) {
            auth.logout();
            return throwError(() => error);
          }
          return next(conToken(req, token));
        }),
      );
    }),
  );
};
