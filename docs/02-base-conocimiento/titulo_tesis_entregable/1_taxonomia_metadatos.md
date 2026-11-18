# Paso 1 — Taxonomía y esquema de metadatos

## Jerarquía

```text
Facultad: Ingeniería
 └─ Programa: Ingeniería de Sistemas e Informática
     └─ Proceso: Optar Título Profesional – Modalidad Sustentación de Tesis
         └─ Fase: 1 … 9  (+ "general")
             └─ {requisito, paso, pago, plazo, correo, actor, anexo, advertencia}
```

## Esquema de metadatos por fragmento

| Campo | Valores | Ejemplo |
|-------|---------|---------|
| `facultad` | Ingeniería | Ingeniería |
| `programa` | Ingeniería de Sistemas e Informática | idem |
| `proceso` | `titulo_tesis` | titulo_tesis |
| `fase` | 1…9 / `general` | 4 |
| `tipo_dato` | requisito \| paso \| pago \| plazo \| correo \| actor \| anexo \| advertencia | plazo |
| `fuente` | Resolución N.° 2367-2025-R-CU-UDH (11-nov-2025) | idem |
| `fecha_vigencia` | 2025-11-11 | 2025-11-11 |
| `estado` | confirmado \| pendiente | pendiente |

## Ejemplo de fragmento

```json
{
  "facultad": "Ingeniería",
  "programa": "Ingeniería de Sistemas e Informática",
  "proceso": "titulo_tesis",
  "fase": 7,
  "tipo_dato": "requisito",
  "texto": "Boleta de pago.",
  "fuente": "Resolución N.° 2367-2025-R-CU-UDH (11-nov-2025)",
  "fecha_vigencia": "2025-11-11",
  "estado": "pendiente"
}
```

## Reglas
- `estado = pendiente` cuando el documento no especifica el dato (montos Fases 2–8, boleta de pago Fase 7, requisitos del Repositorio, etc.).
- Todo fragmento lleva los 8 metadatos; sin metadatos completos no se indexa.
