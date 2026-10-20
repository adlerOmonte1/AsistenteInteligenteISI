# Plantillas de respuesta — traslados generales

## Reglas de uso

Las respuestas entre comillas son textos para estudiantes. Las referencias técnicas sirven para integrar el diseño; no se muestran como códigos al estudiante. No usar una variable sin resolver ni rellenarla con texto inventado. Antes de enviar una respuesta, validar el contexto y la presencia del dato en la ficha seleccionada. Todos los datos mantienen la atribución a los documentos aportados y la vigencia institucional pendiente.

Las listas de fichas son candidatas: seleccionar exclusivamente el proceso consultado. La comparación explícita es la única excepción. En externo, adjuntar la advertencia de dirección cuando afecte la aplicabilidad. Para copiar el certificado original o presentar una copia, prevalece la fase 4 sobre la fase 1.

## Diccionario de variables

| Variable | Origen o regla |
|---|---|
| `{tipo_traslado}` | Entidad resuelta: traslado interno o externo. |
| `{fuente}` | `fuente` de la ficha seleccionada; se muestra el nombre del documento. |
| `{titulo}` | `titulo` de la ficha seleccionada. |
| `{requisitos}` | `datos.requisitos`; conservar todas las condiciones, incluida la copia autenticada. |
| `{pasos}` | `datos.pasos`, expresados en lenguaje natural y en el mismo orden. |
| `{pagos}` | `datos.pagos`, con moneda PEN, monto y unidad. Una lista vacía significa costo no indicado. |
| `{pagos_consultados}` | Subconjunto de `datos.pagos` correspondiente a `concepto_pago`, o unión de F01/F03/F05 si se solicitan todos. No eliminar la unidad por ciclo o por sílabo. |
| `{plazo}` | `datos.plazo`; nulo conduce a información pendiente. Conservar aproximadamente y días hábiles. |
| `{responsable}` | `datos.responsable`. |
| `{enviar_a}` | `datos.enviar_a`; no agregar direcciones, URLs ni horarios. |
| `{titulo_siguiente}`, `{pasos_siguientes}`, `{fuente_siguiente}` | Seguir `siguiente_fase`; leer `titulo`, `datos.pasos` y `fuente` de esa ficha. |
| `{secuencia_fases}` | Ordenar fichas por `fase` dentro del proceso; resumir títulos sin modificar el orden. |
| `{comparacion_documentada}` | Contrastar ruta de F05 y cierre de INT F07 frente a EXT F06/F07. No inferir diferencias no documentadas. |
| `{dato_a_aclarar}`, `{pregunta_aclaratoria}` | Regla de diálogo: concepto de pago, etapa o tipo faltante. No son hechos administrativos. |
| `{dato_pendiente}` | Ausencia o reserva respaldada por `pendientes.md` y la ficha consultada. |

## Catálogo

### TRA_P_BIENVENIDA — Bienvenida

- **Identificador:** `TRA_P_BIENVENIDA`.
- **Nombre:** Bienvenida.
- **Intent asociado:** NO_APLICA; acción TRA_ACC_bienvenida.
- **Entidades necesarias:** Ninguna.
- **Ficha fuente:** NO_APLICA: acción conversacional sin hechos administrativos propios.
- **Condición de uso:** Inicio de conversación.
- **Respuesta:** «Hola. Te ayudo a consultar los documentos sobre traslados y convalidación de cursos en la UDH.»
- **Pregunta de seguimiento:** ¿Tu consulta es sobre traslado interno o externo?
- **Si falta información:** Usar TRA_P_TIPO si no se identifica el proceso.

### TRA_P_TIPO — Identificación del tipo

