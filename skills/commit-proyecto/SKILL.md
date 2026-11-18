---
name: commit-proyecto
description: Cierra una tarea en el repositorio del Asistente Académico UDH preparando los comandos de rama y commit para que los ejecute el usuario, con el formato de mensajes del proyecto. Úsala cuando se pida commitear, hacer el commit, subir o cerrar una tarea, o al terminar un cambio.
---

# Commits del proyecto

## Quién ejecuta

**El usuario ejecuta `git add`, `git commit`, la creación de ramas y el `push`.** El agente no los ejecuta: entrega los comandos, cada uno en su propio bloque, listos para copiar. Puede ejecutar comandos de solo lectura (`git status`, `git diff`, `git log`).

## Antes de proponer el commit

1. Ejecute la verificación de `CLAUDE.md` (backend, frontend, C4, contrato) y reporte el resultado real.
2. Revise `git status` para no incluir `.env`, `node_modules`, `dist`, `.venv`, `media` ni datos de estudiantes.
3. Liste los archivos cambiados agrupados por área.

## Ramas

`main` está protegida. Una rama por tarea, creada desde `main` actualizado:

| Tipo | Rama |
|---|---|
| Funcionalidad | `feat/<tema>` |
| Corrección | `fix/<tema>` |
| Documentación | `docs/<tema>` |
| Base de conocimiento | `kb/<proceso>` |
| Infraestructura | `infra/<tema>` |

## Mensaje

```
tipo(alcance): asunto en imperativo
```

- En español, **sin tildes**, en minúsculas, sin punto final, hasta 72 caracteres.
- `tipo`: `feat`, `fix`, `docs`, `kb`, `infra`, `test`, `refactor`.
- `alcance`: app, proyecto o proceso (`dialogo`, `admin`, `traslados`, `despliegue`).
- Cuerpo opcional: qué cambia y por qué, en líneas de 72 caracteres.
- Sin líneas de coautoría ni firmas de herramientas.

Ejemplos:

```
feat(conocimiento): revertir una ficha a una version anterior
fix(generacion): no reintentar ante la cuota diaria de gemini
kb(traslados): ids al formato del contrato
docs(despliegue): guia de certificados https
```

## Formato de la entrega

```bash
git switch -c feat/<tema>
```

```bash
git add <rutas>
```

```bash
git commit -m "feat(alcance): asunto"
```

Y una línea final con lo que no se verificó, si lo hay.
