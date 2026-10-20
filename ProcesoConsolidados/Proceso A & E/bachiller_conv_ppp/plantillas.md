# Plantillas de respuesta — Proceso E: Grado de Bachiller y Convalidación de PPP

Las variables entre `{{ }}` se rellenan **solo** con campos de la ficha indicada. Si un campo dice «No indicado» o la ficha está en `estado: pendiente`, se usa `PL_PENDIENTE` y nunca se inventa el dato.

## Plantillas comunes

### PL_FALTA_ENTIDAD
> Para ayudarte mejor: {{intent.si_falta_entidad}}

### PL_DESAMBIGUAR
> «Convalidación» puede referirse a dos trámites distintos:
> 1. **Convalidar tus Prácticas Preprofesionales (PPP)** con tu experiencia laboral.
> 2. **Convalidar cursos** por traslado interno o externo.
>
> ¿Cuál de los dos necesitas?

### PL_PENDIENTE
> {{lo_confirmado_de_la_ficha}}
>
> ⚠️ **{{dato_pendiente}}** aún no está confirmado en las fuentes oficiales del Programa. Te recomiendo consultarlo directamente con la Coordinación del P.A. de Ingeniería de Sistemas e Informática (952069136 · Carretera Central Km 2.5, La Esperanza).

### PL_SIGUIENTE
> ¿Quieres que te explique el siguiente paso ({{ficha.siguiente_fase.titulo}})?

### PL_CIERRE
> ¡Listo! Si tienes otra consulta sobre tu Bachiller o la convalidación de tus prácticas, escríbeme. Recuerda revisar tu correo institucional durante todo el trámite. 👋

---

## Grado de Bachiller

### PL_BAC_INFO_GENERAL — `BAC_info_general` · fichas BAC_P01–BAC_P06
> El Grado de Bachiller se tramita de forma **virtual** en 6 pasos:
> 1. **Plataforma:** en *Trámite de Grados y Títulos*, elige «Optar el Grado Académico de Bachiller».
> 2. **Fotos:** sube una foto tamaño pasaporte (fondo blanco, vestimenta formal) y entrega 2 fotos físicas de 4 cm x 5 cm en la oficina de Ingeniería de Sistemas e Informática.
> 3. **Correo:** envía tu DNI ampliado vigente y la foto a `ana.trujillo@udh.edu.pe` con el asunto «DNI- FOTO para Bachiller».
> 4. **Verificación:** en *Académico → Consulta Registro de Grados y Títulos*, revisa que cada oficina atienda tus requisitos.
> 5. **Comisión:** arma tu expediente digital, lo evalúa y lo envía al Consejo de Facultad (inicio de cada mes).
> 6. **Consejo Universitario:** instancia final del grado.
>
> ¿Quieres el detalle de algún paso?

### PL_BAC_PASO — `BAC_requisitos_paso` · ficha BAC_P{{paso}}
> **Paso {{ficha.fase}} — {{ficha.titulo}}**
>
> **Requisitos:** {{ficha.requisitos}}
> **Qué hacer:** {{ficha.pasos}}
> **Dónde:** {{ficha.enviar_a}}
>
> {{PL_SIGUIENTE}}

### PL_BAC_FOTOS — `BAC_fotos` · ficha BAC_P02
> Para el Bachiller necesitas:
> - **Foto digital:** tamaño pasaporte, fondo blanco y vestimenta formal; se sube al sistema *Trámite de Grados y Títulos*.
> - **Fotos físicas:** 2 unidades de **4 cm x 5 cm** (la misma foto), que se entregan en la oficina de Ingeniería de Sistemas e Informática.

### PL_BAC_CORREO — `BAC_envio_correo` · ficha BAC_P03
> Envía un correo a **`ana.trujillo@udh.edu.pe`** con el asunto exacto **«DNI- FOTO para Bachiller»** y adjunta:
> - DNI ampliado vigente.
> - Foto con fondo blanco, tamaño pasaporte, con vestimenta formal.

### PL_BAC_SEGUIMIENTO — `BAC_seguimiento` · ficha BAC_P04
> Para ver el avance de tu Bachiller, entra a **Académico → Consulta Registro de Grados y Títulos** y verifica que cada oficina haya atendido los requisitos que el sistema generó automáticamente.
> Si alguna oficina te envía un documento a tu correo institucional, **reenvíalo al correo de la Comisión**.
>
> ⚠️ La lista de requisitos que genera la plataforma y la dirección del correo de la Comisión aún no están confirmadas; consúltalas con Coordinación.

