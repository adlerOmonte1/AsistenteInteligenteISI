# Plantillas de respuesta para TSP

## Reglas comunes

Las fichas son la fuente interna de hechos. Resolver el contexto antes de renderizar una plantilla. Todas las respuestas se atribuyen a TrabajoSuficiencia.md; su vigencia institucional está pendiente. Los ejemplos son demostraciones concretas del diseño, no estados reales de un expediente. No mostrar variables sin resolver ni IDs internos al bachiller.

Los códigos TSP_P01–TSP_P14 corresponden a P01–P14 del encargo con el prefijo obligatorio del módulo. Los restantes cubren documentos, alcance, resoluciones, Repositorio, seguimiento, contacto y ejecución. GEN_derivar_humano es solo una referencia externa en TSP_P13.

## Origen de variables

| Variables | Extracción o regla |
|---|---|
| fase, fase_actual | fase de la ficha; si es 0, mostrar prerrequisito. |
| titulo, ficha_id | titulo e id de la ficha; ficha_id es trazabilidad interna. |
| requisitos, evidencias | datos.requisitos; mantener documentos y condiciones de cada etapa. |
| documentos | Subconjunto de datos.requisitos que expresa formato Word/PDF o especificaciones documentales. Si no existe, indicar formato no precisado sin inventarlo. |
| pasos, responsable | datos.pasos y actores que el propio texto identifica. |
| destino, destino_experiencia | datos.enviar_a. |
| concepto, monto | datos.pago.concepto y monto_pen; formatear PEN con dos decimales. null significa no indicado, distinto de cero. |
| estado_verificacion | estado y vigencia de la ficha; mostrar documentado, vigencia pendiente. |
| plazo, tipo_plazo | Registro pertinente en datos.plazos; máximo, mínimo/rango, aproximado o periodicidad. No elegir arbitrariamente entre evaluación y subsanación. |
| fase_siguiente, nombre_siguiente | Seguir siguiente_fase y leer fase/titulo de la ficha destino. |
| condiciones | datos.condiciones_continuidad de la ficha actual. |
| pregunta_entidad_faltante, pregunta_desambiguacion | Regla contextual de intents.yaml; preguntar solo el dato necesario con candidatos existentes. |
| plazo_subsanacion, detalle_disponible | datos.plazos del ámbito subsanación y la reserva documental aplicable en pendientes.md. |
| experiencia_anios | datos.experiencia_requerida_anios de TSP_F00. |
| descripcion_apto, descripcion_programacion, condicion_sustentacion | datos y condiciones_continuidad de TSP_F06 y TSP_F07. |
| pasos_titulo, condiciones_titulo, seguimiento_titulo | datos.pasos, condiciones de atención de áreas y datos.seguimiento de TSP_F08. |
| dato_pendiente, informacion_disponible | Ausencia documentada o validación pendiente identificada en pendientes.md y en la ficha. |
| motivo_orientacion | Motivo de transición: petición explícita, dos fallos o necesidad de validación institucional; no inventa contacto. |
| oferta_continuidad | Pregunta de seguimiento si hay siguiente etapa u otra consulta; despedida si termina. |
| modalidad_mencionada | Modalidad extraída del mensaje, sin recuperar reglas de otro proceso. |
| oficio, resolucion | datos.documentos_generados, sin intercambiar emisores. |
| constancia_repositorio, requisitos_repositorio, canal_repositorio | TSP_F08: generación descrita, lista específica no incluida y canal Trámite Seguimiento. |
| seguimiento_documentado | datos.seguimiento de la ficha actual, con distinción de F08. |
| dependencia, contacto_documentado | responsable identificado y datos.contacto_repositorio de TSP_F08; para Secretaría no existe contacto documentado. |
| duracion_ejecucion, orientacion_asesor | datos.plazos del ámbito ejecución y datos.pasos de TSP_F03. |

## Catálogo

### TSP_P01 — Requisitos por fase

- **Código de plantilla:** `TSP_P01`.
- **Intent asociado:** TSP_requisitos_fase.
- **Variables utilizadas:** `{fase}`, `{titulo}`, `{requisitos}`, `{documentos}`, `{ficha_id}`.
- **Estructura de la respuesta:** «Según el documento, para {fase}, {titulo}, necesitas: {requisitos}. Sobre los formatos de archivo: {documentos}.»
- **Ejemplo concreto:** «Para la fase 3 necesitas informe de aprobación de jurados, constancia de originalidad y trabajo en PDF, según el documento.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Seleccionar una ficha inequívoca. ficha_id se usa solo como trazabilidad interna, no se muestra como código al estudiante. No repetir la lista completa en documentos: resumir solo los formatos si están especificados.

