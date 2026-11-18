import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    title: 'Asistente Académico · Ingeniería de Sistemas e Informática',
    loadComponent: () => import('./features/inicio/inicio').then((m) => m.Inicio),
  },
  {
    path: 'tramites/:clave',
    loadComponent: () => import('./features/tramite/tramite').then((m) => m.Tramite),
  },
  {
    path: 'documentos',
    title: 'Documentos y normativa',
    loadComponent: () => import('./features/documentos/documentos').then((m) => m.Documentos),
  },
  {
    path: 'asistente',
    title: 'Conversar con el asistente',
    loadComponent: () => import('./features/asistente/asistente').then((m) => m.Asistente),
  },
  {
    path: 'buscar',
    title: 'Buscar',
    loadComponent: () => import('./features/buscar/buscar').then((m) => m.Buscar),
  },
  {
    path: 'acerca',
    title: 'Acerca del asistente',
    loadComponent: () => import('./features/acerca/acerca').then((m) => m.Acerca),
  },
  { path: '**', redirectTo: '' },
];
