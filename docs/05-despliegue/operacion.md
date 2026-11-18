# Operación y mantenimiento

Tareas habituales una vez instalado el sistema. Los comandos usan el alias `dc` de la guía de despliegue y se ejecutan en `/opt/asistente`.

## 1. Cuentas

Las crea el Centro de Cómputo en **Panel → Usuarios**. No hay registro público.

| Rol | Para quién |
|---|---|
| `lector` | Quien solo consulta métricas y conversaciones |
| `editor` | Personal que actualiza fichas, intents, pendientes y documentos |
| `revisor` | Coordinación del programa: aprueba lo que publica el editor |
| `superadmin` | Centro de Cómputo |

Las cuentas no se borran: se desactivan, para conservar quién publicó cada cambio. Si una cuenta queda bloqueada por intentos fallidos, se libera sola a los 15 minutos.

## 2. Actualizar la información de un trámite

Cuando cambia un dato oficial (nueva resolución, otro correo, otro monto):

1. El **editor** abre la ficha en Panel → Fichas, la corrige y guarda. El asistente sigue respondiendo con la versión publicada.
2. Actualiza `fuente` y `vigencia` con la norma nueva y marca el dato como `confirmado` solo si hay documento o correo oficial.
3. Pulsa **Enviar a revisión**. El sistema verifica que las seis secciones estén completas.
4. El **revisor** (una persona distinta) abre Panel → Bandeja de revisión y aprueba o rechaza con observaciones.
5. Al aprobar, el worker indexa la ficha y corre una prueba de humo. En menos de dos minutos el asistente responde con el cambio.

Si algo salió mal, el revisor puede **revertir** a cualquier versión anterior desde el historial de la ficha.

Para documentos nuevos (una resolución completa), Panel → Subir documento propone fichas en borrador que se revisan igual.

## 3. Revisar la calidad

Una vez por semana:

- **Panel → Resumen**: porcentaje de derivadas y de respuestas «no útiles». Si suben, hay un tema mal cubierto.
- **Panel → Conversaciones**, filtro «Solo derivadas» y «Calificadas no útiles»: las preguntas que se repiten indican un intent con pocos ejemplos o una ficha que falta.
- **Panel → Pendientes**: preguntas abiertas con Coordinación. Al resolver una, actualice la ficha afectada.
- **Panel → Golden set → Ejecutar** después de cambios grandes. Metas: intent ≥ 90 %, ficha ≥ 90 %, clave ≥ 95 %, inventados = 0.

## 4. Costo del modelo de lenguaje

- El tope duro está en la consola del proveedor (Google AI Studio → límites de gasto). Configúrelo al pasar al plan de pago.
- El tope interno se ajusta en **Panel → Configuración**. Al superarlo, el asistente sigue respondiendo, pero copia las fichas en lugar de redactar.
- El gasto del mes se ve en Panel → Resumen.

## 5. Cambiar la API key o el proveedor

1. Edite `.env` (`LLM_API_KEY`, o `LLM_PROVEEDOR` / `EMBED_PROVEEDOR`).
2. Reinicie: `dc up -d`.
3. Si cambió el proveedor **o el modelo de embeddings**, recalcule el índice: `dc exec api python manage.py reindexar`.

Cambiar solo la clave, manteniendo proveedor y modelo, no requiere reindexar.

## 6. Respaldos

El script `infra/scripts/respaldo.sh` (programado en cron) guarda en `/var/backups/asistente/`:

- `base-AAAAMMDD-HHMM.dump`: toda la base (fichas, versiones, cuentas, consultas, índice);
- `media-AAAAMMDD-HHMM.tar.gz`: documentos subidos desde el panel.

Conserva 14 días. **Copie periódicamente esa carpeta fuera del servidor**: un respaldo en el mismo disco no protege de una falla del disco.

Restaurar una base:

```bash
infra/scripts/restaurar.sh /var/backups/asistente/base-20261201-0200.dump
```

Pide confirmación escribiendo `SI`, detiene la API y el worker mientras restaura y los vuelve a iniciar.

## 7. Registros

```bash
dc logs --tail 100 api
```

```bash
dc logs --tail 100 worker
```

Las preguntas de los estudiantes no aparecen en los registros del servidor; se guardan anonimizadas en la base y se consultan desde el panel.

## 8. Datos personales

- El widget no pide nombre, DNI ni código.
- Si un estudiante los escribe, se reemplazan por marcadores (`[dni]`, `[codigo]`, `[telefono]`, `[correo]`) antes de guardar.
- Las consultas se borran automáticamente a los 12 meses (tarea diaria del worker).
- Al LLM solo se envían la pregunta y el texto de las fichas.

## 9. Ante un incidente

| Situación | Acción inmediata |
|---|---|
| El asistente dio un dato equivocado | Corregir y publicar la ficha; si es urgente, el revisor revierte a la versión anterior |
| Gasto anómalo del LLM | Panel → Configuración → desactivar «Usar el LLM»; revisar Conversaciones |
| Abuso del chat (spam) | Bajar `LIMITE_MENSAJES_*` en `.env` y `dc up -d` |
| Clave del proveedor expuesta | Revocarla en AI Studio, crear otra, actualizar `.env`, `dc up -d` |
| Servidor caído | `dc ps`; `dc up -d`; si la base se dañó, restaurar el último respaldo |
