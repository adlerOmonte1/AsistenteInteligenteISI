# ADR-0001 · Monorepo con una carpeta por contenedor C4

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

El repositorio nació para los entregables documentales de las fases 1 y 2: archivos sueltos en la raíz y una carpeta por integrante. Para construir el software se necesitan backend, frontend, infraestructura y la base de conocimiento, y el equipo de seis personas debe poder trabajar en paralelo sin pisarse. El sistema se entregará al Centro de Cómputo, que necesita encontrar todo en un solo lugar.

## Decisión

Un solo repositorio con una carpeta por contenedor del modelo C4 y una por tipo de contenido:

```
backend/   frontend/   infra/   knowledge-base/   docs/   scripts/   skills/
```

Dentro de `backend/apps/` hay una app de Django por componente; dentro de `frontend/projects/*/src/app/features/` una feature por componente. `scripts/validar_c4.py` exige en el CI que cada una tenga su elemento en `docs/03-arquitectura/modelo-c4/workspace.dsl`.

## Alternativas consideradas

- **Repositorios separados para backend y frontend.** Obliga a coordinar versiones de la API entre repositorios y duplica el CI. Para un equipo pequeño y una sola entrega, el costo no se justifica.
- **Mantener la estructura por integrante.** Mezcla documentos y código y no sobrevive a la entrega: el Centro de Cómputo no conoce a los integrantes.

## Consecuencias

- Un Pull Request puede cambiar la API y el panel juntos, y el CI prueba ambos.
- Las ramas anteriores a la reorganización chocan con la nueva estructura: hay que rebasarlas o mover sus archivos a mano.
- Crear, renombrar o borrar una app o feature obliga a actualizar el modelo C4 en el mismo PR.
