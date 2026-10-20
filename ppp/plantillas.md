# Plantillas de respuesta — PPP

## Convenciones
- Trato de **usted**.
- Cada respuesta tiene una clave `INTENT · etapa` o un código de flujo (`DX_`, `VC_`).
- Requisitos con viñetas; pasos numerados.
- Las respuestas de etapa cierran con el correo y una pregunta de seguimiento.
- Máximo unas 120 palabras por mensaje.
- Los datos vienen de `fichas/` y `datos_clave.json`. Si un dato cambia, se actualiza ahí y aquí.

---

## Información general

### PPP_info_general
```
Las Prácticas Pre Profesionales son obligatorias y no tienen exoneración. Consisten en 600 horas efectivas en cuatro etapas:
1. Carta de presentación
2. Plan de PPP
3. Ejecución
4. Informe final y sustentación

Son requisito para obtener el Grado de Bachiller.
¿Desea conocer las condiciones para iniciarlas?
```

### PPP_requisitos_inicio
```
Para iniciar sus prácticas debe cumplir lo siguiente:
- Haber concluido todos los cursos de especialidad hasta el octavo ciclo.
- Tener un horario de prácticas que no se cruce con sus clases.
- Practicar en una entidad pública o privada del rubro, supervisado por un Ingeniero de Sistemas o de carrera afín.
- Trabajar en un área válida: desarrollo de sistemas; infraestructura, redes y comunicaciones; seguridad y auditoría; gestión de TIC; o gestión de proyectos.

Si ya trabajó 16 meses o más en la especialidad, puede convalidar sus prácticas por experiencia laboral.
¿Desea conocer la primera etapa, la carta de presentación?
```

---

## Verificación de condiciones (Flujo 3)

### VC_CICLO
```
Todavía no puede iniciar sus prácticas. Primero debe concluir todos los cursos de especialidad hasta el octavo ciclo.
```

### VC_HORARIO
```
El horario de sus prácticas no puede cruzarse con el de sus clases. Le recomiendo coordinar con la entidad un horario compatible antes de iniciar el trámite.
```

### VC_SUPERVISOR
```
La entidad debe contar con un Ingeniero de Sistemas o de carrera afín que supervise sus prácticas. Si no lo tiene, esa entidad no es válida para sus PPP.
```

### VC_AREA
```
Sus prácticas deben realizarse en un área válida: desarrollo de sistemas; infraestructura, redes y comunicaciones; seguridad y auditoría; gestión de TIC; o gestión de proyectos. Le recomiendo confirmar con la entidad que sus funciones correspondan a una de ellas.
```

### VC_OK
```
Usted cumple las condiciones para iniciar sus prácticas. El primer paso es conseguir la carta de aceptación de la entidad y solicitar la carta de presentación.
¿Desea ver los requisitos de la carta de presentación?
```

---

## Diagnóstico de etapa (Flujo 2)

Preguntas del flujo, en orden:
```
DX_Q0: Le ayudo a ubicar su etapa. ¿Ya tiene una entidad que lo acepte como practicante?
DX_Q1: ¿Ya recibió la carta de presentación de la Facultad?
DX_Q2: ¿Su Plan de PPP ya fue aprobado?
DX_Q2b: ¿Ya inició sus prácticas en la entidad?
DX_Q3: ¿Ya cumplió las 600 horas?
DX_Q4: ¿Ya envió su informe final?
DX_Q5: ¿Ya recibió la resolución de la Facultad?
```

### DX_E01
```
Usted está en la Etapa 1, Carta de presentación. Necesita la carta de aceptación de la entidad (Anexo 03) y su carta de compromiso (Anexo 02). Solicite el trámite en el sistema UDH, pague S/ 5.00 y envíe los anexos a secretaria.fac.ing@udh.edu.pe.
¿Desea ver los pasos completos?
```

### DX_E02
```
Usted está en la Etapa 2, Plan de PPP. Presente la carta de presentación a la entidad y elabore su Plan según el Anexo 04. Recuerde que tendrá como máximo 15 días calendario desde el inicio de su práctica para presentarlo a comision.practicas.isi@udh.edu.pe.
¿Desea ver los requisitos del Plan?
```

### DX_E02_ALERTA
```
Usted está en la Etapa 2, Plan de PPP. Tiene como máximo 15 días calendario desde el inicio de su práctica para presentar el Plan, así que le recomiendo enviarlo cuanto antes a comision.practicas.isi@udh.edu.pe.
¿Desea ver los requisitos del Plan?
```

### DX_E03
```
Usted está en la Etapa 3, Ejecución. Debe completar las 600 horas efectivas, registrar su asistencia firmada y sellada por la entidad y asistir a las reuniones con su Asesor–Supervisor. En esta etapa usted no envía documentos.
¿Desea saber qué documentos necesitará al terminar?
```

