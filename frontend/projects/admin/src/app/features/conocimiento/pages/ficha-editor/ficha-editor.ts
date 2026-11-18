import { DatePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  computed,
  effect,
  inject,
  input,
  signal,
  viewChild,
} from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Observable, catchError, of } from 'rxjs';
import { ESTADOS_REVISION, Ficha, SECCIONES, TITULOS_SECCION, VersionFicha } from 'shared';
import { Auth } from '../../../../core/auth/auth';
import { erroresDeCampo } from '../../../../core/http/error-interceptor';
import { Notificaciones } from '../../../../core/http/notificaciones';
import { ConocimientoApi } from '../../data-access/conocimiento-api';

const AYUDA_SECCION: Record<string, string> = {
  requisitos: 'Una línea por requisito, empezando con «- ».',
  pasos: 'Pasos numerados: «1. …», «2. …».',
  pago: 'Monto exacto (S/ 0.00), concepto y dónde se paga, o «No indicado».',
  plazo: 'Plazo exacto según la norma, o «No indicado».',
  enviar_a: 'Correo institucional u oficina, o «No aplica (…)».',
  siguiente_fase: 'Código de la siguiente ficha (p. ej. BAC_P03) o «Fin del proceso».',
};

/**
 * Editor de ficha: metadatos, las seis secciones del contrato y el ciclo de
 * revisión. Guardar deja la ficha en borrador; el asistente sigue respondiendo
 * con la versión publicada hasta que un revisor apruebe el cambio.
 */
