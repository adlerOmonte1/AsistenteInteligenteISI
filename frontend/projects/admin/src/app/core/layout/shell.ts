import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MarcaUdh, NOMBRES_ROL, Rol } from 'shared';
import { Auth } from '../auth/auth';

interface ItemMenu {
  ruta: string;
  texto: string;
  rol: Rol;
  grupo: 'Conocimiento' | 'Calidad' | 'Sistema' | '';
}

const MENU: ItemMenu[] = [
  { ruta: '/dashboard', texto: 'Resumen', rol: 'lector', grupo: '' },
  { ruta: '/fichas', texto: 'Fichas', rol: 'lector', grupo: 'Conocimiento' },
  { ruta: '/revision', texto: 'Bandeja de revisión', rol: 'revisor', grupo: 'Conocimiento' },
  { ruta: '/intents', texto: 'Intents', rol: 'editor', grupo: 'Conocimiento' },
  { ruta: '/pendientes', texto: 'Pendientes', rol: 'editor', grupo: 'Conocimiento' },
  { ruta: '/documentos', texto: 'Documentos', rol: 'editor', grupo: 'Conocimiento' },
  { ruta: '/cargas', texto: 'Subir documento', rol: 'editor', grupo: 'Conocimiento' },
  { ruta: '/probador', texto: 'Probador', rol: 'editor', grupo: 'Calidad' },
  { ruta: '/evaluacion', texto: 'Golden set', rol: 'editor', grupo: 'Calidad' },
  { ruta: '/conversaciones', texto: 'Conversaciones', rol: 'lector', grupo: 'Calidad' },
  { ruta: '/usuarios', texto: 'Usuarios', rol: 'superadmin', grupo: 'Sistema' },
  { ruta: '/configuracion', texto: 'Configuración', rol: 'superadmin', grupo: 'Sistema' },
];

@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, MarcaUdh],
  templateUrl: './shell.html',
  styleUrl: './shell.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Shell {
  protected readonly auth = inject(Auth);
  protected readonly nombresRol = NOMBRES_ROL;
  protected readonly menuAbierto = signal(false);

  protected readonly grupos = computed(() => {
    const visibles = MENU.filter((item) => this.auth.tieneRol(item.rol));
    const orden = ['', 'Conocimiento', 'Calidad', 'Sistema'] as const;
    return orden
      .map((grupo) => ({ grupo, items: visibles.filter((i) => i.grupo === grupo) }))
      .filter((g) => g.items.length);
  });
}
