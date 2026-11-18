import { InjectionToken } from '@angular/core';

/**
 * URL base de la API, p. ej. `/api/v1` o `https://asistente.udh.edu.pe/api/v1`.
 * Cada aplicación la provee en su app.config.ts; el widget la toma del atributo `api`.
 */
export const API_URL = new InjectionToken<string>('API_URL', { factory: () => '/api/v1' });
