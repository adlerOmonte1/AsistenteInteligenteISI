
# Plan de trabajo — Fase 2

La clave para que nadie dependa de nadie es **repartir por proceso, no por tipo de tarea**, y fijar desde hoy un formato común. Si una persona hace las fichas, otra los _intents_ y otra los flujos, todos se bloquean entre sí. Si cada integrante es dueño de un proceso completo, de principio a fin y con la misma plantilla, el único punto de unión será juntar las carpetas al final.

## 1\. Reparto de responsabilidades

| Integrante | Responsable de | Carga |
| --- | --- | --- |
| A (tú) | Arquitectura híbrida, esquema de metadatos, flujo de actualización por el administrador y consolidación final LOPEZ/OSO/ADLER (CONSOLIDACION FINAL) | Diseño |
| B | Título por sustentación de tesis (9 fases) KENNY | Alta |
| C | Título por Trabajo de Suficiencia Profesional (prerrequisito y 7 fases) DANI/SIDANE (FASE 5) | Alta |
| D | Prácticas Preprofesionales (PPP) Plan 2021 (4 etapas y anulaciones) ADLER | Media |
| E | Grado de Bachiller y convalidación de PPP por experiencia laboral LOPEZ/OSO | Media |
| F | Convalidación por traslado (interno y externo) e _intents_ generales y transversales: saludo, _fallback_, derivación a un humano, ruta académica y elección de modalidad de título SIDANE | Media |

Todos obtienen los datos del documento consolidado de la Fase 1, que ya existe. Por lo tanto, nadie tiene que esperar a que otro integrante termine su trabajo.

## 2\. Entregables por integrante (B a F)

Cada integrante debe preparar los siguientes entregables para su proceso:

1. **Fichas de conocimiento:** una por cada fase o etapa.
2. **Intents y entidades:** con entre 10 y 15 frases de ejemplo por _intent_.
3. **Diagrama de flujo conversacional:** elaborado en Mermaid.
4. **Plantillas de respuesta:** respuestas estandarizadas para los casos de uso del proceso.
5. **Golden set:** entre 10 y 15 preguntas con sus respuestas esperadas.
6. **Lista de pendientes:** datos sin confirmar del proceso que deberán consultarse con Coordinación.

### Entregables del integrante A

El responsable A debe entregar:

- Documento de arquitectura híbrida.
- Esquema de metadatos.
- Diagrama del flujo de actualización por parte del administrador.
- Plantilla del informe final.
- Informe final consolidado con los entregables de todos los integrantes.

## 3\. Contrato común de trabajo

**Este contrato debe compartirse hoy y mantenerse sin cambios durante la ejecución de la Fase 2.**

### 3.1. Estructura del repositorio GitHub

Cada integrante trabajará únicamente en su propia carpeta para evitar conflictos durante la integración.

```
fase2/
├── 00_arquitectura/          # A
├── titulo_tesis/             # B
├── titulo_tsp/               # C
├── ppp/                      # D
├── bachiller_conv_ppp/       # E
└── traslados_generales/      # F
    ├── fichas/
    ├── intents.yaml
    ├── flujo.md
    ├── plantillas.md
    ├── golden_set.csv
    └── pendientes.md
```

Cada carpeta de proceso deberá contener los archivos correspondientes a los entregables establecidos. La estructura de ejemplo muestra el contenido de `traslados_generales/`; los demás procesos seguirán el mismo contrato, adaptando sus identificadores y nombres de archivo cuando corresponda.

### 3.2. Prefijos de identificadores

Para evitar colisiones entre integrantes, se utilizarán los siguientes prefijos:

| Prefijo | Proceso |
| --- | --- |
| `TES_` | Título por tesis |
| `TSP_` | Título por Trabajo de Suficiencia Profesional |
| `PPP_` | Prácticas Preprofesionales |
| `BAC_` | Grado de Bachiller |
| `CPP_` | Convalidación de PPP |
| `TRA_` | Traslados |
| `GEN_` | Intents generales y transversales |

### 3.3. Formato de las fichas de conocimiento

Cada ficha se guardará en Markdown dentro de la carpeta `fichas/`.

Ejemplo: `fichas/TES_F04.md`

```
---
id: TES_F04
facultad: Ingeniería
programa: Ingeniería de Sistemas e Informática
proceso: titulo_tesis
fase: 4
titulo: Designación de jurados revisores del informe final
fuente: Res. N.° 2367-2025-R-CU-UDH
vigencia: 2025-11-11
estado: confirmado        # confirmado | pendiente
---
## Requisitos
- ...

## Pasos
1. ...

## Pago
S/ ... (o "no indicado")

## Plazo
...

## Enviar a
secretaria.sistemas.hco@udh.edu.pe

## Siguiente fase
TES_F05
```

**Reglas para las fichas:**

- Cada fase o etapa debe tener su propia ficha.
- Todos los campos del encabezado deben estar completos.
- Los datos no confirmados deben marcarse con `estado: pendiente`.
- No se deben inventar requisitos, costos, plazos, correos ni referencias normativas.
- Cuando una información no figure en la fuente, se debe indicar explícitamente que no está indicada o que está pendiente de confirmación, según corresponda.

### 3.4. Formato de los intents

Los _intents_ se documentarán en `intents.yaml`.

Ejemplo:

```
- intent: TES_requisitos_fase
  descripcion: Requisitos de una fase del título por tesis
  entidades: [fase]
  ejemplos:
    - "qué necesito para la fase 4 de tesis"
    - "requisitos para designar jurados revisores"
  ficha_relacionada: TES_F*
  si_falta_entidad: "¿De qué fase de la tesis necesitas los requisitos? (1 a 9)"
```

