import { Pipe, PipeTransform } from '@angular/core';

/**
 * Markdown mínimo para las respuestas del asistente y las fichas: negritas,
 * cursivas, listas, enlaces y saltos de línea. Escapa el HTML antes de
 * transformar, de modo que el texto nunca puede inyectar etiquetas.
 */
export function markdownSeguro(texto: string): string {
  const escapado = texto
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  const enLinea = (linea: string) =>
    linea
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[\s(])_(.+?)_(?=[\s.,;:)]|$)/g, '$1<em>$2</em>')
      .replace(/(^|[\s(])\*(?!\s)(.+?)\*(?=[\s.,;:)]|$)/g, '$1<em>$2</em>')
      .replace(
        /(https?:\/\/[^\s<]+[^\s<.,;:)])/g,
        '<a href="$1" target="_blank" rel="noopener">$1</a>',
      )
      .replace(/\b([\w.+-]+@udh\.edu\.pe)\b/g, '<a href="mailto:$1">$1</a>');

  const bloques: string[] = [];
  let lista: { tipo: 'ul' | 'ol'; items: string[] } | null = null;
  const cerrarLista = () => {
    if (lista)
      bloques.push(
        `<${lista.tipo}>${lista.items.map((i) => `<li>${i}</li>`).join('')}</${lista.tipo}>`,
      );
    lista = null;
  };

  for (const linea of escapado.split('\n')) {
    const vineta = linea.match(/^\s*[-•]\s+(.*)$/);
    const numerada = linea.match(/^\s*\d+[.)]\s+(.*)$/);
    if (vineta || numerada) {
      const tipo = vineta ? 'ul' : 'ol';
      if (!lista || lista.tipo !== tipo) {
        cerrarLista();
        lista = { tipo, items: [] };
      }
      lista.items.push(enLinea((vineta ?? numerada)![1]));
      continue;
    }
    cerrarLista();
    if (linea.trim()) bloques.push(`<p>${enLinea(linea)}</p>`);
  }
  cerrarLista();
  return bloques.join('');
}

@Pipe({ name: 'markdown' })
export class MarkdownPipe implements PipeTransform {
  transform(valor: string | null | undefined): string {
    return valor ? markdownSeguro(valor) : '';
  }
}
