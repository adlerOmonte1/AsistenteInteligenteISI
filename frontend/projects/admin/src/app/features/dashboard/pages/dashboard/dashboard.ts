import { CurrencyPipe, DecimalPipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';
import { NOMBRES_VIA, ResumenMetricas } from 'shared';
import { CalidadApi } from '../../../calidad/data-access/calidad-api';

const ORDEN_VIAS = ['determinista', 'aclaracion', 'desambiguacion', 'rag', 'derivacion'];

/** Resumen de los últimos 30 días: volumen, vías, derivaciones, utilidad y costo. */
@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, DecimalPipe, CurrencyPipe, PercentPipe],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Dashboard {
  protected readonly nombresVia = NOMBRES_VIA;
  protected readonly resumen = toSignal<ResumenMetricas | null | undefined>(
    inject(CalidadApi)
      .resumen()
      .pipe(catchError(() => of(null))),
  );

  protected readonly vias = computed(() => {
    const r = this.resumen();
    if (!r) return [];
    return ORDEN_VIAS.map((via) => ({
      via,
      n: r.por_via[via] ?? 0,
      pct: r.porcentaje_por_via[via] ?? 0,
    }));
  });

  protected readonly maximoDia = computed(() =>
    Math.max(1, ...(this.resumen()?.por_dia.map((d) => d.consultas) ?? [])),
  );
  protected readonly maximoProceso = computed(() =>
    Math.max(1, ...(this.resumen()?.por_proceso.map((p) => p.consultas) ?? [])),
  );
}