### PL_BAC_PLAZOS — `BAC_plazos_consejo` · fichas BAC_P05, BAC_P06
> Con tus requisitos completos, la Comisión evalúa tu expediente y lo envía al **siguiente Consejo de Facultad, que se realiza al inicio de cada mes**. Si no llega a tiempo, pasa al Consejo del mes siguiente. Luego el trámite pasa al **Consejo Universitario**.
>
> ⚠️ Los plazos de cada etapa y la forma de entrega de la resolución del grado no están indicados en las fuentes; consúltalos con Coordinación.

### PL_BAC_COSTO — `BAC_costo` · ficha BAC_P01
> Las fuentes oficiales del trámite de Bachiller **no indican montos de pago**. Los requisitos (incluidos posibles pagos) los genera automáticamente la plataforma al registrar tu solicitud; revísalos en *Consulta Registro de Grados y Títulos* o consulta con Coordinación.

### PL_BAC_PRERREQUISITO — `BAC_prerrequisito_ppp` · ficha BAC_P01
> Sí: las **Prácticas Preprofesionales (PPP) son requisito obligatorio del Grado de Bachiller** y no tienen exoneración. Puedes cumplirlas realizando la PPP regular o, si trabajaste al menos 16 meses en la especialidad, **convalidándolas por experiencia laboral**. ¿Quieres saber cómo convalidarlas?

---

## Convalidación de PPP por experiencia laboral

### PL_CPP_CONDICIONES — `CPP_condiciones` · ficha CPP_E00
> Puedes convalidar tus PPP si acreditas:
> - Haber laborado **no menos de 16 meses** en labores vinculadas a la especialidad.
> - Como **nombrado o contratado** en una institución **pública o privada**.
> - Y aceptar una **exposición obligatoria** ante la Comisión de PPP.
>
> ⚠️ El ciclo mínimo aún no está confirmado: el reglamento (Art. 31) pide el **sexto ciclo concluido** y el flujograma indica **VII ciclo**. Consúltalo con Coordinación.

### PL_CPP_EXPEDIENTE — `CPP_requisitos_expediente` · ficha CPP_E01
> El expediente de convalidación (Art. 32) lleva:
> 1. Solicitud al Coordinador del P.A. pidiendo la convalidación (**Anexo 08**).
> 2. Constancia(s) de trabajo o contrato(s) original(es), con tipo de trabajo, fecha de ingreso y duración.
> 3. Boletas de pago de haberes de cada institución donde laboraste.
> 4. Ficha de evaluación del jefe, director o representante, con cargo y firma.
> 5. Informe técnico según el esquema del **Anexo 09**.
> 6. Recibo de pago por derecho de trámite documentario.

### PL_CPP_ENVIO — `CPP_envio_expediente` · ficha CPP_E01
> 1. Solicita la convalidación en el **sistema UDH**.
> 2. Envía el expediente completo a **`secretaria.sistemas.hco@udh.edu.pe`**.
>
> El P.A. verifica tus requisitos y deriva el expediente a la Comisión de PPP.

### PL_CPP_PLAZO — `CPP_plazo` · ficha CPP_E01
> Tienes un **máximo de 20 días** para presentar el informe.
>
> ⚠️ Desde cuándo corren esos 20 días y si son hábiles o calendario aún no está confirmado; tampoco se indican plazos para la evaluación de la Comisión ni para la resolución. Consúltalo con Coordinación.

### PL_CPP_COSTO — `CPP_costo` · ficha CPP_E01
> La convalidación exige un **recibo de pago por derecho de trámite documentario**, pero el **monto no está indicado** en las fuentes oficiales. Consúltalo con Coordinación antes de pagar.

### PL_CPP_SUSTENTACION — `CPP_sustentacion` · ficha CPP_E03
> La **Comisión de PPP** evalúa tu expediente y luego tu **exposición (sustentación) de la convalidación, que es obligatoria** y se coordina con el jefe de prácticas. Si apruebas, la Comisión emite la **constancia de aprobación de la PPP**.

### PL_CPP_RESULTADO — `CPP_resultado` · ficha CPP_E04
> Tras la constancia de la Comisión, el P.A. eleva tu expediente a la **Facultad de Ingeniería**, que **aprueba la convalidación mediante resolución**.
> Con tu PPP convalidada ya puedes tramitar tu **Grado de Bachiller**. ¿Te explico cómo?

### PL_CPP_ETAPA — `CPP_etapa_info` · ficha CPP_E{{etapa}}
> **Etapa {{ficha.fase}} — {{ficha.titulo}}**
>
> **Qué ocurre:** {{ficha.pasos}}
> **Requisitos:** {{ficha.requisitos}}
> **Enviar a:** {{ficha.enviar_a}}
>
> {{PL_SIGUIENTE}}
