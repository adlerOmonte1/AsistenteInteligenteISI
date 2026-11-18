import { HttpParams } from '@angular/common/http';

/** Construye HttpParams omitiendo los filtros vacíos. */
export function parametros(
  filtros: Record<string, string | number | boolean | null | undefined>,
): HttpParams {
  let params = new HttpParams();
  for (const [clave, valor] of Object.entries(filtros)) {
    if (valor !== '' && valor !== null && valor !== undefined)
      params = params.set(clave, String(valor));
  }
  return params;
}
