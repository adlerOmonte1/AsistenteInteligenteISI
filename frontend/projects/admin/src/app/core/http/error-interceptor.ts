import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { ErrorApi } from 'shared';
import { Notificaciones } from './notificaciones';

/**
 * Muestra el `detalle` de los errores que no son de validación. Los 400 los
 * maneja cada formulario, que muestra `errores` junto a cada campo.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const avisos = inject(Notificaciones);
  return next(req).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse && error.status !== 400 && error.status !== 401) {
        const cuerpo = error.error as Partial<ErrorApi> | null;
        avisos.error(
          cuerpo?.detalle ??
            (error.status === 0
              ? 'No hay conexión con el servidor.'
              : error.status === 403
                ? 'No tiene permiso para esta acción.'
                : 'Ocurrió un error inesperado.'),
        );
      }
      return throwError(() => error);
    }),
  );
};

/** Convierte un error de la API en un mapa campo → mensaje para los formularios. */
export function erroresDeCampo(error: unknown): Record<string, string> {
  if (!(error instanceof HttpErrorResponse) || error.status !== 400) return {};
  const errores = (error.error as Partial<ErrorApi> | null)?.errores ?? {};
  return Object.fromEntries(
    Object.entries(errores).map(([campo, valor]) => [
      campo,
      Array.isArray(valor) ? valor.join(' ') : String(valor),
    ]),
  );
}