### TSP_P02 — Procedimiento paso a paso

- **Código de plantilla:** `TSP_P02`.
- **Intent asociado:** TSP_pasos_fase.
- **Variables utilizadas:** `{fase}`, `{pasos}`, `{responsable}`, `{destino}`.
- **Estructura de la respuesta:** «Para {fase}, la secuencia documentada es: {pasos}. Participan {responsable}; la recepción corresponde a {destino}.»
- **Ejemplo concreto:** «En la fase 1, el bachiller genera la solicitud en la Plataforma y envía carta de aceptación y constancia del curso a Secretaría. El Programa Académico procesa y emite el oficio; la Facultad emite la resolución.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Conservar acciones y responsables. No convertir la Plataforma genérica en una URL inventada. Para F00, el pago o plazo ausente no se completan.

### TSP_P03 — Pago documentado

- **Código de plantilla:** `TSP_P03`.
- **Intent asociado:** TSP_costo_fase.
- **Variables utilizadas:** `{fase}`, `{concepto}`, `{monto}`, `{estado_verificacion}`.
- **Estructura de la respuesta:** «El documento indica para {fase}, {concepto}, un pago de {monto}. Estado de verificación: {estado_verificacion}.»
- **Ejemplo concreto:** «Para declarar apto en la fase 6, el documento indica S/ 3,212.00. La vigencia del monto está pendiente de confirmación institucional.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Si monto_pen es null, indicar No indicado y no formatearlo como cero. Si falta fase, usar TSP_P06. Cero documentado en F01/F02 debe mostrarse como S/ 0.00.

### TSP_P04 — Plazo y periodicidad

- **Código de plantilla:** `TSP_P04`.
- **Intent asociado:** TSP_plazo_fase.
- **Variables utilizadas:** `{fase}`, `{plazo}`, `{tipo_plazo}`.
- **Estructura de la respuesta:** «Según el documento, en {fase}, para la actividad consultada el plazo es {plazo}, de carácter {tipo_plazo}.»
- **Ejemplo concreto:** «La evaluación de la fase 2 tiene un máximo de 15 días según el documento. No se precisa si son días hábiles o calendario ni desde qué hito se cuentan.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Identificar la actividad si la ficha tiene varios plazos. Para un ámbito no documentado, usar TSP_P12; no reutilizar duración de ejecución como tiempo de atención.

### TSP_P05 — Siguiente etapa con condiciones

- **Código de plantilla:** `TSP_P05`.
- **Intent asociado:** TSP_siguiente_fase.
- **Variables utilizadas:** `{fase_actual}`, `{fase_siguiente}`, `{nombre_siguiente}`, `{condiciones}`.
- **Estructura de la respuesta:** «Después de {fase_actual}, la siguiente fase documentada es {fase_siguiente}, {nombre_siguiente}. Antes de continuar, considera: {condiciones}.»
- **Ejemplo concreto:** «Después de aprobar el trabajo en la fase 3, corresponde ejecutarlo con orientación del asesor técnico durante mínimo 2 y máximo 6 meses. Finalizada la ejecución, sigue la fase 4 de jurados para el informe final.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Leer siguiente_fase y condiciones_continuidad. F03 exige explicar ejecución; F07 exige explicar sustentación. F08 no tiene otra fase. No asumir que el bachiller cumplió la condición por pedir avanzar.

### TSP_P06 — Entidad faltante

- **Código de plantilla:** `TSP_P06`.
- **Intent asociado:** Intención pendiente, por ejemplo TSP_costo_fase.
- **Variables utilizadas:** `{pregunta_entidad_faltante}`.
- **Estructura de la respuesta:** «{pregunta_entidad_faltante}»
- **Ejemplo concreto:** «¿De qué fase del Trabajo de Suficiencia Profesional necesitas conocer el costo? Puedes indicarme una fase del 1 al 8.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** La consulta se entiende, pero falta una entidad indispensable. Conservar el intent anterior cuando responda la 6. La primera pregunta no suma un fallo.

### TSP_P07 — Desambiguación entre fases

