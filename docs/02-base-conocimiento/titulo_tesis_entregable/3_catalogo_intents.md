# Paso 3 — Catálogo de intents y entidades

## 3.1 Intents

### Generales
saludo · despedida · agradecimiento · menu_ayuda · hablar_con_humano · fuera_de_alcance · fallback

### Propios del proceso
titulo_tesis_info · titulo_tesis_fase

### Transversales
consultar_requisitos · consultar_costo · consultar_plazo · consultar_correo · consultar_estado_tramite · elegir_modalidad_titulo · ruta_academica

> Excluidos (no son este proceso): `ppp_info`, `conv_ppp_experiencia`, `bachiller_info`, `titulo_tsp_info`, `convalidacion_traslado`.

## 3.2 Entidades

| Entidad | Valores |
|---------|---------|
| `fase` | 1–9, general |
| `modalidad_titulo` | tesis, TSP |
| `documento` | carta de aceptación, constancia CRC, compromiso de honor, resolución de asesores, informe de conformidad, constancia de originalidad, instrumento de evaluación, informe final, boleta de pago, DNI, antecedentes penales, constancia de repositorio, fotos |
| `tramite_login` | nombre exacto en mayúsculas (ver fichas) |
| `programa` | Ingeniería de Sistemas e Informática |

## 3.3 Tabla intent | frases_ejemplo | entidades

| intent | frases_ejemplo | entidades_que_extrae |
|--------|----------------|----------------------|
| saludo | "hola" · "buenas" · "buenos días" · "hola, una consulta" · "qué tal" · "buenas tardes" · "hey" · "hola bot" · "holi" · "buenas noches" | — |
| despedida | "chau" · "adiós" · "hasta luego" · "nos vemos" · "eso es todo" · "ya me voy" · "gracias, chau" · "listo, hasta pronto" · "cerrar" · "bye" | — |
| agradecimiento | "gracias" · "muchas gracias" · "te agradezco" · "genial, gracias" · "ok gracias" · "súper, gracias" · "mil gracias" · "buenazo" · "gracias por la ayuda" · "perfecto, gracias" | — |
| menu_ayuda | "qué puedes hacer" · "ayuda" · "menú" · "qué temas manejas" · "en qué me ayudas" · "opciones" · "qué sabes de titulación" · "cómo funciona esto" · "necesito ayuda" · "qué información tienes" | — |
| hablar_con_humano | "quiero hablar con alguien" · "pásame con secretaría" · "necesito una persona" · "comunícame con coordinación" · "hay alguien real" · "con quién coordino" · "quiero un humano" · "atiéndanme por teléfono" · "no me sirve, quiero hablar con alguien" · "número de contacto" | programa |
| fuera_de_alcance | "cuánto es la pensión" · "cuándo son las matrículas" · "dónde queda la biblioteca" · "cómo me convalido" · "qué es el PPP" · "cómo saco mi bachiller" · "cuál es el clima" · "recomiéndame una película" · "ayúdame con mi tarea" · "horario de clases" | — |
| fallback | "asdf" · "no sé" · "eso" · "mmm" · "xyz123" · "lo de siempre" · "pues" · "a ver" · "quizás" · "tal vez" | — |
| titulo_tesis_info | "quiero mi título por tesis" · "cómo me titulo con tesis" · "proceso de titulación" · "quiero sustentar mi tesis" · "cómo saco el título profesional" · "qué pasos hay para titularme" · "titulación por tesis sistemas" · "por dónde empiezo para titularme" · "cuántas fases tiene el proceso" · "quiero titularme" · "cómo es el trámite de título" · "explícame el proceso de tesis" | modalidad_titulo, programa |
| titulo_tesis_fase | "qué necesito para la fase 4" · "ya tengo asesor, qué sigue" · "estoy en pre sustentación" · "ya declaré apto, y ahora" · "qué sigue después del informe final" · "en qué consiste la fase 6" · "voy por la fase 3" · "ya aprobaron mi proyecto, qué hago" · "estoy en la fase de jurados" · "cuál es la fase 9" · "qué viene después de la pre sustentación" · "ya tengo fecha de sustentación, qué falta" | fase, tramite_login |
| consultar_requisitos | "qué documentos necesito" · "requisitos para designar asesor" · "qué papeles piden para declarar apto" · "qué es el doc objetante" · "qué es la constancia de originalidad" · "necesito compromiso de honor" · "piden DNI en alguna fase" · "qué piden para fecha y hora" · "lista de requisitos fase 2" · "qué adjunto al trámite" · "requisitos para el título" | fase, documento |
| consultar_costo | "cuánto cuesta la pre sustentación" · "cuánto se paga en declarar apto" · "cuánto cuesta el título" · "hay que pagar en la fase 3" · "monto de la fase 4" · "cuánto es el trámite de fecha y hora" · "qué es la boleta de pago" · "cuánto pago por optar título" · "tiene costo designar asesor" · "cuánto cuesta jurados revisores" · "precio del trámite" | fase, documento |
| consultar_plazo | "cuántos días tengo para subsanar" · "cuánto demora la aprobación del proyecto" · "plazo para pedir fecha y hora" · "cuánto dura la fase 1" · "cuándo es el Consejo de Facultad" · "cuánto tarda la entrega del grado" · "cuántas revisiones me dan" · "hasta cuándo vale mi asesor" · "cuántos meses tengo en la fase 3" · "se anula mi trámite si me demoro" · "tiempo para levantar observaciones" | fase |
| consultar_correo | "dónde mando los papeles" · "a qué correo envío los requisitos" · "correo de secretaría" · "correo del repositorio" · "a quién le escribo" · "número para consultar" · "teléfono de la escuela" · "dónde queda la facultad" · "a dónde envío el informe de conformidad" · "contacto del programa" | fase, documento |
| consultar_estado_tramite | "cómo va mi trámite" · "dónde veo mi trámite" · "cómo hago seguimiento" · "ya salió mi resolución" · "cómo sé si ya atendieron mi trámite" · "dónde consulto mi título" · "trámite seguimiento" · "cuándo entra mi trámite a Consejo" · "dónde veo registro de grados y títulos" · "mi trámite está atendido" | fase, tramite_login |
| elegir_modalidad_titulo | "tesis o TSP" · "qué modalidad me conviene" · "me titulo por trabajo de suficiencia" · "qué modalidades hay" · "diferencia entre tesis y TSP" · "quiero por tesis, no por TSP" · "puedo titularme sin tesis" · "otras formas de titularme" · "modalidad de sustentación de tesis" · "cuál es más rápida" | modalidad_titulo |
| ruta_academica | "qué necesito antes del título" · "primero PPP, luego bachiller, luego título?" · "puedo pedir título sin ser bachiller" · "en qué orden va todo" · "ya soy bachiller, qué sigue" · "necesito el curso de conducta responsable" · "dónde hago el curso de investigación" · "qué hago antes de la fase 1" · "grado de bachiller es obligatorio" · "ruta para titularme" | fase, modalidad_titulo |

## 3.4 Reglas de enrutamiento
- `consultar_costo` + fase 2–8 → plantilla **pendiente**; fase 9 → **S/ 5.00**.
- `consultar_correo` + fase 9 y mención de repositorio → `repositorio@udh.edu.pe`.
- Slot `fase` faltante en `titulo_tesis_fase`, `consultar_requisitos`, `consultar_plazo` → preguntar fase.
- `elegir_modalidad_titulo` = TSP → derivar (fuera de alcance).
