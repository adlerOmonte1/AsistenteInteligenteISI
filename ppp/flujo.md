# Flujo conversacional — PPP

El proceso tiene tres flujos:
1. **Flujo principal:** atiende las 14 intenciones de PPP.
2. **Flujo de diagnóstico de etapa:** guía al estudiante que no sabe qué le toca hacer.
3. **Flujo de verificación de condiciones:** confirma si el estudiante puede iniciar las prácticas.

---

## 1. Flujo principal

```mermaid
flowchart TD
    A([Mensaje del estudiante]) --> B{¿Intent de PPP?}
    B -- No --> Z1[Otros procesos:<br/>GEN_, BAC_, TES_, TSP_, TRA_]
    B -- Sí --> C{¿Menciona experiencia laboral<br/>o convalidar prácticas?}
    C -- Sí --> Z2[Desvío a CPP_*]
    C -- No --> D{¿Qué intent?}

    D -- PPP_info_general --> R1[Respuesta fija]
    D -- PPP_asesor_supervisor --> R1
    D -- PPP_sustentacion --> R1
    D -- PPP_anulacion --> R1
    D -- PPP_siguiente_paso --> R1
    D -- PPP_requisitos_inicio --> V[[Flujo 3:<br/>verificación de condiciones]]
    D -- PPP_diagnostico_etapa --> DG[[Flujo 2:<br/>diagnóstico de etapa]]

    D -- PPP_costo<br/>PPP_plazo<br/>PPP_estado_tramite --> F{¿Indicó etapa?}
    F -- No --> F1[Resumen de todas las etapas]
    F -- Sí --> H

    D -- PPP_requisitos_etapa<br/>PPP_pasos_etapa<br/>PPP_correo_etapa --> G{¿Indicó etapa?}
    G -- Sí --> H
    G -- No --> G1[Preguntar etapa]

    D -- PPP_anexo_info --> AN{¿Indicó anexo?}
    AN -- Sí --> H
    AN -- No --> AN1[Preguntar anexo]

    G1 --> X{¿Respuesta válida?}
    AN1 --> X
    X -- Sí --> H
    X -- No, 1.er intento --> X1[Repetir la pregunta<br/>con las opciones numeradas]
    X1 --> X
    X -- No, 2.º intento --> Z3[GEN_derivar_humano]

    H[Buscar ficha y datos_clave.json] --> I{¿Estado del dato?}
    I -- confirmado --> J[Responder con plantilla]
    I -- pendiente --> K[Plantilla de dato no confirmado<br/>+ correo del P.A.]

    R1 --> L
    F1 --> L
    J --> L
    K --> L
    L[Pregunta de seguimiento<br/>de la plantilla] --> M{¿Acepta?}
    M -- Sí --> H
    M -- No --> N([GEN_despedida])
```

---

## 2. Flujo de diagnóstico de etapa

Se activa con `PPP_diagnostico_etapa`. Hace preguntas de sí o no, en orden, y se detiene en la primera respuesta «no».

```mermaid
flowchart TD
    A([PPP_diagnostico_etapa]) --> Q0{¿Ya tiene una entidad<br/>que lo acepte como practicante?}
    Q0 -- No --> V[[Flujo 3:<br/>verificación de condiciones]]
    Q0 -- Sí --> Q1{¿Ya recibió la carta de<br/>presentación de la Facultad?}
    Q1 -- No --> E1[Etapa 1:<br/>respuesta DX_E01]
    Q1 -- Sí --> Q2{¿Su Plan de PPP<br/>ya fue aprobado?}
    Q2 -- No --> Q2b{¿Ya inició sus prácticas<br/>en la entidad?}
    Q2b -- Sí --> E2a[Etapa 2 con alerta de plazo:<br/>respuesta DX_E02_ALERTA]
    Q2b -- No --> E2[Etapa 2:<br/>respuesta DX_E02]
    Q2 -- Sí --> Q3{¿Ya cumplió las<br/>600 horas?}
    Q3 -- No --> E3[Etapa 3:<br/>respuesta DX_E03]
    Q3 -- Sí --> Q4{¿Ya envió su<br/>informe final?}
    Q4 -- No --> E4[Etapa 4:<br/>respuesta DX_E04]
    Q4 -- Sí --> Q5{¿Ya recibió la resolución<br/>de la Facultad?}
    Q5 -- No --> E5[En evaluación:<br/>respuesta DX_E04_EVAL]
    Q5 -- Sí --> E6[PPP concluida:<br/>respuesta DX_FIN → BAC_*]

    E1 --> S[Pregunta de seguimiento]
    E2 --> S
    E2a --> S
    E3 --> S
    E4 --> S
    E5 --> S
    E6 --> S
```

Si el estudiante responde algo distinto de sí o no dos veces seguidas, pasa a `GEN_derivar_humano`.

---

## 3. Flujo de verificación de condiciones

