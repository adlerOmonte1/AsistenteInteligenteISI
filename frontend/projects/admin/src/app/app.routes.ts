import { Routes } from '@angular/router';
import { authGuard, invitadoGuard, rolGuard } from './core/auth/guards';
import { Shell } from './core/layout/shell';

/** Cada ruta declara el rol mínimo en `data.rol`; el backend vuelve a validar el permiso. */
export const routes: Routes = [
  {
    path: 'login',
    title: 'Ingresar · Panel UDH',
    canActivate: [invitadoGuard],
    loadComponent: () => import('./features/auth/pages/login/login').then((m) => m.Login),
  },
  {
    path: '',
    component: Shell,
    canActivate: [authGuard],
    canActivateChild: [rolGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      {
        path: 'dashboard',
        title: 'Resumen',
        data: { rol: 'lector' },
        loadComponent: () =>
          import('./features/dashboard/pages/dashboard/dashboard').then((m) => m.Dashboard),
      },
      {
        path: 'fichas',
        title: 'Fichas',
        data: { rol: 'lector' },
        loadComponent: () =>
          import('./features/conocimiento/pages/fichas-lista/fichas-lista').then(
            (m) => m.FichasLista,
          ),
      },
      {
        path: 'fichas/nueva',
        title: 'Nueva ficha',
        data: { rol: 'editor' },
        loadComponent: () =>
          import('./features/conocimiento/pages/ficha-editor/ficha-editor').then(
            (m) => m.FichaEditor,
          ),
      },
      {
        path: 'fichas/:id',
        title: 'Ficha',
        data: { rol: 'lector' },
        loadComponent: () =>
          import('./features/conocimiento/pages/ficha-editor/ficha-editor').then(
            (m) => m.FichaEditor,
          ),
      },
      {
        path: 'revision',
        title: 'Bandeja de revisión',
        data: { rol: 'revisor' },
        loadComponent: () =>
          import('./features/conocimiento/pages/revision/revision').then((m) => m.Revision),
      },
      {
        path: 'cargas',
        title: 'Subir documento',
        data: { rol: 'editor' },
        loadComponent: () =>
          import('./features/conocimiento/pages/cargas/cargas').then((m) => m.Cargas),
      },
      {
        path: 'intents',
        title: 'Intents',
        data: { rol: 'editor' },
        loadComponent: () =>
          import('./features/intents/pages/intents/intents').then((m) => m.Intents),
      },
      {
        path: 'pendientes',
        title: 'Pendientes',
        data: { rol: 'editor' },
        loadComponent: () =>
          import('./features/pendientes/pages/pendientes/pendientes').then((m) => m.Pendientes),
      },
      {
        path: 'documentos',
        title: 'Documentos',
        data: { rol: 'editor' },
        loadComponent: () =>
          import('./features/documentos/pages/documentos/documentos').then((m) => m.Documentos),
      },
      {
        path: 'probador',
        title: 'Probador',
        data: { rol: 'editor' },
        loadComponent: () =>
          import('./features/probador/pages/probador/probador').then((m) => m.Probador),
      },
      {
        path: 'evaluacion',
        title: 'Golden set',
        data: { rol: 'editor' },
        loadComponent: () =>
          import('./features/evaluacion/pages/evaluaciones/evaluaciones').then(
            (m) => m.Evaluaciones,
          ),
      },
      {
        path: 'evaluacion/:id',
        title: 'Resultado de evaluación',
        data: { rol: 'editor' },
        loadComponent: () =>
          import('./features/evaluacion/pages/evaluacion-detalle/evaluacion-detalle').then(
            (m) => m.EvaluacionDetalle,
          ),
      },
      {
        path: 'conversaciones',
        title: 'Conversaciones',
        data: { rol: 'lector' },
        loadComponent: () =>
          import('./features/conversaciones/pages/conversaciones/conversaciones').then(
            (m) => m.Conversaciones,
          ),
      },
      {
        path: 'usuarios',
        title: 'Usuarios',
        data: { rol: 'superadmin' },
        loadComponent: () =>
          import('./features/usuarios/pages/usuarios/usuarios').then((m) => m.Usuarios),
      },
      {
        path: 'configuracion',
        title: 'Configuración',
        data: { rol: 'superadmin' },
        loadComponent: () =>
          import('./features/configuracion/pages/configuracion/configuracion').then(
            (m) => m.ConfiguracionPagina,
          ),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