- **Identificador:** `TRA_P_TIPO`.
- **Nombre:** Identificación del tipo.
- **Intent asociado:** TRA_tipo_traslado.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** NO_APLICA: acción conversacional sin hechos administrativos propios.
- **Condición de uso:** Falta el tipo y la respuesta depende de él.
- **Respuesta:** «Para orientarte, necesito identificar el procedimiento.»
- **Pregunta de seguimiento:** ¿Tu consulta es sobre traslado interno o externo?
- **Si falta información:** No asumir el tipo por cambiar de carrera o de universidad. Contar una respuesta inválida como un fallo.

### TRA_P_DESAMBIGUACION — Desambiguación específica

- **Identificador:** `TRA_P_DESAMBIGUACION`.
- **Nombre:** Desambiguación específica.
- **Intent asociado:** TRA_costo; TRA_plazo; TRA_siguiente_fase.
- **Entidades necesarias:** tipo_traslado; concepto_pago o fase según consulta
- **Ficha fuente:** NO_APLICA: acción conversacional sin hechos administrativos propios.
- **Condición de uso:** Se comprende la intención, pero falta un dato indispensable.
- **Respuesta:** «Para responder sobre {tipo_traslado}, necesito precisar {dato_a_aclarar}.»
- **Pregunta de seguimiento:** {pregunta_aclaratoria}
- **Si falta información:** Ofrecer solo conceptos o etapas existentes; tras dos respuestas inválidas aplicar GEN_derivar_humano.

### TRA_P_REQUISITOS — Requisitos documentales

- **Identificador:** `TRA_P_REQUISITOS`.
- **Nombre:** Requisitos documentales.
- **Intent asociado:** TRA_requisitos.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F04](fichas/TRA_INT_F04.md), [TRA_EXT_F04](fichas/TRA_EXT_F04.md)
- **Condición de uso:** Se piden los requisitos generales.
- **Respuesta:** «Según {fuente}, para {tipo_traslado} debes presentar: {requisitos}. La vigencia de esta información está pendiente de confirmación institucional.»
- **Pregunta de seguimiento:** ¿Deseas saber dónde se presentan o cómo obtener uno de los documentos?
- **Si falta información:** Si falta tipo, preguntar. Los requisitos no confirmados se remiten a TRA_P_PENDIENTE.

### TRA_P_CERTIFICADO — Certificado de Estudios

- **Identificador:** `TRA_P_CERTIFICADO`.
- **Nombre:** Certificado de Estudios.
- **Intent asociado:** TRA_certificado.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F01](fichas/TRA_INT_F01.md), [TRA_EXT_F01](fichas/TRA_EXT_F01.md)
- **Condición de uso:** Consulta de solicitud del certificado.
- **Respuesta:** «El documento {fuente} indica solicitar el Certificado de Estudios en el Sistema Login UDH. Los pagos descritos son: {pagos}. Su vigencia requiere confirmación.»
- **Pregunta de seguimiento:** ¿Deseas consultar la Constancia de Ingreso o la forma de presentar el certificado?
- **Si falta información:** Si se pregunta por original o copia, recuperar F04 del proceso y usar TRA_P_REQUISITOS. Si falta medio de pago, usar TRA_P_PENDIENTE.

### TRA_P_CONSTANCIA — Constancia de Ingreso

- **Identificador:** `TRA_P_CONSTANCIA`.
- **Nombre:** Constancia de Ingreso.
- **Intent asociado:** TRA_constancia.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F02](fichas/TRA_INT_F02.md), [TRA_EXT_F02](fichas/TRA_EXT_F02.md)
- **Condición de uso:** Consulta cómo o ante quién obtener la constancia.
- **Respuesta:** «Según {fuente}, la Constancia de Ingreso es emitida por {responsable}. El plazo descrito es {plazo}.»
- **Pregunta de seguimiento:** ¿Deseas conocer la siguiente etapa?
- **Si falta información:** Costo, requisitos específicos y canal no indicados: explicar la ausencia, sin afirmar gratuidad.

### TRA_P_SILABOS — Sílabos académicos

