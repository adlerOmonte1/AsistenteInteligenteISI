# Flujo conversacional — Proceso E: Grado de Bachiller y Convalidación de PPP

Contempla lo exigido en el contrato (sección 3.5): desambiguación, solicitud de entidades faltantes, respuesta basada en ficha, seguimiento a pasos o etapas posteriores, cierre y derivación a `GEN_derivar_humano` tras **dos intentos fallidos**.

Convenciones:

- Un **intento fallido** es una respuesta del usuario que no permite reconocer el intent o la entidad pedida. El contador es por conversación y se reinicia al responder con una ficha.
- Si la ficha tiene `estado: pendiente`, la respuesta usa la plantilla `PL_PENDIENTE` y nunca completa el dato faltante.

## 1. Entrada y desambiguación entre procesos

```mermaid
flowchart TD
  A[Mensaje del usuario] --> B{¿Intent reconocido?}
  B -- BAC_* --> BAC[[Flujo Bachiller]]
  B -- CPP_* --> CPP[[Flujo Convalidación PPP]]
  B -- Ambiguo --> C{¿Qué ambigüedad?}
  C -- "«convalidar» sin contexto" --> C1[Preguntar: ¿PPP por experiencia laboral<br/>o cursos por traslado?]
  C -- "«grado» / «título»" --> C2[Preguntar: ¿Grado de Bachiller<br/>o Título Profesional?]
  C -- "«cuánto cuesta» / «a qué correo»" --> C3[Preguntar: ¿Bachiller<br/>o convalidación de PPP?]
  C1 -- PPP --> CPP
  C1 -- Traslado --> TRA[Derivar a TRA_* · integrante F]
  C2 -- Bachiller --> BAC
  C2 -- Título --> TIT[Derivar a GEN_eleccion_modalidad · integrante F]
  C3 -- Bachiller --> BAC
  C3 -- PPP --> CPP
  B -- No --> F1{¿Intentos fallidos >= 2?}
  C1 & C2 & C3 -- Respuesta no reconocida --> F1
  F1 -- No --> R[Reformular: «No te entendí, ¿me lo dices de otra forma?»] --> A
  F1 -- Sí --> H[GEN_derivar_humano]
```

## 2. Flujo del Grado de Bachiller

```mermaid
flowchart TD
  A[Intent BAC_* detectado] --> B{¿Requiere paso_bachiller<br/>y falta?}
  B -- Sí --> C[Preguntar paso: 1 a 6]
  C --> C1{¿Paso reconocido?}
  C1 -- No --> F{¿Intentos fallidos >= 2?}
  F -- No --> C
  F -- Sí --> H[GEN_derivar_humano]
  C1 -- Sí --> D
  B -- No --> D[Recuperar ficha BAC_Pn]
  D --> E{¿estado de la ficha?}
  E -- confirmado --> G[Responder con plantilla del intent]
  E -- pendiente --> G2[Responder con PL_PENDIENTE<br/>+ lo confirmado de la ficha]
  G & G2 --> S{¿Ver paso siguiente?<br/>campo «Siguiente fase»}
  S -- Sí --> N{¿Hay paso siguiente?}
  N -- "Sí: BAC_Pn+1" --> D
  N -- "No (fin, BAC_P06)" --> T[Informar: el Bachiller es requisito<br/>del Título TES_F07 / TSP_F06]
  S -- No --> Z{¿Otra consulta?}
  T --> Z
  Z -- Sí --> A0[Volver a reconocimiento de intent]
  Z -- No --> K[Cierre con PL_CIERRE]
```

## 3. Flujo de la Convalidación de PPP por experiencia laboral

```mermaid
flowchart TD
  A[Intent CPP_* detectado] --> V{¿El usuario ya confirmó<br/>que cumple condiciones?}
  V -- No sabe --> V1[Mostrar CPP_E00:<br/>16 meses · nombrado o contratado ·<br/>ciclo mínimo pendiente]
  V1 --> V2{¿Cumple?}
  V2 -- No --> PPP[Sugerir PPP regular · PPP_* integrante D]
  V2 -- "Sí" --> B
  V -- Sí --> B{¿Requiere etapa_cpp<br/>o documento_cpp y falta?}
  B -- Sí --> C[Preguntar etapa 0 a 4<br/>o documento del expediente]
  C --> C1{¿Entidad reconocida?}
  C1 -- No --> F{¿Intentos fallidos >= 2?}
  F -- No --> C
  F -- Sí --> H[GEN_derivar_humano]
  C1 -- Sí --> D
  B -- No --> D[Recuperar ficha CPP_En]
  D --> E{¿estado de la ficha?}
  E -- confirmado --> G[Responder con plantilla del intent]
  E -- pendiente --> G2[Responder con PL_PENDIENTE<br/>monto / inicio de los 20 días / ciclo]
  G & G2 --> S{¿Ver etapa siguiente?}
  S -- Sí --> N{¿Hay etapa siguiente?}
  N -- "Sí: CPP_En+1" --> D
  N -- "No (fin, CPP_E04)" --> T[Ofrecer el trámite de Bachiller · BAC_P01]
  T -- Acepta --> BAC[[Flujo Bachiller]]
  S -- No --> Z{¿Otra consulta?}
  T -- No --> Z
  Z -- Sí --> A0[Volver a reconocimiento de intent]
  Z -- No --> K[Cierre con PL_CIERRE]
```

## 4. Reglas de decisión

| Situación | Acción del sistema | Plantilla |
|---|---|---|
| Intent BAC/CPP reconocido con todas sus entidades | Responder con la ficha | La del intent |
| Falta entidad obligatoria (`paso_bachiller`, `etapa_cpp`, `documento_cpp`) | Preguntar con el texto `si_falta_entidad` | `PL_FALTA_ENTIDAD` |
| `tipo_foto` no indicada | Mostrar ambas fotos (no se considera intento fallido) | `PL_BAC_FOTOS` |
| Ficha con `estado: pendiente` | Responder lo confirmado y declarar el dato pendiente | `PL_PENDIENTE` |
| «Convalidar» sin contexto | Desambiguar PPP vs. traslado | `PL_DESAMBIGUAR` |
| Usuario pide «siguiente» / «y luego» | Seguir el campo «Siguiente fase» de la ficha | La del intent |
| 2 intentos fallidos consecutivos | Derivar | `GEN_derivar_humano` |
| Usuario pide hablar con una persona | Derivar de inmediato | `GEN_derivar_humano` |
