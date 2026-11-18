import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Auth } from '../../../../core/auth/auth';

@Component({
  selector: 'app-login',
  templateUrl: './login.html',
  styleUrl: './login.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Login {
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);

  protected readonly enviando = signal(false);
  protected readonly error = signal('');

  protected ingresar(evento: SubmitEvent) {
    evento.preventDefault();
    const datos = new FormData(evento.target as HTMLFormElement);
    const username = String(datos.get('username') ?? '').trim();
    const password = String(datos.get('password') ?? '');
    if (!username || !password) {
      this.error.set('Ingrese su usuario y contraseña.');
      return;
    }
    this.enviando.set(true);
    this.error.set('');
    this.auth.login(username, password).subscribe({
      next: () => void this.router.navigate(['/dashboard']),
      error: (e: HttpErrorResponse) => {
        this.enviando.set(false);
        this.error.set(e.error?.detalle ?? 'No se pudo iniciar sesión. Intente nuevamente.');
      },
    });
  }
}