- **Identificador:** `TRA_P_SILABOS`.
- **Nombre:** Sílabos académicos.
- **Intent asociado:** TRA_silabos.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F03](fichas/TRA_INT_F03.md), [TRA_EXT_F03](fichas/TRA_EXT_F03.md)
- **Condición de uso:** Consulta obtención o formalidades de los sílabos.
- **Respuesta:** «Según {fuente}, solicita los sílabos de los cursos a convalidar. Deben estar sellados y firmados por la autoridad competente. Los pagos descritos son: {pagos}. La oficina exacta está pendiente de confirmación.»
- **Pregunta de seguimiento:** ¿Quieres conocer dónde se presenta la documentación?
- **Si falta información:** No inventar la oficina, la autoridad firmante ni el tiempo de entrega; orientar a Coordinación para confirmarlos.

### TRA_P_COSTO — Costo por concepto

- **Identificador:** `TRA_P_COSTO`.
- **Nombre:** Costo por concepto.
- **Intent asociado:** TRA_costo.
- **Entidades necesarias:** tipo_traslado; concepto_pago si se pide un pago concreto
- **Ficha fuente:** [TRA_INT_F01](fichas/TRA_INT_F01.md), [TRA_EXT_F01](fichas/TRA_EXT_F01.md), [TRA_INT_F03](fichas/TRA_INT_F03.md), [TRA_EXT_F03](fichas/TRA_EXT_F03.md), [TRA_INT_F05](fichas/TRA_INT_F05.md), [TRA_EXT_F05](fichas/TRA_EXT_F05.md)
- **Condición de uso:** Concepto identificado o solicitud explícita de todos los pagos.
- **Respuesta:** «Para {tipo_traslado}, el documento {fuente} indica {pagos_consultados}. La vigencia del tarifario no está confirmada.»
- **Pregunta de seguimiento:** ¿Quieres consultar los otros conceptos o los pasos del procedimiento?
- **Si falta información:** Si S/ 5 no identifica el concepto, preguntar si se refiere al derecho del certificado o a la solicitud de convalidación. Para un concepto sin precio documentado, usar TRA_P_PENDIENTE con la ficha pertinente.

### TRA_P_PLAZO — Plazos aproximados

- **Identificador:** `TRA_P_PLAZO`.
- **Nombre:** Plazos aproximados.
- **Intent asociado:** TRA_plazo.
- **Entidades necesarias:** tipo_traslado; fase o documento si el alcance es ambiguo
- **Ficha fuente:** [TRA_INT_F01](fichas/TRA_INT_F01.md), [TRA_EXT_F01](fichas/TRA_EXT_F01.md), [TRA_INT_F02](fichas/TRA_INT_F02.md), [TRA_EXT_F02](fichas/TRA_EXT_F02.md), [TRA_INT_F03](fichas/TRA_INT_F03.md), [TRA_EXT_F03](fichas/TRA_EXT_F03.md), [TRA_INT_F04](fichas/TRA_INT_F04.md), [TRA_EXT_F04](fichas/TRA_EXT_F04.md), [TRA_INT_F05](fichas/TRA_INT_F05.md), [TRA_EXT_F05](fichas/TRA_EXT_F05.md), [TRA_INT_F06](fichas/TRA_INT_F06.md), [TRA_EXT_F06](fichas/TRA_EXT_F06.md), [TRA_INT_F07](fichas/TRA_INT_F07.md), [TRA_EXT_F07](fichas/TRA_EXT_F07.md)
- **Condición de uso:** Etapa identificada y datos.plazo no es nulo.
- **Respuesta:** «Según {fuente}, el plazo descrito para {titulo} es {plazo}. Es una duración aproximada; no permite asegurar el tiempo total del trámite.»
- **Pregunta de seguimiento:** ¿Deseas revisar otra etapa?
- **Si falta información:** Si datos.plazo es nulo, indicarlo. Si se pregunta por duración total sin etapa, pedir precisión; no sumar tiempos parciales.

### TRA_P_PRESENTACION — Entrega de documentos

