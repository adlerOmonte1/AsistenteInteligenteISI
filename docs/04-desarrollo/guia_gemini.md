# Guía: activar Gemini con el plan gratuito

Sin API key el asistente usa el proveedor `local`: no redacta, copia las secciones de las fichas, y los embeddings solo reconocen palabras iguales. Con Gemini el asistente redacta las respuestas abiertas y entiende paráfrasis («cuánto me cobran» ≈ «costo»).

Para la fase de pruebas basta el **plan gratuito de Google AI Studio**: no pide tarjeta.

## 1. Obtener la API key

1. Entre a <https://aistudio.google.com/apikey> con una cuenta de Google. Use una cuenta del equipo o del proyecto, no una personal que luego no se pueda transferir.
2. Pulse **Create API key** y elija (o cree) un proyecto de Google Cloud.
3. Copie la clave. Trátela como una contraseña: no la pegue en el chat del equipo ni la suba al repositorio.

En la misma página puede revisar los modelos disponibles y los límites del plan gratuito: un número de peticiones por minuto y por día para cada modelo. Para pruebas del equipo alcanzan de sobra.

## 2. Configurar el backend

1. Copie `backend/.env.example` como `backend/.env`.
2. Pegue la clave en `LLM_API_KEY`. Los demás valores ya vienen listos:

```
LLM_PROVEEDOR=gemini
LLM_MODELO=gemini-2.5-flash-lite
LLM_API_KEY=su-clave
EMBED_PROVEEDOR=gemini
EMBED_MODELO=gemini-embedding-001
```

`backend/.env` está en `.gitignore`: no se sube a GitHub.

## 3. Recalcular el índice

Los embeddings guardados se calcularon con el proveedor local; los de Gemini están en otro espacio vectorial. Después de cambiar de proveedor es **obligatorio** reindexar:

```bash
cd backend && .venv/Scripts/python manage.py reindexar
```

Son unos 1 160 textos (≈ 360 secciones y ≈ 800 ejemplos de intents). El plan gratuito cuenta **cada texto como una petición** y limita las peticiones por minuto y por día, así que el comando:

- envía lotes de 50 textos;
- ante un `429` espera lo que indica Gemini y repite (hasta 6 veces, `--reintentos`);
- guarda cada ficha y cada lote apenas se calculan.

Si aun así se corta con «se agotó la cuota», **vuelva a ejecutar el mismo comando**: continúa donde quedó. Si el detalle dice «per day», es la cuota diaria: el comando se detiene sin reintentar y se continúa al día siguiente (se reinicia a la medianoche, hora del Pacífico).

En el plan gratuito la cuota diaria de embeddings es de **1 000 textos** (17/11/2026), compartida entre `reindexar` y las preguntas del chat (cada pregunta usa uno). Una reindexación completa (~1 200 textos) toma dos días. Para cargar fichas sin gastar cuota: `manage.py importar_conocimiento --sin-indexar` y luego `reindexar`. El uso de la cuota se ve en <https://ai.dev/rate-limit>.

Mientras el índice esté a medias el asistente funciona igual: compara solo vectores del mismo proveedor y completa con la búsqueda por palabras.

Para ir más despacio (por ejemplo, si el límite por minuto es bajo), agregue en `backend/.env`:

```
EMBED_LOTE=20
EMBED_PAUSA=15
```

## 4. Reiniciar y probar

1. Reinicie `runserver` para que lea el `.env`.
2. En el panel, abra **Configuración**: debe decir proveedor `gemini`.
3. Pruebe en el **Probador** una pregunta abierta, por ejemplo «trabajo hace dos años en soporte, ¿me sirve para algo?». La traza muestra la vía `rag` y las fichas citadas.
4. Ejecute el **Golden set** (con el worker encendido: `python manage.py qcluster`) y compare con la línea base de `docs/02-base-conocimiento/estado_conocimiento.md`.

## 5. Calibrar los umbrales

La confianza del clasificador depende del proveedor de embeddings: con Gemini los valores suben respecto del modo local. Tras el primer golden set con Gemini, ajuste en **Configuración** los umbrales determinista (0,75) y de desambiguación (0,40) hasta cumplir las metas, y vuelva a ejecutar el golden set.

## Precauciones del plan gratuito

- **Privacidad:** en el plan gratuito Google puede usar lo enviado para mejorar sus productos. Sirve para pruebas porque el sistema no envía datos personales (las preguntas se enmascaran al registrarse, y al LLM solo van la pregunta y las fichas). Para producción se recomienda el plan de pago (ver `bases_del_sistema.md`).
- **Límites:** si se superan, Gemini responde 429. El sistema no se cae: la vía RAG pasa a copiar las secciones (como el modo local) y el clasificador queda solo con la búsqueda por palabras. En **Conversaciones** se ve el motivo `error_proveedor_llm`.
- **Modelos:** Google retira modelos con el tiempo. Si un nombre deja de existir, cambie `LLM_MODELO` o `EMBED_MODELO` por el que indique AI Studio y, si cambió el de embeddings, vuelva a ejecutar `reindexar`.
- **Volver al modo local:** ponga `LLM_PROVEEDOR=local` y `EMBED_PROVEEDOR=local`, reinicie y ejecute `reindexar`.
