import { DatePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, of } from 'rxjs';
import { NOMBRES_ROL, Rol, Usuario } from 'shared';
import { erroresDeCampo } from '../../../../core/http/error-interceptor';
import { Notificaciones } from '../../../../core/http/notificaciones';
import { DatosUsuario, SistemaApi } from '../../data-access/sistema-api';

/** Cuentas del panel. No hay registro público: solo el Centro de Cómputo crea cuentas. */
@Component({
  selector: 'app-usuarios',
  imports: [DatePipe],
  template: `
    <header class="pagina-cabecera">
      <div>
        <h1>Usuarios</h1>
        <p>
          Las cuentas no se eliminan: se desactivan, para conservar el historial de quién publicó
          cada cambio.
        </p>
      </div>
      <button class="boton" type="button" (click)="abrir(null)">Nueva cuenta</button>
    </header>

    <div class="tabla-contenedor">
      <table class="tabla">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Nombre</th>
            <th>Rol</th>
            <th>Facultad</th>
            <th>Último ingreso</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          @for (u of usuarios(); track u.id) {
            <tr>
              <td class="mono">{{ u.username }}</td>
              <td>{{ u.first_name }} {{ u.last_name }}</td>
              <td>{{ roles[u.rol] }}</td>
              <td class="tenue">{{ nombreFacultad(u.facultad) }}</td>
              <td class="tenue">
                {{ u.last_login ? (u.last_login | date: 'dd/MM/yyyy HH:mm') : 'Nunca' }}
              </td>
              <td>
                <span class="insignia" [class.exito]="u.is_active">{{
                  u.is_active ? 'Activa' : 'Desactivada'
                }}</span>
              </td>
              <td>
                <button class="boton secundario chico" type="button" (click)="abrir(u)">
                  Editar
                </button>
              </td>
            </tr>
          }
        </tbody>
      </table>
    </div>

    <dialog class="modal" #dialogo>
      @if (abierto()) {
        @let u = editando();
        <form (submit)="guardar($event)">
          <h2>{{ u ? 'Editar ' + u.username : 'Nueva cuenta' }}</h2>
          <div class="rejilla-formulario">
            <label class="campo"
              ><span>Usuario</span
              ><input type="text" name="username" [value]="u?.username ?? ''" required />
              @if (errores()['username']) {
                <small class="error">{{ errores()['username'] }}</small>
              }
            </label>
            <label class="campo"
              ><span>Correo institucional</span
              ><input type="email" name="email" [value]="u?.email ?? ''"
            /></label>
            <label class="campo"
              ><span>Nombres</span
              ><input type="text" name="first_name" [value]="u?.first_name ?? ''"
            /></label>
            <label class="campo"
              ><span>Apellidos</span
              ><input type="text" name="last_name" [value]="u?.last_name ?? ''"
            /></label>
            <label class="campo">
              <span>Rol</span>
              <select name="rol">
                @for (r of listaRoles; track r[0]) {
                  <option [value]="r[0]" [selected]="r[0] === (u?.rol ?? 'editor')">
                    {{ r[1] }}
                  </option>
                }
              </select>
            </label>
            <label class="campo">
              <span>Facultad</span>
              <select name="facultad">
                <option value="">Todas</option>
                @for (f of facultades(); track f.id) {
                  <option [value]="f.id" [selected]="f.id === u?.facultad">{{ f.nombre }}</option>
                }
              </select>
            </label>
          </div>
          <label class="campo">
            <span>{{ u ? 'Nueva contraseña (opcional)' : 'Contraseña' }}</span>
            <input type="password" name="password" autocomplete="new-password" [required]="!u" />
            @if (errores()['password']) {
              <small class="error">{{ errores()['password'] }}</small>
            } @else {
              <small class="ayuda"
                >Mínimo 10 caracteres; no puede ser solo números ni parecida al usuario.</small
              >
            }
          </label>
          <label class="fila"
            ><input type="checkbox" name="is_active" [checked]="u?.is_active ?? true" /> Cuenta
            activa</label
          >
          <div class="acciones">
            <button class="boton secundario" type="button" (click)="cerrar()">Cancelar</button>
            <button class="boton" type="submit">Guardar</button>
          </div>
        </form>
      }
    </dialog>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Usuarios {
  private readonly api = inject(SistemaApi);
  private readonly avisos = inject(Notificaciones);
  protected readonly roles = NOMBRES_ROL;
  protected readonly listaRoles = Object.entries(NOMBRES_ROL) as [Rol, string][];
  protected readonly facultades = toSignal(this.api.facultades().pipe(catchError(() => of([]))), {
    initialValue: [],
  });
  protected readonly usuarios = signal<Usuario[]>([]);
  protected readonly editando = signal<Usuario | null>(null);
  protected readonly abierto = signal(false);
  protected readonly errores = signal<Record<string, string>>({});
  private readonly dialogo = viewChild<ElementRef<HTMLDialogElement>>('dialogo');

  constructor() {
    this.cargar();
  }

  protected nombreFacultad(id: number | null): string {
    return id === null ? 'Todas' : (this.facultades().find((f) => f.id === id)?.nombre ?? '—');
  }

  protected abrir(usuario: Usuario | null) {
    this.editando.set(usuario);
    this.errores.set({});
    this.abierto.set(true);
    this.dialogo()?.nativeElement.showModal();
  }

  protected cerrar() {
    this.dialogo()?.nativeElement.close();
    this.abierto.set(false);
  }

  protected guardar(evento: SubmitEvent) {
    evento.preventDefault();
    const d = new FormData(evento.target as HTMLFormElement);
    const datos: DatosUsuario = {
      username: String(d.get('username')).trim(),
      email: String(d.get('email')).trim(),
      first_name: String(d.get('first_name')).trim(),
      last_name: String(d.get('last_name')).trim(),
      rol: String(d.get('rol')) as Rol,
      facultad: d.get('facultad') ? Number(d.get('facultad')) : null,
      is_active: d.get('is_active') === 'on',
    };
    const password = String(d.get('password') ?? '');
    if (password) datos.password = password;
    this.api.guardarUsuario(this.editando()?.id ?? null, datos).subscribe({
      next: () => {
        this.cerrar();
        this.avisos.exito('Cuenta guardada.');
        this.cargar();
      },
      error: (e) => this.errores.set(erroresDeCampo(e)),
    });
  }

  private cargar() {
    this.api.usuarios().subscribe((r) => this.usuarios.set(r.results));
  }
}