- **Identificador:** `TRA_P_PRESENTACION`.
- **Nombre:** Entrega de documentos.
- **Intent asociado:** TRA_presentacion.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F04](fichas/TRA_INT_F04.md), [TRA_EXT_F04](fichas/TRA_EXT_F04.md)
- **Condición de uso:** Consulta por el lugar de entrega.
- **Respuesta:** «Según {fuente}, presenta {requisitos} en {enviar_a}. No se entrega el Certificado de Estudios original.»
- **Pregunta de seguimiento:** ¿Deseas conocer cómo registrar la convalidación después de la entrega?
- **Si falta información:** Ubicación específica, horario y canal físico/digital no indicados: no completar con supuestos.

### TRA_P_REGISTRO — Registro de la solicitud

- **Identificador:** `TRA_P_REGISTRO`.
- **Nombre:** Registro de la solicitud.
- **Intent asociado:** TRA_registro.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F05](fichas/TRA_INT_F05.md), [TRA_EXT_F05](fichas/TRA_EXT_F05.md)
- **Condición de uso:** Consulta por la ruta en Login tras la entrega documental.
- **Respuesta:** «Después de entregar los documentos, {fuente} indica la ruta {enviar_a}. El pago descrito es {pagos}. Su vigencia está pendiente de confirmación.»
- **Pregunta de seguimiento:** ¿Deseas conocer la evaluación de la solicitud?
- **Si falta información:** Si el proceso no está identificado, preguntar antes de mostrar Interno o Externo. En externo, no prometer la aplicabilidad del procedimiento a una dirección no confirmada.

### TRA_P_EVALUACION — Evaluación académica

- **Identificador:** `TRA_P_EVALUACION`.
- **Nombre:** Evaluación académica.
- **Intent asociado:** TRA_evaluacion.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F06](fichas/TRA_INT_F06.md), [TRA_EXT_F06](fichas/TRA_EXT_F06.md)
- **Condición de uso:** Consulta por revisión académica en Coordinación.
- **Respuesta:** «Según {fuente}, la etapa {titulo} está a cargo de {responsable}. Comprende: {pasos}. El plazo indicado es {plazo}.»
- **Pregunta de seguimiento:** ¿Quieres consultar el resultado de esta etapa?
- **Si falta información:** No asegurar aprobación de cursos ni trasladar los criterios internos a la fase 6 externa. Condiciones precisas no documentadas: TRA_P_PENDIENTE.

### TRA_P_RESOLUCION — Emisión y envío de resolución

- **Identificador:** `TRA_P_RESOLUCION`.
- **Nombre:** Emisión y envío de resolución.
- **Intent asociado:** TRA_resolucion.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F07](fichas/TRA_INT_F07.md), [TRA_EXT_F06](fichas/TRA_EXT_F06.md)
- **Condición de uso:** Consulta por resolución de Coordinación.
- **Respuesta:** «Según {fuente}, Coordinación Académica emite la Resolución de Cursos Convalidados y la envía al correo electrónico registrado del estudiante.»
- **Pregunta de seguimiento:** ¿Deseas conocer si existe una etapa posterior en el procedimiento documentado?
- **Si falta información:** No inventar fecha exacta de envío ni afirmar que la resolución del estudiante ya fue emitida. En externo no garantizar reconocimiento automático en otra universidad.

### TRA_P_SIGUIENTE — Navegación a la siguiente fase

