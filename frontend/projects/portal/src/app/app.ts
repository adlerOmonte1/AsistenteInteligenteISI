import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter, map } from 'rxjs';
import { ChatPanel, MarcaUdh } from 'shared';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ChatPanel, MarcaUdh],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  private readonly router = inject(Router);

  protected readonly menuAbierto = signal(false);
  protected readonly chatAbierto = signal(false);
  protected readonly anio = new Date().getFullYear();

  /** En /asistente la conversación ocupa la página; el botón flotante sobra. */
  protected readonly enAsistente = toSignal(
    this.router.events.pipe(
      filter((e) => e instanceof NavigationEnd),
      map((e) => (e as NavigationEnd).urlAfterRedirects.startsWith('/asistente')),
    ),
    { initialValue: false },
  );

  /** «Trámites» queda marcado también dentro de un trámite (/tramites/…). */
  protected readonly enTramites = toSignal(
    this.router.events.pipe(
      filter((e) => e instanceof NavigationEnd),
      map((e) => {
        const url = (e as NavigationEnd).urlAfterRedirects.split(/[?#]/)[0];
        return url === '/' || url.startsWith('/tramites') || url.startsWith('/buscar');
      }),
    ),
    { initialValue: true },
  );

  protected alternarMenu() {
    this.menuAbierto.update((v) => !v);
  }
}