### DX_E04
```
Usted está en la Etapa 4, Informe final. Tiene 20 días hábiles desde que concluyó sus prácticas para enviar su expediente en PDF a secretaria.sistemas.hco@udh.edu.pe.
¿Desea ver la lista de documentos del expediente?
```

### DX_E04_EVAL
```
Su expediente está en evaluación. La Comisión de PPP lo revisa y toma la sustentación; luego el Programa Académico lo eleva a la Facultad, que emite la resolución. Si recibe observaciones tras la sustentación, tiene 10 días hábiles para subsanarlas.
¿Desea saber cómo es la sustentación?
```

### DX_FIN
```
Sus prácticas están concluidas. Con la resolución de aprobación de la Facultad puede continuar con el trámite del Grado de Bachiller.
¿Desea conocer ese proceso?
```

---

## Requisitos por etapa

### PPP_requisitos_etapa · carta_presentacion
```
Requisitos de la Etapa 1, Carta de presentación:
- Carta de aceptación de la entidad receptora (Anexo 03).
- Carta de compromiso (Anexo 02).

Envíelos a secretaria.fac.ing@udh.edu.pe.
¿Desea conocer los pasos de esta etapa?
```

### PPP_requisitos_etapa · plan
```
Requisitos de la Etapa 2, Plan de PPP:
- Plan de PPP (Anexo 04).
- Carta de presentación.
- Carta de compromiso (Anexo 02).
- Carta de aceptación de la entidad (Anexo 03).

Envíelos a comision.practicas.isi@udh.edu.pe.
¿Desea conocer los pasos de esta etapa?
```

### PPP_requisitos_etapa · ejecucion
```
Para la Etapa 3, Ejecución, necesita tener su Plan aprobado y un Asesor–Supervisor designado. Durante esta etapa debe:
- Cumplir las 600 horas efectivas.
- Registrar su asistencia en un formato firmado y sellado por la entidad.

En esta etapa no envía documentos.
¿Desea saber qué necesitará para el informe final?
```

### PPP_requisitos_etapa · informe_final
```
Requisitos de la Etapa 4, Informe final (todo en PDF):
- Constancia de PPP de la entidad, con fechas de inicio y término, y labores realizadas.
- Ficha de evaluación del jefe de área (Anexo 06).
- Informe de PPP según el Anexo 05.
- Ficha de supervisión firmada y sellada por su Asesor–Supervisor (Anexo 07).
- Formato de asistencia firmado y sellado por la entidad.
- Constancia de inscripción en Seguimiento del Graduado.

Envíelos a secretaria.sistemas.hco@udh.edu.pe.
¿Desea conocer los pasos de esta etapa?
```

---

## Pasos por etapa

### PPP_pasos_etapa · carta_presentacion
```
Pasos de la Etapa 1, Carta de presentación:
1. Obtenga la carta de aceptación de la entidad (Anexo 03).
2. Elabore su carta de compromiso (Anexo 02).
3. Solicite el trámite de carta de presentación en el sistema UDH.
4. Pague S/ 5.00.
5. Envíe los anexos a secretaria.fac.ing@udh.edu.pe.
6. Matrícula y Tesorería verifican; luego la Facultad emite su carta y la envía a su correo institucional.

¿Desea ver la Etapa 2, Plan de PPP?
```

### PPP_pasos_etapa · plan
```
Pasos de la Etapa 2, Plan de PPP:
1. Presente la carta de presentación a la entidad.
2. Elabore su Plan según el Anexo 04.
3. Solicite «Aprobación de Plan de PPP» en el sistema UDH.
4. Envíe los requisitos a comision.practicas.isi@udh.edu.pe.
5. El Programa Académico lo deriva a la Comisión de PPP, que aprueba u observa su Plan.
6. Si lo aprueba, la Comisión le designa un Asesor–Supervisor.

Plazo: 15 días calendario desde el inicio de su práctica; 7 días hábiles para subsanar.
¿Desea ver la Etapa 3, Ejecución?
```

### PPP_pasos_etapa · ejecucion
```
Pasos de la Etapa 3, Ejecución:
1. Cumpla las 600 horas efectivas en la entidad.
2. Registre su asistencia en un formato firmado y sellado por la entidad.
3. Reúnase con su Asesor–Supervisor (mensualmente o como mínimo 2 veces) y esté en el centro de prácticas durante la supervisión.
4. Su Asesor–Supervisor eleva a la Comisión la Ficha de avances (Anexo 10) y la Ficha de supervisión (Anexo 07).

¿Desea ver la Etapa 4, Informe final?
```