@Component({
  selector: 'app-ficha-editor',
  imports: [ReactiveFormsModule, RouterLink, DatePipe],
  templateUrl: './ficha-editor.html',
  styleUrl: './ficha-editor.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FichaEditor {
  private readonly api = inject(ConocimientoApi);
  private readonly router = inject(Router);
  private readonly avisos = inject(Notificaciones);
  private readonly fb = inject(FormBuilder).nonNullable;
  protected readonly auth = inject(Auth);

  /** Parámetro :id; ausente en /fichas/nueva. */
  readonly id = input<string>();

  protected readonly secciones = SECCIONES;
  protected readonly titulos = TITULOS_SECCION;
  protected readonly ayuda = AYUDA_SECCION;
  protected readonly estados = ESTADOS_REVISION;

  protected readonly ficha = signal<Ficha | null>(null);
  protected readonly historial = signal<VersionFicha[]>([]);
  protected readonly errores = signal<Record<string, string>>({});
  protected readonly ocupado = signal(false);
  protected readonly procesos = toSignal(this.api.procesos().pipe(catchError(() => of([]))), {
    initialValue: [],
  });

  private readonly dialogoRechazo = viewChild<ElementRef<HTMLDialogElement>>('dialogoRechazo');

  protected readonly form = this.fb.group({
    proceso: [0, Validators.required],
    codigo: ['', [Validators.required, Validators.pattern(/^[A-Z]{3}_([A-Z]{3}_)?[A-Z]\d{2}$/)]],
    fase: [0, [Validators.required, Validators.min(0)]],
    titulo: ['', Validators.required],
    fuente: ['', Validators.required],
    vigencia: [''],
    vigencia_texto: ['no indicada'],
    estado_dato: ['pendiente' as 'pendiente' | 'confirmado'],
    requisitos: [''],
    pasos: [''],
    pago: [''],
    plazo: [''],
    enviar_a: [''],
    siguiente_fase: [''],
    informacion_adicional: [''],
  });

  protected readonly esNueva = computed(() => !this.id());
  protected readonly puedeEditar = computed(() => {
    const f = this.ficha();
    return this.auth.tieneRol('editor') && (!f || f.estado_revision !== 'en_revision');
  });
  protected readonly puedeEnviar = computed(() => {
    const f = this.ficha();
    return (
      !!f &&
      this.auth.tieneRol('editor') &&
      (f.estado_revision === 'borrador' || f.estado_revision === 'rechazada')
    );
  });
  protected readonly puedeRevisar = computed(
    () => this.ficha()?.estado_revision === 'en_revision' && this.auth.tieneRol('revisor'),
  );

  constructor() {
    effect(() => {
      const id = this.id();
      if (id) this.cargar(Number(id));
    });
    effect(() => {
      if (this.puedeEditar()) this.form.enable({ emitEvent: false });
      else this.form.disable({ emitEvent: false });
      if (!this.esNueva()) this.form.controls.proceso.disable({ emitEvent: false });
    });
  }

  private cargar(id: number) {
    this.api.ficha(id).subscribe((f) => this.mostrar(f));
    this.api.historial(id).subscribe((h) => this.historial.set(h));
  }

  private mostrar(f: Ficha) {
    this.ficha.set(f);
    this.form.reset({
      ...f,
      vigencia: f.vigencia ?? '',
      vigencia_texto: f.vigencia_texto || 'no indicada',
    });
    this.errores.set({});
  }

  protected guardar() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.avisos.error('Revise los campos marcados.');
      return;
    }
    const valores = this.form.getRawValue();
    const datos: Partial<Ficha> = { ...valores, vigencia: valores.vigencia || null };
    const actual = this.ficha();
    this.ejecutar(actual ? this.api.guardar(actual.id, datos) : this.api.crear(datos), (f) => {
      this.avisos.exito('Borrador guardado. El asistente sigue usando la versión publicada.');
      if (!actual) void this.router.navigate(['/fichas', f.id]);
    });
  }

  protected enviarARevision() {
    const f = this.ficha();
    if (!f) return;
    if (this.form.dirty) {
      this.avisos.error('Guarde los cambios antes de enviar a revisión.');
      return;
    }
    this.ejecutar(this.api.enviarARevision(f.id), () =>
      this.avisos.exito('Ficha enviada a revisión.'),
    );
  }

  protected aprobar() {
    const f = this.ficha();
    if (!f) return;
    this.ejecutar(this.api.aprobar(f.id), () => {
      this.avisos.exito('Ficha publicada. El índice se actualiza en segundo plano.');
      this.api.historial(f.id).subscribe((h) => this.historial.set(h));
    });
  }

  protected abrirRechazo() {
    this.dialogoRechazo()?.nativeElement.showModal();
  }

  protected rechazar(evento: SubmitEvent) {
    evento.preventDefault();
    const f = this.ficha();
    const observaciones = String(
      new FormData(evento.target as HTMLFormElement).get('observaciones') ?? '',
    ).trim();
    if (!f || !observaciones) return;
    this.dialogoRechazo()?.nativeElement.close();
    this.ejecutar(this.api.rechazar(f.id, observaciones), () =>
      this.avisos.info('Ficha devuelta al editor.'),
    );
  }

  protected revertir(version: VersionFicha) {
    const f = this.ficha();
    if (!f || !confirm(`¿Publicar de nuevo el contenido de la versión ${version.numero}?`)) return;
    this.ejecutar(this.api.revertir(f.id, version.numero), () => {
      this.avisos.exito(`Se publicó el contenido de la versión ${version.numero}.`);
      this.api.historial(f.id).subscribe((h) => this.historial.set(h));
    });
  }

  protected invalido(campo: string): boolean {
    const control = this.form.get(campo);
    return !!this.errores()[campo] || (!!control && control.invalid && control.touched);
  }

  private ejecutar(peticion: Observable<Ficha>, alTerminar: (f: Ficha) => void) {
    this.ocupado.set(true);
    peticion.subscribe({
      next: (f) => {
        this.ocupado.set(false);
        this.mostrar(f);
        alTerminar(f);
      },
      error: (e) => {
        this.ocupado.set(false);
        const errores = erroresDeCampo(e);
        this.errores.set(errores);
        if (Object.keys(errores).length)
          this.avisos.error('La ficha no cumple el contrato; revise los campos marcados.');
      },
    });
  }
}