- **Código de plantilla:** `TSP_P07`.
- **Intent asociado:** TSP_requisitos_fase; TSP_pasos_fase; TSP_documentos_fase; TSP_resolucion_fase.
- **Variables utilizadas:** `{pregunta_desambiguacion}`.
- **Estructura de la respuesta:** «{pregunta_desambiguacion}»
- **Ejemplo concreto:** «¿Te refieres a la designación de jurados de la fase 2 o a los jurados para el informe final de la fase 4?»
- **Fichas relacionadas:** [TSP_F02](fichas/TSP_F02.md), [TSP_F04](fichas/TSP_F04.md)
- **Condición y datos faltantes:** No resolver jurados por coincidencia parcial. Para informe final o resolución genérica, construir la pregunta con candidatos reales de las fichas; no introducir una fase inexistente.

### TSP_P08 — Observaciones y subsanación

- **Código de plantilla:** `TSP_P08`.
- **Intent asociado:** TSP_observaciones.
- **Variables utilizadas:** `{fase}`, `{plazo_subsanacion}`, `{detalle_disponible}`.
- **Estructura de la respuesta:** «En {fase}, el documento indica {plazo_subsanacion} para subsanar. Sobre el procedimiento: {detalle_disponible}.»
- **Ejemplo concreto:** «Para observaciones de la fase 4 se indica un máximo de 2 meses. El documento no precisa desde qué comunicación se cuenta ni el circuito detallado para entregar las correcciones.»
- **Fichas relacionadas:** [TSP_F02](fichas/TSP_F02.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Si fase es ambigua, aclarar. En F08 no hay un plazo de subsanación documentado: indicarlo y orientar a revisar requisitos/observaciones de Repositorio, sin aplicar los 2 meses de otras fases.

### TSP_P09 — Prerrequisito de experiencia

- **Código de plantilla:** `TSP_P09`.
- **Intent asociado:** TSP_experiencia_previa.
- **Variables utilizadas:** `{experiencia_anios}`, `{evidencias}`, `{destino_experiencia}`.
- **Estructura de la respuesta:** «Antes de las ocho fases, el documento exige acreditar {experiencia_anios} años de experiencia profesional con {evidencias}. Se envían a {destino_experiencia}.»
- **Ejemplo concreto:** «Antes de iniciar, acredita 2 años de experiencia con contratos, boletas y documentación de continuidad laboral. Se envía por correo a Secretaría, que confirma recepción. El correo exacto y la validación de fondo requieren confirmación.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md)
- **Condición y datos faltantes:** No presentar F00 como novena fase ni asegurar que la sola recepción acredita cumplimiento. Pago no indicado; no afirmar gratuidad.

### TSP_P10 — Aptitud y programación de sustentación

- **Código de plantilla:** `TSP_P10`.
- **Intent asociado:** TSP_sustentacion.
- **Variables utilizadas:** `{descripcion_apto}`, `{descripcion_programacion}`, `{condicion_sustentacion}`.
- **Estructura de la respuesta:** «La declaración de apto comprende {descripcion_apto}. La programación comprende {descripcion_programacion}. {condicion_sustentacion}.»
- **Ejemplo concreto:** «La fase 6 culmina con la resolución de apto. En la fase 7 se solicita fecha y hora y se obtiene su resolución. Luego se realiza la sustentación antes de continuar con la fase 8.»
- **Fichas relacionadas:** [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md)
- **Condición y datos faltantes:** La comparación puede usar ambas fichas; una consulta específica recupera solo la correspondiente. La resolución de apto no fija por sí sola la fecha.

### TSP_P11 — Trámite final del título

