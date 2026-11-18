import { Injectable, signal } from '@angular/core';

export interface Notificacion {
  id: number;
  tipo: 'exito' | 'peligro' | 'info';
  texto: string;
}

/** Avisos breves en la esquina del panel. */
@Injectable({ providedIn: 'root' })
export class Notificaciones {
  private siguiente = 0;
  readonly lista = signal<Notificacion[]>([]);

  exito(texto: string) {
    this.mostrar('exito', texto);
  }

  error(texto: string) {
    this.mostrar('peligro', texto, 7000);
  }

  info(texto: string) {
    this.mostrar('info', texto);
  }

  cerrar(id: number) {
    this.lista.update((l) => l.filter((n) => n.id !== id));
  }

  private mostrar(tipo: Notificacion['tipo'], texto: string, ms = 4000) {
    const id = this.siguiente++;
    this.lista.update((l) => [...l, { id, tipo, texto }]);
    setTimeout(() => this.cerrar(id), ms);
  }
}
