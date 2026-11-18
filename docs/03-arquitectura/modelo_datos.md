# Modelo de datos

Fuente: los `models.py` de cada app. Las migraciones están en `backend/apps/<app>/migrations/` y el CI comprueba que no falte ninguna (`makemigrations --check`).

```mermaid
erDiagram
  FACULTAD ||--o{ PROGRAMA : tiene
  PROGRAMA ||--o{ PROCESO : tiene
  FACULTAD |o--o{ USUARIO : limita
  PROCESO ||--o{ FICHA : describe
  FICHA ||--o{ VERSION_FICHA : publica
  FICHA |o--o| VERSION_FICHA : version_publicada
  FICHA |o--o| FICHA : reemplazada_por
  PROCESO ||--o{ INTENT : agrupa
  INTENT }o--o{ FICHA : responde_con
  INTENT ||--o{ EJEMPLO_INTENT : tiene
  PROCESO ||--o{ PENDIENTE : tiene
  PENDIENTE }o--o{ FICHA : afecta
  PROCESO |o--o{ PLANTILLA : tiene
  PROCESO |o--o{ DOCUMENTO : publica
  PROCESO ||--o{ CARGA_DOCUMENTO : recibe
  VERSION_FICHA ||--o{ SECCION_INDEXADA : indexa
  PROCESO ||--o{ CASO_EVALUACION : prueba
  EVALUACION ||--o{ RESULTADO_CASO : contiene
  CASO_EVALUACION ||--o{ RESULTADO_CASO : evalua
  CONVERSACION }o--o| FICHA : ficha_actual
  CONSULTA }o--o| PROCESO : trata
```

## Entidades

| Entidad | App | Propósito | Reglas |
|---|---|---|---|
| `Facultad`, `Programa`, `Proceso` | conocimiento | Jerarquía que permite escalar a toda la universidad. | `Proceso.clave` es única por programa; `prefijos` define qué códigos le pertenecen. |
| `Ficha` | conocimiento | **Borrador** editable de una fase. | `codigo` único por proceso y no cambia una vez publicado. Seis secciones obligatorias para enviar a revisión. |
| `VersionFicha` | conocimiento | Copia **inmutable** de lo publicado. Lo que responde el asistente y muestra el portal. | Numeración correlativa por ficha. Nunca se edita ni se borra. |
| `Intent`, `EjemploIntent` | conocimiento | Intención del estudiante y sus ejemplos con embedding. | `secciones` limita lo que muestra la vía determinista. |
| `Plantilla`, `Pendiente` | conocimiento | Textos reutilizables y datos por confirmar con Coordinación. | Resolver un pendiente no modifica fichas. |
| `Documento` | conocimiento | Biblioteca normativa del portal. | Archivo .pdf/.docx validado por firma o enlace externo. |
| `CargaDocumento` | conocimiento | Documento subido para proponer fichas en borrador. | Las fichas propuestas siempre quedan en borrador. |
| `SeccionIndexada` | recuperacion | Una sección de una versión publicada, con su embedding (768, HNSW coseno). | Al publicar, las anteriores pasan a `vigente=False`. Guarda el proveedor del embedding. |
| `Conversacion` | dialogo | Estado del diálogo de una sesión anónima. | La sesión es un UUID del navegador. |
| `Consulta` | analitica | Registro de cada pregunta y respuesta. | Pregunta enmascarada; se purga a los 12 meses. |
| `CasoEvaluacion`, `Evaluacion`, `ResultadoCaso` | evaluacion | Golden set y sus ejecuciones. | Una evaluación puede ser manual o una prueba de humo tras publicar. |
| `Usuario` | cuentas | Cuenta del personal. | Rol jerárquico; `facultad` vacía = todas. |
| `Configuracion` | sistema | Parámetros editables desde el panel. | Fila única (pk = 1). |

## Ciclo de vida de una ficha

```mermaid
stateDiagram-v2
  [*] --> borrador: crear o importar
  borrador --> en_revision: enviar a revision y validar contrato
  en_revision --> publicada: aprobar - revisor distinto del editor
  en_revision --> rechazada: rechazar con observaciones
  rechazada --> borrador: editar
  publicada --> borrador: editar - lo publicado no cambia
  publicada --> publicada: revertir a una version anterior
```

Al aprobar se crea una `VersionFicha`, el worker indexa sus secciones y corre una prueba de humo con tres casos del golden set del proceso. Si la prueba detecta datos inventados, se vuelve automáticamente a la versión anterior.