- **Código de plantilla:** `TSP_P11`.
- **Intent asociado:** TSP_titulo_profesional.
- **Variables utilizadas:** `{pasos_titulo}`, `{condiciones_titulo}`, `{seguimiento_titulo}`.
- **Estructura de la respuesta:** «Según el documento, para la fase 8: {pasos_titulo}. Considera {condiciones_titulo}. El seguimiento se realiza mediante {seguimiento_titulo}.»
- **Ejemplo concreto:** «Tras la sustentación, inicia Optar Título Profesional en Login UDH. Revisa la constancia automática y los requisitos de Repositorio en Trámite Seguimiento, presenta 2 fotos tamaño pasaporte con vestimenta formal en Coordinación y verifica atención de las áreas antes del Consejo.»
- **Fichas relacionadas:** [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** No transformar la generación automática de constancia en conformidad automática del Repositorio. El plazo de entrega es aproximado y no acredita que el título del usuario esté listo.

### TSP_P12 — Dato pendiente

- **Código de plantilla:** `TSP_P12`.
- **Intent asociado:** Intent TSP que originó la consulta.
- **Variables utilizadas:** `{dato_pendiente}`, `{informacion_disponible}`.
- **Estructura de la respuesta:** «El dato sobre {dato_pendiente} no está suficientemente especificado o confirmado en el documento. Lo disponible es: {informacion_disponible}. Corresponde pedir confirmación a Coordinación o al área competente.»
- **Ejemplo concreto:** «El correo de Secretaría no aparece en TrabajoSuficiencia.md. El documento sí señala que los requisitos de experiencia se remiten por correo, pero la dirección debe confirmarse.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** No tratar la falta documental como fallo del usuario ni suplirla con datos de otra modalidad. Si existe dato documental sin vigencia, informar ambos extremos.

### TSP_P13 — Transición a orientación humana

- **Código de plantilla:** `TSP_P13`.
- **Intent asociado:** Referencia externa a GEN_derivar_humano; no intent local.
- **Variables utilizadas:** `{motivo_orientacion}`.
- **Estructura de la respuesta:** «Esta consulta requiere orientación del personal administrativo. {motivo_orientacion}.»
- **Ejemplo concreto:** «Esta consulta requiere orientación del personal administrativo porque no logré precisar tu solicitud después de dos intentos.»
- **Fichas relacionadas:** No aplica: acción conversacional o referencia al módulo global, sin hechos administrativos propios.
- **Condición y datos faltantes:** Solo texto local de transición. Se referencia el intent global del integrante F; no se copia su definición, ejemplos ni reglas de contacto. No afirmar una transferencia efectiva ni enviar mensajes.

### TSP_P14 — Cierre y continuidad

- **Código de plantilla:** `TSP_P14`.
- **Intent asociado:** Seguimiento de la intención activa; acción TSP_ACC_cierre.
- **Variables utilizadas:** `{oferta_continuidad}`.
- **Estructura de la respuesta:** «{oferta_continuidad}»
- **Ejemplo concreto:** «¿Deseas revisar otra fase o conocer la siguiente etapa documentada?»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Si hay fase activa con siguiente, ofrecerla y guardar oferta_siguiente. Si F08 terminó o el estudiante se despide, cerrar con Gracias por consultar; puedes volver con otra duda sobre TSP. Un sí sin oferta concreta requiere aclaración.

### TSP_P15 — Documentos y formatos

- **Código de plantilla:** `TSP_P15`.
- **Intent asociado:** TSP_documentos_fase.
- **Variables utilizadas:** `{fase}`, `{documentos}`.
- **Estructura de la respuesta:** «Para {fase}, el documento señala: {documentos}.»
- **Ejemplo concreto:** «Para programar la sustentación en la fase 7 se solicita la resolución de aprobación del informe final en PDF y el informe final en Word.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Conservar literalmente Word/PDF y los nombres de documentos. No agregar formatos al DNI o grado cuando la fuente no los indique.

### TSP_P16 — Consulta fuera de alcance

- **Código de plantilla:** `TSP_P16`.
- **Intent asociado:** TSP_fuera_alcance.
- **Variables utilizadas:** `{modalidad_mencionada}`.
- **Estructura de la respuesta:** «Tu consulta corresponde a {modalidad_mencionada}. Este módulo orienta sobre Trabajo de Suficiencia Profesional. ¿Deseas consultar TSP?»
- **Ejemplo concreto:** «La titulación por tesis es otra modalidad. Este módulo corresponde a Trabajo de Suficiencia Profesional y no contiene las fases de tesis. ¿Deseas consultar TSP?»
- **Fichas relacionadas:** No aplica: acción conversacional o referencia al módulo global, sin hechos administrativos propios.
- **Condición y datos faltantes:** No recuperar fichas TSP para responder reglas de tesis. La navegación a otro módulo corresponde al orquestador, sin inventar un intent de otro integrante.

### TSP_P17 — Oficio y resolución

- **Código de plantilla:** `TSP_P17`.
- **Intent asociado:** TSP_resolucion_fase.
- **Variables utilizadas:** `{fase}`, `{oficio}`, `{resolucion}`.
- **Estructura de la respuesta:** «En {fase}, el Programa Académico emite {oficio} y la Facultad de Ingeniería emite {resolucion}.»
- **Ejemplo concreto:** «En la fase 6, el Programa Académico emite el oficio de conformidad de apto para sustentación y la Facultad emite la resolución de apto.»
- **Fichas relacionadas:** [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** No afirmar que el usuario ya tiene el documento. Para F00 no se documentan oficio ni resolución; responder que se confirma recepción.

### TSP_P18 — Repositorio Institucional

- **Código de plantilla:** `TSP_P18`.
- **Intent asociado:** TSP_repositorio.
- **Variables utilizadas:** `{constancia_repositorio}`, `{requisitos_repositorio}`, `{canal_repositorio}`.
- **Estructura de la respuesta:** «Según el documento, {constancia_repositorio}. Los requisitos específicos se revisan en {canal_repositorio}: {requisitos_repositorio}.»
- **Ejemplo concreto:** «La Constancia de Inscripción al Repositorio se genera automáticamente con Optar Título Profesional, según el documento. Los requisitos particulares deben revisarse en Trámite Seguimiento; su lista no está incluida en la fuente.»
- **Fichas relacionadas:** [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** No inventar la lista de requisitos, porcentaje de originalidad ni formato de archivos del Repositorio. La constancia no sustituye su atención.

### TSP_P19 — Seguimiento del expediente

- **Código de plantilla:** `TSP_P19`.
- **Intent asociado:** TSP_seguimiento.
- **Variables utilizadas:** `{seguimiento_documentado}`.
- **Estructura de la respuesta:** «Puedes orientarte mediante {seguimiento_documentado}, según el documento. No tengo acceso a tu expediente para verificar su estado real.»
- **Ejemplo concreto:** «El documento señala seguimiento desde Login UDH, principalmente en Trámite Seguimiento. Para la fase 8 añade Consulta Registro de Grados y Títulos. No puedo verificar si tu expediente ya fue atendido.»
- **Fichas relacionadas:** [TSP_F00](fichas/TSP_F00.md), [TSP_F01](fichas/TSP_F01.md), [TSP_F02](fichas/TSP_F02.md), [TSP_F03](fichas/TSP_F03.md), [TSP_F04](fichas/TSP_F04.md), [TSP_F05](fichas/TSP_F05.md), [TSP_F06](fichas/TSP_F06.md), [TSP_F07](fichas/TSP_F07.md), [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Para fases iniciales, no atribuir Consulta Registro de Grados y Títulos como mecanismo específico del expediente de asesor. Las menciones de estado son declaraciones del usuario.

### TSP_P20 — Contacto documental por dependencia

- **Código de plantilla:** `TSP_P20`.
- **Intent asociado:** TSP_contacto.
- **Variables utilizadas:** `{dependencia}`, `{contacto_documentado}`, `{estado_verificacion}`.
- **Estructura de la respuesta:** «Para {dependencia}, el documento indica {contacto_documentado}. {estado_verificacion}.»
- **Ejemplo concreto:** «Para Repositorio Institucional, el documento indica repositorio@udh.edu.pe y 952 068 664. Su vigencia actual requiere confirmación. No son el contacto de Secretaría.»
- **Fichas relacionadas:** [TSP_F08](fichas/TSP_F08.md)
- **Condición y datos faltantes:** Si pide Secretaría, no usar el contacto de Repositorio: TSP_P12. Si la dependencia no se especifica, preguntar cuál necesita. No presentar el contacto como validado hoy.

### TSP_P21 — Ejecución del trabajo

- **Código de plantilla:** `TSP_P21`.
- **Intent asociado:** TSP_ejecucion_trabajo.
- **Variables utilizadas:** `{duracion_ejecucion}`, `{orientacion_asesor}`.
- **Estructura de la respuesta:** «Después de la aprobación del trabajo, la ejecución tiene {duracion_ejecucion}, bajo {orientacion_asesor}. Luego se continúa con los jurados del informe final.»
- **Ejemplo concreto:** «Después de la aprobación en la fase 3, el trabajo se ejecuta bajo orientación del asesor técnico durante un mínimo de 2 y un máximo de 6 meses. Finalizada la ejecución, corresponde la fase 4.»
- **Fichas relacionadas:** [TSP_F03](fichas/TSP_F03.md)
- **Condición y datos faltantes:** Distinguir tiempo de ejecución y respuesta administrativa. No inventar una prórroga ni declarar validada la ejecución del usuario.

