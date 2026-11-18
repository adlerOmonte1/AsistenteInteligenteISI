const CLAVE = 'udh-asistente-sesion';

/**
 * Identificador anónimo de la conversación. Vive en sessionStorage: se pierde al
 * cerrar la pestaña y no contiene datos de la persona.
 */
export function obtenerSesion(): string {
  try {
    const existente = sessionStorage.getItem(CLAVE);
    if (existente) return existente;
    const nueva = crypto.randomUUID();
    sessionStorage.setItem(CLAVE, nueva);
    return nueva;
  } catch {
    return crypto.randomUUID();
  }
}

export function reiniciarSesion(): string {
  try {
    sessionStorage.removeItem(CLAVE);
  } catch {
    /* almacenamiento no disponible */
  }
  return obtenerSesion();
}
