# Pendientes para Coordinación — PPP

Llevar a la reunión del 28 de octubre. Mientras no se confirmen, el chatbot responde con la plantilla `DATO_PENDIENTE`. Al confirmar cada punto, actualizar la ficha, `datos_clave.json`, la plantilla y la fila del golden set indicadas.

| # | Pregunta para Coordinación | Ficha | Plantilla | Golden set |
|---|---|---|---|---|
| 1 | ¿El trámite «Aprobación de Plan de PPP» tiene algún pago? ¿Cuánto? | PPP_E02 | PPP_costo · plan | PPP_Q26 |
| 2 | ¿El trámite «Aprobación del informe final de PPP» tiene algún pago? ¿Cuánto? | PPP_E04 | PPP_costo · informe_final | — |
| 3 | Los 15 días para presentar el Plan, ¿son calendario o hábiles? El flujograma solo dice «15 días». | PPP_E02 | PPP_plazo · plan | PPP_Q27 |
| 4 | ¿En cuánto tiempo se emite la carta de presentación? | PPP_E01 | PPP_plazo · carta_presentacion | PPP_Q31 |
| 5 | ¿Dónde se descargan los formatos de los anexos? | PPP_T02 | PPP_anexo_info · descarga | PPP_Q36 |
| 6 | ¿Cómo se entera el estudiante de que su Plan fue aprobado u observado? ¿Y del resultado del informe final? | PPP_E02, PPP_E04 | PPP_estado_tramite · plan / informe_final | PPP_Q45 |
| 7 | ¿Cómo se programa la sustentación y si es virtual o presencial? | PPP_E04 | PPP_sustentacion | PPP_Q40 |
| 8 | El reinicio en 30 días calendario en otra entidad, ¿aplica a todas las causales de anulación o solo a no subsanar el Plan? | PPP_T01 | PPP_anulacion | PPP_Q43 |
| 9 | ¿Dónde y cómo se obtiene la constancia de inscripción en Seguimiento del Graduado? | PPP_E04 | PPP_requisitos_etapa · informe_final | — |
| 10 | ¿Cómo recibe el estudiante la resolución de aprobación de la PPP? | PPP_E04 | PPP_siguiente_paso | — |

## Criterios ya acordados con Coordinación (no se vuelven a preguntar)

| Punto | Criterio aplicado |
|---|---|
| Orden de la carta de aceptación | Se consigue antes de la carta de presentación |
| Plazo del informe final | 20 días hábiles |
| Formato del informe | Solo PDF por correo |
| Correos de destino | Los tres correos específicos del flujograma |
| Solicitud de practicante (Anexo 01) | No se exige |
| Autorización de la Comisión (Art. 7, inc. 2) | Se omite |