### PPP_pasos_etapa · informe_final
```
Pasos de la Etapa 4, Informe final:
1. Reúna su expediente completo en PDF.
2. Solicite «Aprobación del informe final de PPP» en el sistema UDH.
3. Envíe el expediente a secretaria.sistemas.hco@udh.edu.pe.
4. El Programa Académico lo deriva a la Comisión de PPP, que evalúa el expediente.
5. Sustente ante la Comisión; la sustentación es obligatoria y pública.
6. La Comisión emite la constancia de aprobación y el Programa Académico eleva su expediente a la Facultad.
7. La Facultad aprueba sus prácticas mediante resolución.

Plazo: 20 días hábiles tras concluir sus prácticas; 10 días hábiles para subsanar tras la sustentación.
¿Desea saber qué sigue después?
```

---

## Correo por etapa

### PPP_correo_etapa · carta_presentacion
```
Para la Etapa 1, Carta de presentación, envíe los Anexos 02 y 03 a secretaria.fac.ing@udh.edu.pe.
¿Desea ver los requisitos de esta etapa?
```

### PPP_correo_etapa · plan
```
Para la Etapa 2, Plan de PPP, envíe sus documentos a comision.practicas.isi@udh.edu.pe. Tiene como máximo 15 días calendario desde el inicio de su práctica para presentarlo.
¿Desea ver los requisitos del Plan?
```

### PPP_correo_etapa · ejecucion
```
En la Etapa 3, Ejecución, usted no envía documentos. Las fichas de avance (Anexo 10) y de supervisión (Anexo 07) las eleva su Asesor–Supervisor a la Comisión.
```

### PPP_correo_etapa · informe_final
```
Para la Etapa 4, Informe final, envíe su expediente en PDF a secretaria.sistemas.hco@udh.edu.pe. Tiene 20 días hábiles desde que concluyó sus prácticas.
¿Desea ver la lista de documentos del expediente?
```

---

## Costos

### PPP_costo · (sin etapa)
```
Pagos del proceso de prácticas:
- Etapa 1, carta de presentación: S/ 5.00, al solicitar el trámite en el sistema UDH.
- Etapa 3, ejecución: no tiene pago.
- Etapas 2 y 4: la información oficial no indica un monto. Para confirmarlo, escriba a secretaria.sistemas.hco@udh.edu.pe.
```

### PPP_costo · carta_presentacion
```
La carta de presentación cuesta S/ 5.00. El pago se realiza al solicitar el trámite en el sistema UDH.
```

### PPP_costo · plan
→ usar `DATO_PENDIENTE`.

### PPP_costo · ejecucion
```
La Etapa 3, Ejecución, no tiene pago.
```

### PPP_costo · informe_final
→ usar `DATO_PENDIENTE`.

---

## Plazos

### PPP_plazo · (sin etapa)
```
Plazos de las prácticas:
- Plan de PPP: máximo 15 días calendario desde el inicio de la práctica.
- Subsanar el Plan: 7 días hábiles.
- Informe final: 20 días hábiles después de concluir la práctica.
- Subsanar tras la sustentación: 10 días hábiles.

Si no subsana a tiempo, la práctica se anula.
```

### PPP_plazo · carta_presentacion
→ usar `DATO_PENDIENTE`.

### PPP_plazo · plan
```
Tiene como máximo 15 días calendario desde el inicio de su práctica para presentar el Plan. Si se lo observan, tiene 7 días hábiles para subsanar; si no lo hace, la práctica se anula y podrá reiniciarla en 30 días calendario en otra entidad.
```

### PPP_plazo · ejecucion
```
Durante la ejecución debe reunirse con su Asesor–Supervisor mensualmente o como mínimo 2 veces. Tenga en cuenta que 3 faltas consecutivas o 5 alternadas sin justificar anulan la práctica.
```

### PPP_plazo · informe_final
```
Tiene 20 días hábiles desde que concluyó sus prácticas para presentar el informe final. Si recibe observaciones tras la sustentación, tiene 10 días hábiles para subsanarlas; si no lo hace, la práctica se anula.
```

---

## Anexos

### PPP_anexo_info · 02
```
El Anexo 02 es la carta de compromiso. La elabora usted y se presenta en la Etapa 1 (carta de presentación) y en la Etapa 2 (Plan de PPP).
```

### PPP_anexo_info · 03
```
El Anexo 03 es la carta de aceptación. La emite la entidad donde realizará sus prácticas y se presenta en la Etapa 1 y en la Etapa 2.
```

### PPP_anexo_info · 04
```
El Anexo 04 es el formato del Plan de PPP. Lo elabora usted y se presenta en la Etapa 2 a comision.practicas.isi@udh.edu.pe.
```

### PPP_anexo_info · 05
```
El Anexo 05 es la estructura que debe seguir su informe de PPP. Se presenta en la Etapa 4, dentro del expediente final.
```