- **Identificador:** `TRA_P_SIGUIENTE`.
- **Nombre:** Navegación a la siguiente fase.
- **Intent asociado:** TRA_siguiente_fase.
- **Entidades necesarias:** tipo_traslado, fase
- **Ficha fuente:** [TRA_INT_F01](fichas/TRA_INT_F01.md), [TRA_EXT_F01](fichas/TRA_EXT_F01.md), [TRA_INT_F02](fichas/TRA_INT_F02.md), [TRA_EXT_F02](fichas/TRA_EXT_F02.md), [TRA_INT_F03](fichas/TRA_INT_F03.md), [TRA_EXT_F03](fichas/TRA_EXT_F03.md), [TRA_INT_F04](fichas/TRA_INT_F04.md), [TRA_EXT_F04](fichas/TRA_EXT_F04.md), [TRA_INT_F05](fichas/TRA_INT_F05.md), [TRA_EXT_F05](fichas/TRA_EXT_F05.md), [TRA_INT_F06](fichas/TRA_INT_F06.md), [TRA_EXT_F06](fichas/TRA_EXT_F06.md), [TRA_INT_F07](fichas/TRA_INT_F07.md), [TRA_EXT_F07](fichas/TRA_EXT_F07.md)
- **Condición de uso:** Fase activa y solicitud de avanzar; siguiente_fase no es nulo.
- **Respuesta:** «La siguiente etapa descrita es {titulo_siguiente}: {pasos_siguientes}. Información tomada de {fuente_siguiente}; vigencia pendiente de confirmación.»
- **Pregunta de seguimiento:** ¿Quieres consultar sus requisitos o continuar con otra etapa?
- **Si falta información:** Si falta fase, preguntar; si siguiente_fase es nulo, indicar fin documentado. No interpretar avanzar como registro ni finalización efectiva del trámite.

### TRA_P_DIFERENCIAS — Comparación de procedimientos

- **Identificador:** `TRA_P_DIFERENCIAS`.
- **Nombre:** Comparación de procedimientos.
- **Intent asociado:** TRA_diferencia.
- **Entidades necesarias:** Ninguna.
- **Ficha fuente:** [TRA_INT_F05](fichas/TRA_INT_F05.md), [TRA_EXT_F05](fichas/TRA_EXT_F05.md), [TRA_INT_F07](fichas/TRA_INT_F07.md), [TRA_EXT_F06](fichas/TRA_EXT_F06.md), [TRA_EXT_F07](fichas/TRA_EXT_F07.md)
- **Condición de uso:** Comparación explícita entre ambos procesos.
- **Respuesta:** «Según los documentos aportados, {comparacion_documentada}. El documento externo incluye una evaluación posterior en la universidad de destino; la dirección exacta del traslado está pendiente de confirmación con Coordinación.»
- **Pregunta de seguimiento:** ¿Deseas revisar el procedimiento interno o lo descrito en el documento externo?
- **Si falta información:** No inventar diferencias de costo, requisitos o condiciones de admisión. No equiparar la descripción externa a un ingreso confirmado a UDH.

### TRA_P_PENDIENTE — Información no confirmada

- **Identificador:** `TRA_P_PENDIENTE`.
- **Nombre:** Información no confirmada.
- **Intent asociado:** Intent original que motivó la consulta.
- **Entidades necesarias:** tipo_traslado si cambia la respuesta
- **Ficha fuente:** [TRA_INT_F01](fichas/TRA_INT_F01.md), [TRA_EXT_F01](fichas/TRA_EXT_F01.md), [TRA_INT_F02](fichas/TRA_INT_F02.md), [TRA_EXT_F02](fichas/TRA_EXT_F02.md), [TRA_INT_F03](fichas/TRA_INT_F03.md), [TRA_EXT_F03](fichas/TRA_EXT_F03.md), [TRA_INT_F04](fichas/TRA_INT_F04.md), [TRA_EXT_F04](fichas/TRA_EXT_F04.md), [TRA_INT_F05](fichas/TRA_INT_F05.md), [TRA_EXT_F05](fichas/TRA_EXT_F05.md), [TRA_INT_F06](fichas/TRA_INT_F06.md), [TRA_EXT_F06](fichas/TRA_EXT_F06.md), [TRA_INT_F07](fichas/TRA_INT_F07.md), [TRA_EXT_F07](fichas/TRA_EXT_F07.md)
- **Condición de uso:** La ficha no contiene el dato requerido o este necesita validación institucional.
- **Respuesta:** «El dato sobre {dato_pendiente} no está confirmado en {fuente}. Puedes solicitar su confirmación a Coordinación Académica.»
- **Pregunta de seguimiento:** ¿Quieres conocer la información que sí figura en el documento?
- **Si falta información:** Si no hay ficha por una ambigüedad, primero aclarar. No tratar una ausencia documental como fallo del usuario.