Se activa con `PPP_requisitos_inicio` cuando el estudiante pregunta si **él** puede iniciar («¿puedo empezar?»). Si solo pide la lista de condiciones, se responde directamente con la plantilla `PPP_requisitos_inicio`.

```mermaid
flowchart TD
    A([¿Puedo iniciar mis prácticas?]) --> C1{¿Concluyó todos los cursos de<br/>especialidad hasta el 8.º ciclo?}
    C1 -- No --> N1[No puede iniciar todavía:<br/>respuesta VC_CICLO]
    C1 -- Sí --> C2{¿El horario de prácticas<br/>se cruza con sus clases?}
    C2 -- Sí --> N2[Debe ajustar el horario:<br/>respuesta VC_HORARIO]
    C2 -- No --> C3{¿Lo supervisará un Ingeniero<br/>de Sistemas o de carrera afín?}
    C3 -- No --> N3[Entidad no válida:<br/>respuesta VC_SUPERVISOR]
    C3 -- Sí --> C4{¿Trabajará en desarrollo, redes,<br/>seguridad, gestión de TIC<br/>o gestión de proyectos?}
    C4 -- No --> N4[Área no válida:<br/>respuesta VC_AREA]
    C4 -- Sí --> OK[Cumple las condiciones:<br/>respuesta VC_OK → Etapa 1]
    C4 -- No sabe --> N5[Mostrar la lista de áreas<br/>y repetir la pregunta]
    N5 --> C4
```

---

## Reglas del flujo

| Situación | Comportamiento |
|---|---|
| Pregunta requisitos, pasos o correo sin indicar la etapa | Se pregunta la etapa con las 4 opciones numeradas |
| Pregunta costo, plazo o estado sin etapa | No se pregunta: se muestra el resumen de todas las etapas |
| Pregunta por un anexo sin número | Se pregunta el anexo mostrando la lista 02, 03, 04, 05, 06, 07 y 10 |
| Pregunta por el Anexo 01 | Se indica que no se exige |
| Pregunta por los Anexos 08 o 09 | Desvío a `CPP_*` |
| Menciona que ya trabaja o quiere convalidar | Desvío a `CPP_*` antes de responder |
| Pide el correo de la Etapa 3 | Se aclara que en esa etapa el estudiante no envía documentos |
| Dos respuestas no reconocidas seguidas | `GEN_derivar_humano` |
| El dato está marcado como pendiente | Plantilla de dato no confirmado, con el correo del P.A. |
| Termina una respuesta de etapa | Se ofrece la etapa siguiente (campo `Siguiente fase` de la ficha) |
| El estudiante responde la etapa con un número (1 a 4) | Se acepta como valor de la entidad `etapa` |
| El mensaje ya responde una pregunta de los flujos 2 o 3 (por ejemplo, «estoy en séptimo ciclo») | Se omite esa pregunta y se usa la respuesta dada |

---

## Ejemplos de conversación

**Desambiguación de etapa**
> **Estudiante:** a qué correo mando mis documentos de prácticas
>
> **Chatbot:** El correo cambia según la etapa. ¿Para cuál lo necesita? 1) Carta de presentación, 2) Plan de PPP o 4) Informe final.
>
> **Estudiante:** el plan
>
> **Chatbot:** Para la Etapa 2, Plan de PPP, envíe sus documentos a comision.practicas.isi@udh.edu.pe. Tiene como máximo 15 días calendario desde el inicio de su práctica para presentarlo.
> ¿Desea ver los requisitos del Plan de PPP?

**Diagnóstico de etapa**
> **Estudiante:** no sé qué me toca hacer en mis prácticas
>
> **Chatbot:** Le ayudo a ubicar su etapa. ¿Ya tiene una entidad que lo acepte como practicante?
>
> **Estudiante:** sí
>
> **Chatbot:** ¿Ya recibió la carta de presentación de la Facultad?
>
> **Estudiante:** sí
>
> **Chatbot:** ¿Su Plan de PPP ya fue aprobado?
>
> **Estudiante:** no
>
> **Chatbot:** ¿Ya inició sus prácticas en la entidad?
>
> **Estudiante:** sí, hace una semana
>
> **Chatbot:** Usted está en la Etapa 2, Plan de PPP. Tiene como máximo 15 días calendario desde el inicio de su práctica para presentar el Plan, así que le recomiendo enviarlo cuanto antes a comision.practicas.isi@udh.edu.pe.
> ¿Desea ver los requisitos del Plan?

**Dato no confirmado**
> **Estudiante:** cuánto se paga por el plan
>
> **Chatbot:** Ese dato aún no está confirmado en la información oficial. Para no darle información incorrecta, le recomiendo consultarlo en secretaria.sistemas.hco@udh.edu.pe.

**Desvío a otro proceso**
> **Estudiante:** trabajo hace 2 años en sistemas, igual tengo que hacer prácticas
>
> **Chatbot:** Si usted ya trabajó 16 meses o más en labores de la especialidad, puede convalidar sus prácticas en lugar de realizarlas. ¿Desea conocer ese trámite?