**Reglas para los intents:**

- Cada _intent_ debe incluir su descripción, entidades, ejemplos y ficha relacionada.
- Cada _intent_ debe tener al menos 10 frases de ejemplo.
- Se debe especificar la pregunta que hará el sistema cuando falte una entidad necesaria.
- Los identificadores deben respetar los prefijos asignados a cada proceso.
- Las referencias a fichas deben permitir identificar el conocimiento que utilizará el sistema para responder.

### 3.5. Formato de los flujos conversacionales

Los flujos se documentarán en `flujo.md` y se representarán mediante Mermaid.

Ejemplo:
EL GRAFICO ESTA EN EL DOCUMENTO:
https://docs.google.com/document/d/1Om-hjTyc9ueMGaLIudGRMx__CpVJUDIvsnk-ph0RkNU/edit?usp=sharing
ULTIMA HOJA
```
flowchart TD
  A[Intent detectado] --> B{¿Falta fase?}
  B -- Sí --> C[Preguntar fase]
  B -- No --> D[Responder con ficha]
  C --> D
  D --> E{¿Ver fase siguiente?}
  E -- Sí --> D
  E -- No --> F[Cierre]
```

**Regla común de derivación:** después de dos intentos fallidos, el sistema debe derivar la conversación mediante `GEN_derivar_humano`.

El integrante F definirá este _intent_ transversal. Los demás integrantes únicamente deberán referenciarlo por su identificador, sin esperar a que F termine su implementación.

Todos los flujos deben contemplar:

- Desambiguación cuando la consulta no sea suficientemente específica.
- Solicitud de entidades faltantes.
- Respuesta basada en la ficha correspondiente.
- Seguimiento para consultar fases o etapas posteriores.
- Cierre de la conversación.
- Derivación a un humano después de dos intentos fallidos.

### 3.6. Formato del golden set

El conjunto de preguntas de evaluación se guardará en `golden_set.csv`.

Ejemplo:

```
id,pregunta,intent_esperado,ficha_esperada,respuesta_clave
TES_Q01,"cuánto cuesta optar el título por tesis",TES_costo,TES_F09,"S/ 5.00"
```

**Reglas del golden set:**

- Debe contener al menos 10 preguntas por proceso.
- Cada pregunta debe tener un _intent_ esperado.
- Cada pregunta debe estar asociada a una ficha esperada.
- La respuesta clave debe permitir comprobar si el sistema responde correctamente.
- Los costos y demás datos de las respuestas deben estar respaldados por las fuentes disponibles.

### 3.7. Lista de pendientes

Cada integrante debe registrar los datos que no se encuentren confirmados en `pendientes.md`.

La lista servirá como insumo para la reunión con Coordinación del 28 de octubre. Cada pendiente debe identificar, como mínimo, el dato que falta y la fase o etapa del proceso al que corresponde.

## 4\. Cronograma de trabajo

| Fecha | Integrantes B a F | Integrante A |
| --- | --- | --- |
| 20 de octubre | Reciben el contrato y crean sus carpetas | Publica el contrato en el repositorio |
| 20–22 de octubre | Elaboran las fichas de conocimiento | Desarrolla la arquitectura y el esquema de metadatos |
| 22–24 de octubre | Elaboran los intents y las frases de ejemplo | Desarrolla el flujo de actualización por el administrador |
| 24–26 de octubre | Elaboran los flujos conversacionales y las plantillas | Prepara la plantilla del informe final |
| 26–27 de octubre | Completan el golden set y la lista de pendientes | Revisa que cada carpeta cumpla el contrato |
| 28 de octubre | Participan en una única reunión con Coordinación, utilizando los archivos `pendientes.md` de todos los procesos | Participa en la consolidación de los pendientes |
| 29 de octubre | Entregables individuales completos | Consolida e integra los entregables en el informe final |

## 5\. Criterios de aceptación: ¿cuándo está terminado un proceso?

La carpeta de cada integrante se considerará completa únicamente cuando cumpla los siguientes criterios:

- [ ]Existe una ficha por cada fase o etapa del proceso.
- [ ]Todas las fichas tienen completos los campos de su encabezado.
- [ ]Los datos no confirmados están identificados mediante `estado: pendiente`.
- [ ]Cada _intent_ tiene al menos 10 frases de ejemplo.
- [ ]Cada _intent_ especifica qué pregunta debe hacerse cuando falta una entidad.
- [ ]El flujo conversacional contempla desambiguación, seguimiento y derivación a un humano.
- [ ]El golden set contiene al menos 10 preguntas con sus respuestas esperadas.
- [ ]Los entregables respetan los prefijos de identificadores y la estructura acordada.
- [ ]Los datos incluidos están respaldados por las fuentes disponibles; no se han inventado requisitos, costos, plazos ni procedimientos.
- [ ]Los pendientes están documentados para su revisión con Coordinación.

## 6\. Resultado esperado

Con esta organización, cada integrante puede avanzar de forma independiente y completar su proceso sin bloquear el trabajo de los demás.

Si alguien se retrasa, únicamente se verá afectada su carpeta y no el avance de los otros integrantes. La arquitectura y los formatos comunes permiten integrar los resultados sin tener que rehacer los entregables.

**El objetivo del 29 de octubre es consolidar las carpetas completas y elaborar el informe final**, manteniendo la trazabilidad de las fuentes, la consistencia de los metadatos y la identificación explícita de cualquier dato pendiente de confirmación.