### TRA_P_NO_RECONOCIDA — Pregunta no reconocida

- **Identificador:** `TRA_P_NO_RECONOCIDA`.
- **Nombre:** Pregunta no reconocida.
- **Intent asociado:** NO_APLICA; acción TRA_ACC_desconocido.
- **Entidades necesarias:** Ninguna.
- **Ficha fuente:** NO_APLICA: acción conversacional sin hechos administrativos propios.
- **Condición de uso:** Primer fallo consecutivo de comprensión.
- **Respuesta:** «No pude identificar tu consulta. Puedo ayudarte con requisitos, costos, plazos y etapas de traslado.»
- **Pregunta de seguimiento:** ¿Qué dato sobre tu traslado interno o externo necesitas conocer?
- **Si falta información:** Al segundo fallo consecutivo pasar directamente a TRA_P_HUMANO; no repetir indefinidamente esta pregunta.

### TRA_P_HUMANO — Orientación a personal administrativo

- **Identificador:** `TRA_P_HUMANO`.
- **Nombre:** Orientación a personal administrativo.
- **Intent asociado:** GEN_derivar_humano.
- **Entidades necesarias:** Ninguna.
- **Ficha fuente:** NO_APLICA: acción conversacional sin hechos administrativos propios.
- **Condición de uso:** Petición explícita de persona o dos fallos consecutivos.
- **Respuesta:** «Te sugiero consultar con la Coordinación Académica del Programa Académico de Ingeniería de Sistemas e Informática. No tengo un correo ni un canal oficial confirmado para esta consulta.»
- **Pregunta de seguimiento:** Sin pregunta adicional obligatoria; cerrar la orientación.
- **Si falta información:** No copiar contactos del ejemplo de titulación ni afirmar que se realizó una transferencia o se envió un mensaje.

### TRA_P_CIERRE — Cierre de conversación

- **Identificador:** `TRA_P_CIERRE`.
- **Nombre:** Cierre de conversación.
- **Intent asociado:** NO_APLICA; acción TRA_ACC_cierre.
- **Entidades necesarias:** Ninguna.
- **Ficha fuente:** NO_APLICA: acción conversacional sin hechos administrativos propios.
- **Condición de uso:** Despedida, rechazo de continuar o fin del procedimiento documentado.
- **Respuesta:** «Gracias por consultar. Si tienes otra duda sobre los documentos de traslado, puedes volver a preguntar.»
- **Pregunta de seguimiento:** Sin seguimiento obligatorio.
- **Si falta información:** No afirmar que el trámite se completó; solo termina la conversación.

### TRA_P_PASOS — Resumen de la ruta documental

- **Identificador:** `TRA_P_PASOS`.
- **Nombre:** Resumen de la ruta documental.
- **Intent asociado:** TRA_pasos.
- **Entidades necesarias:** tipo_traslado; direccion_traslado para guía externa personalizada
- **Ficha fuente:** [TRA_INT_F01](fichas/TRA_INT_F01.md), [TRA_EXT_F01](fichas/TRA_EXT_F01.md), [TRA_INT_F02](fichas/TRA_INT_F02.md), [TRA_EXT_F02](fichas/TRA_EXT_F02.md), [TRA_INT_F03](fichas/TRA_INT_F03.md), [TRA_EXT_F03](fichas/TRA_EXT_F03.md), [TRA_INT_F04](fichas/TRA_INT_F04.md), [TRA_EXT_F04](fichas/TRA_EXT_F04.md), [TRA_INT_F05](fichas/TRA_INT_F05.md), [TRA_EXT_F05](fichas/TRA_EXT_F05.md), [TRA_INT_F06](fichas/TRA_INT_F06.md), [TRA_EXT_F06](fichas/TRA_EXT_F06.md), [TRA_INT_F07](fichas/TRA_INT_F07.md), [TRA_EXT_F07](fichas/TRA_EXT_F07.md)
- **Condición de uso:** Solicitud de procedimiento completo o punto de inicio.
- **Respuesta:** «Según {fuente}, la secuencia documentada de {tipo_traslado} es: {secuencia_fases}. Su vigencia está pendiente de confirmación.»
- **Pregunta de seguimiento:** ¿Qué etapa quieres consultar?
- **Si falta información:** En externo, antes de guía personalizada preguntar origen/destino y advertir el alcance pendiente. No exigir que el estudiante recorra todas las etapas para recibir una respuesta.

