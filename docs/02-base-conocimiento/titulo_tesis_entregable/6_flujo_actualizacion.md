# Paso 6 — Flujo de actualización de la base de conocimiento

```mermaid
flowchart TD
    A[Admin sube documento PDF/DOCX del reglamento o guía] --> B[Extracción de texto]
    B --> C["Fragmentación por fase (1…9 + general)"]
    C --> D["Asignar metadatos: facultad, programa, proceso=titulo_tesis, fase, tipo_dato, fuente, fecha_vigencia, estado"]
    D --> E{Revisión humana}
    E -->|Dato claro| F[estado = confirmado]
    E -->|Dato ambiguo o ausente| G[estado = pendiente]
    F --> H[Indexar en el RAG + actualizar fichas JSON]
    G --> H
    H --> I[Ejecutar golden set de regresión]
    I -->|Pasa| J[Archivar versión anterior y publicar]
    I -->|Falla| K[Corregir fichas y volver a revisión]
    K --> E
```

## Responsables
| Rol | Responsabilidad |
|-----|-----------------|
| **Coordinación del Programa (Ing. de Sistemas e Informática)** | Aprobar el contenido y resolver los puntos `pendiente` (montos, boleta de pago, requisitos del Repositorio). |
| **Secretaría del Programa** | Verificar correos, teléfonos, trámites de Login y plazos operativos. |
| **Administrador del bot** | Subir documento, ejecutar indexación y el golden set, archivar la versión anterior. |

## Frecuencia de reindexación
- **Obligatoria:** cada vez que cambie el reglamento o la Resolución (nuevo documento).
- **Programada:** revisión al inicio de cada semestre académico.
- **Ante cambio de datos exactos** (monto, correo, teléfono): actualización inmediata de la ficha JSON.

## Versionado
`vAAAA.MM.DD` por documento fuente. Versión vigente: **v2025.11.11** (Resolución N.° 2367-2025-R-CU-UDH). Las versiones anteriores se archivan, no se borran.
