import { describe, expect, it } from 'vitest';
import { markdownSeguro } from './markdown';

describe('markdownSeguro', () => {
  it('escapa HTML antes de transformar', () => {
    const html = markdownSeguro('<img src=x onerror=alert(1)> **hola**');
    expect(html).not.toContain('<img');
    expect(html).toContain('&lt;img');
    expect(html).toContain('<strong>hola</strong>');
  });

  it('arma listas numeradas y con viñetas', () => {
    expect(markdownSeguro('1. Primero\n2. Segundo')).toBe(
      '<ol><li>Primero</li><li>Segundo</li></ol>',
    );
    expect(markdownSeguro('- Uno\n- Dos')).toBe('<ul><li>Uno</li><li>Dos</li></ul>');
  });

  it('enlaza correos institucionales', () => {
    expect(markdownSeguro('Envíe a secretaria.sistemas.hco@udh.edu.pe')).toContain(
      'href="mailto:secretaria.sistemas.hco@udh.edu.pe"',
    );
  });

  it('no convierte en enlace un javascript: disfrazado', () => {
    expect(markdownSeguro('javascript:alert(1)')).not.toContain('<a');
  });
});