### TRA_P_ESTADO — Seguimiento sin acceso al expediente

- **Identificador:** `TRA_P_ESTADO`.
- **Nombre:** Seguimiento sin acceso al expediente.
- **Intent asociado:** TRA_estado.
- **Entidades necesarias:** tipo_traslado
- **Ficha fuente:** [TRA_INT_F05](fichas/TRA_INT_F05.md), [TRA_EXT_F05](fichas/TRA_EXT_F05.md)
- **Condición de uso:** Consulta sobre estado personal, seguimiento u observaciones.
- **Respuesta:** «No puedo consultar tu expediente. El documento {fuente} no especifica cómo verificar el estado ni cómo subsanar observaciones. Puedes pedir orientación a Coordinación Académica.»
- **Pregunta de seguimiento:** ¿Deseas revisar los pasos documentados de la solicitud?
- **Si falta información:** Guardar cualquier estado mencionado como declaración del estudiante. No inventar enlace de seguimiento, código de expediente ni estado verificado.

### TRA_P_DESTINO — Evaluación en la universidad de destino

- **Identificador:** `TRA_P_DESTINO`.
- **Nombre:** Evaluación en la universidad de destino.
- **Intent asociado:** TRA_destino.
- **Entidades necesarias:** tipo_traslado=externo
- **Ficha fuente:** [TRA_EXT_F07](fichas/TRA_EXT_F07.md)
- **Condición de uso:** Pregunta factual sobre la fase final del documento externo.
- **Respuesta:** «Según {fuente}, la universidad de destino revisa los cursos y los compara con su propia malla curricular, considerando sílabos, créditos y horas, y determina cuáles reconoce. La dirección y aplicabilidad de este procedimiento están pendientes de confirmación con Coordinación.»
- **Pregunta de seguimiento:** ¿Quieres revisar otra parte de lo descrito en el documento externo?
- **Si falta información:** Si se solicita guía personalizada y no hay dirección explícita, usar TRA_P_DIRECCION. Si el contexto activo es interno, aclarar la contradicción. No garantizar aceptación de todos los cursos.

### TRA_P_DIRECCION — Aclaración del sentido externo

- **Identificador:** `TRA_P_DIRECCION`.
- **Nombre:** Aclaración del sentido externo.
- **Intent asociado:** TRA_tipo_traslado; TRA_pasos; TRA_siguiente_fase; TRA_destino.
- **Entidades necesarias:** tipo_traslado=externo, direccion_traslado
- **Ficha fuente:** [TRA_EXT_F07](fichas/TRA_EXT_F07.md)
- **Condición de uso:** Orientación externa personalizada sin origen y destino conocidos.
- **Respuesta:** «El documento externo incluye una evaluación en la universidad de destino, pero no confirma inequívocamente el sentido del traslado.»
- **Pregunta de seguimiento:** ¿Te trasladas desde la UDH hacia otra universidad o desde otra institución hacia la UDH?
- **Si falta información:** Guardar la respuesta como mención del estudiante. Aunque aclare la dirección, indicar que Coordinación debe confirmar el procedimiento aplicable. Aplicar el límite de dos fallos para respuestas inválidas.