### PPP_anexo_info · 06
```
El Anexo 06 es la ficha de evaluación que llena el jefe de área de la entidad. Se presenta en la Etapa 4, dentro del expediente final.
```

### PPP_anexo_info · 07
```
El Anexo 07 es la ficha de supervisión y evaluación. La firma y sella su Asesor–Supervisor; él la eleva a la Comisión durante la ejecución y usted la incluye en el expediente final.
```

### PPP_anexo_info · 10
```
El Anexo 10 es la ficha de avances. La eleva su Asesor–Supervisor a la Comisión durante la Etapa 3, Ejecución.
```

### PPP_anexo_info · 01
```
El Anexo 01 (solicitud de practicante) no se exige en el proceso actual.
```

### PPP_anexo_info · 08 / 09
→ usar `DESVIO_CPP`.

### PPP_anexo_info · descarga
→ usar `DATO_PENDIENTE`.

---

## Asesor–Supervisor, sustentación y anulación

### PPP_asesor_supervisor
```
El Asesor–Supervisor es un docente que designa la Comisión de PPP cuando aprueba su Plan. Su función es:
- Acompañar y supervisar sus prácticas.
- Reunirse con usted mensualmente o como mínimo 2 veces.
- Elevar a la Comisión la Ficha de avances (Anexo 10) y la Ficha de supervisión (Anexo 07).

Usted debe estar en el centro de prácticas durante la supervisión; si no está, la práctica puede anularse.
```

### PPP_sustentacion
```
La sustentación de sus prácticas es obligatoria y pública, y se realiza ante la Comisión de PPP después de enviar su informe final. Para aprobar se requiere el informe de su Asesor–Supervisor, la evaluación de la Comisión y la constancia de sustentación.
Si recibe observaciones, tiene 10 días hábiles para subsanarlas.
```
Si pregunta por fecha o modalidad (virtual o presencial) → usar `DATO_PENDIENTE`.

### PPP_anulacion
```
Sus prácticas pueden anularse por:
- Incumplir el reglamento de PPP.
- Presentar documentos falsificados o un informe plagiado.
- Tener 3 faltas consecutivas o 5 alternadas sin justificar.
- No estar en el centro de prácticas durante la supervisión.
- Recibir un informe de desaprobación del tutor o del supervisor.
- No subsanar a tiempo las observaciones del Plan (7 días hábiles) o de la sustentación (10 días hábiles).

Si se anula por no subsanar el Plan, puede reiniciarla en 30 días calendario en otra entidad.
```

---

## Estado del trámite

### PPP_estado_tramite · (sin etapa)
```
La carta de presentación llega a su correo institucional. Para conocer el estado de su Plan o de su informe final, la información oficial no indica un medio de seguimiento; le recomiendo consultarlo en secretaria.sistemas.hco@udh.edu.pe.
```

### PPP_estado_tramite · carta_presentacion
```
La Facultad envía la carta de presentación a su correo institucional, después de que Matrícula y Tesorería verifican su trámite. Revise su cuenta institucional.
```

### PPP_estado_tramite · plan
→ usar `DATO_PENDIENTE`.

### PPP_estado_tramite · informe_final
→ usar `DATO_PENDIENTE`.

---

## Siguiente paso

### PPP_siguiente_paso
```
Cuando la Comisión aprueba su sustentación, el Programa Académico eleva su expediente y la Facultad de Ingeniería aprueba sus prácticas mediante resolución.
Con sus prácticas aprobadas puede iniciar el trámite del Grado de Bachiller. ¿Desea conocer ese proceso?
```

---

## Respuestas comunes

### REPREGUNTA_ETAPA
```
¿De qué etapa se trata? 1) Carta de presentación, 2) Plan de PPP, 3) Ejecución o 4) Informe final.
```

### REPREGUNTA_ETAPA_2
```
No logré identificar la etapa. Por favor, responda con un número del 1 al 4:
1) Carta de presentación
2) Plan de PPP
3) Ejecución
4) Informe final
```

### REPREGUNTA_ANEXO
```
¿Qué anexo desea consultar? Los anexos de prácticas son: 02, 03, 04, 05, 06, 07 y 10.
```

### DATO_PENDIENTE
```
Ese dato aún no está confirmado en la información oficial. Para no darle información incorrecta, le recomiendo consultarlo en secretaria.sistemas.hco@udh.edu.pe.
```

### DESVIO_CPP
```
Si usted ya trabajó 16 meses o más en labores de la especialidad, puede convalidar sus prácticas en lugar de realizarlas. ¿Desea conocer ese trámite?
```

### DESVIO_TRA
```
La convalidación de cursos por traslado es un trámite distinto al de prácticas. ¿Desea conocer ese proceso?
```

### DESVIO_BAC
```
El Grado de Bachiller es el trámite que sigue después de aprobar sus prácticas. ¿Desea conocer ese proceso?
```
