# Proceso A & E — Fase 2

Entregables de los integrantes **A** (arquitectura y consolidación) y **E** (Grado de Bachiller y Convalidación de PPP por experiencia laboral), según el contrato de [`EntregableFase2.md`](../../EntregableFase2.md).

```
Proceso A & E/
├── 00_arquitectura/                      # A
│   ├── arquitectura_hibrida.md           # Documento de arquitectura híbrida
│   ├── esquema_metadatos.md              # Esquema de metadatos (explicado)
│   ├── esquema_metadatos.schema.json     # Esquema de metadatos (JSON Schema)
│   ├── flujo_actualizacion_admin.md      # Diagrama del flujo de actualización
│   ├── plantilla_informe_final.md        # Plantilla del informe final
│   ├── informe_final_consolidado.md      # Informe final (borrador, se cierra el 29/10)
│   └── validar_contrato.py               # Revisión automática del contrato por carpeta
└── bachiller_conv_ppp/                   # E
    ├── fichas/                           # BAC_P01–P06 · CPP_E00–E04
    ├── intents.yaml                      # 16 intents (8 BAC_, 8 CPP_)
    ├── entidades.yaml                    # paso_bachiller, tipo_foto, etapa_cpp, documento_cpp
    ├── flujo.md                          # Flujos conversacionales en Mermaid
    ├── plantillas.md                     # Plantillas de respuesta
    ├── golden_set.csv                    # 26 preguntas (14 BAC, 12 CPP)
    └── pendientes.md                     # 13 datos para la reunión del 28/10
```

## Validar una carpeta

```bash
python 00_arquitectura/validar_contrato.py . --md
```

Revisa encabezados de fichas, secciones, prefijos, mínimo de 10 ejemplos por intent, `si_falta_entidad`, Mermaid y `GEN_derivar_humano` en el flujo, golden set (≥ 10 por prefijo, intents y fichas existentes) y que las fichas pendientes figuren en `pendientes.md`. Sirve también para las carpetas de B, C, D y F: basta con pasar la carpeta raíz que las contenga.

## Fuentes usadas

- [`procesoBachiller.md`](../procesoBachiller.md) — flujograma «Trámite Virtual de optar el Grado Académico de Bachiller».
- [`PROCESO_PPP.md`](../PROCESO_PPP.md) §11 y [`diagrama-secuencia-convalidacion-ppp.md`](../diagrama-secuencia-convalidacion-ppp.md) — Reglamento de PPP 2021, Arts. 31–32.
- [`Documento_Consolidado_Procesos_PA_ISI.docx`](../Documento_Consolidado_Procesos_PA_ISI.docx) — Fase 1.

No se agregó ningún requisito, costo, plazo ni correo que no figure en estas fuentes; lo que falta está en `bachiller_conv_ppp/pendientes.md`.
