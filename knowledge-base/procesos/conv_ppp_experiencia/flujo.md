# Flujo conversacional — Convalidación de PPP por experiencia laboral (CPP_)

## 1. Flujo del asistente

```mermaid
flowchart TD
  A[Pregunta del usuario] --> B{¿Intent CPP_ detectado?}
  B -- No --> X{¿Segundo intento fallido?}
  X -- No --> Y[Pedir reformular y ofrecer menú: condiciones, requisitos, pasos, plazo, costo]
  Y --> A
  X -- Sí --> Z[GEN_derivar_humano]
  B -- Sí, pero ambiguo --> D[Desambiguar: ¿convalidación por experiencia laboral o PPP normal?]
  D --> E
  B -- Sí --> E{¿Falta la etapa?}
  E -- Sí --> F[Preguntar etapa: 1 solicitud, 2 verificación, 3 comisión, 4 resolución]
  E -- No --> G[Responder con la ficha CPP_Fxx]
  F --> G
  G --> H{¿Quiere ver la etapa siguiente?}
  H -- Sí --> G
  H -- No --> I{¿Resolvió su duda?}
  I -- No --> A
  I -- Sí --> J[Cierre]
```

**Regla de derivación:** tras dos intentos fallidos se usa `GEN_derivar_humano` (definido por F).

## 2. Flujo del proceso (referencia para las respuestas)

```mermaid
flowchart LR
  A["Estudiante: solicita en sistema UDH y envía requisitos (CPP_F02)"] --> B["P.A. Sistemas: verifica conformidad y deriva (CPP_F03)"]
  B --> C["Comisión de PPP: evalúa expediente y sustentación, emite constancia (CPP_F04)"]
  C --> D["P.A. Sistemas: recibe informe y eleva a Facultad (CPP_F04)"]
  D --> E["Facultad de Ingeniería: aprueba por Resolución (CPP_F05)"]
```

## 3. Desambiguación

| Situación | Pregunta del bot |
|---|---|
| El usuario dice solo "convalidar" | "¿Te refieres a convalidar la PPP por experiencia laboral, o por traslado?" (si es traslado, derivar a TRA_) |
| El usuario dice solo "prácticas" | "¿Quieres información de las prácticas preprofesionales normales (PPP_) o de convalidarlas con tu trabajo (CPP_)?" |
| El usuario dice "proceso" sin más | "¿Quieres el resumen completo o una etapa? (1 solicitud, 2 verificación, 3 comisión, 4 resolución)" |

## 4. Conversaciones de ejemplo

**Caso A: respuesta directa**
- Usuario: ¿Qué documentos necesito para convalidar mi PPP por trabajo?
- Bot: (CPP_requisitos → CPP_F02) lista de 5 documentos + correo de envío + plazo de 20 días para el informe. "¿Quieres ver qué pasa después de enviarlos?"
- Usuario: Sí.
- Bot: (CPP_F03) El Programa Académico verifica y deriva a la Comisión de PPP. "¿Seguimos con la etapa de la Comisión?"
- Usuario: No, gracias.
- Bot: Cierre.

**Caso B: falta la etapa**
- Usuario: Explícame el proceso.
- Bot: "¿Quieres el resumen completo o una etapa? (1 solicitud, 2 verificación, 3 comisión, 4 resolución)"
- Usuario: La 3.
- Bot: (CPP_F04) La Comisión evalúa el expediente y la sustentación y emite su constancia de aprobación.

**Caso C: fallback y derivación**
- Usuario: ¿Me conviene más convalidar o hacer prácticas?
- Bot: (intento 1) "No tengo información para comparar. ¿Quieres saber las condiciones, requisitos, pasos, plazo o costo de la convalidación?"
- Usuario: Dime cuál es mejor para mí.
- Bot: (intento 2) → `GEN_derivar_humano`.
