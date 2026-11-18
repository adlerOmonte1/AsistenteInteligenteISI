"""Carga la base de conocimiento de la Fase 2 (knowledge-base/) en la base de datos.

El importador es tolerante: las carpetas que todavía no cumplen el contrato se
cargan igual, y cada desviación queda en el reporte como aviso. Así el
desarrollo no se detiene mientras el equipo corrige los archivos. Con
``estricto=True`` las fichas que no cumplen el contrato quedan en borrador y no
se publican; es el modo que se usa antes de una entrega.

Formatos aceptados (knowledge-base/catalogo.yaml):

- ``contrato``: fichas/*.md con encabezado YAML, intents.yaml, golden_set.csv,
  plantillas.md y pendientes.md. Se toleran variantes ya presentes en el
  repositorio: secciones en el bloque ``datos`` del encabezado (traslados,
  TSP), encabezados de golden set distintos (PPP) y nombres de archivo con
  sufijo (PPP_E00_condiciones.md).
- ``json_tesis``: el JSON del entregable de título por tesis.
"""

import csv
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml
from django.db import transaction

from apps.evaluacion.models import CasoEvaluacion
from comun.texto import normalizar

from ..models import SECCIONES, EjemploIntent, Facultad, Ficha, Intent, Pendiente, Plantilla, Proceso, Programa
from .contrato import errores_de_ficha
from .publicacion import publicar

RE_ENCABEZADO = re.compile(r"^﻿?---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.S)
RE_SECCION = re.compile(r"^##\s+(.+?)\s*$", re.M)
RE_CODIGO = re.compile(r"\b[A-Z]{3}_(?:[A-Z]{3}_)?[A-Z]\d{2}\b")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_ID_PENDIENTE = re.compile(r"^[A-Z][A-Z0-9]*[-_][A-Z0-9_-]+$")
RE_PLANTILLA = re.compile(r"^###\s+`?([A-Z][A-Z0-9_]+)`?\s*$", re.M)

ALIAS_SECCION = {
    "requisitos": "requisitos",
    "requisitos especificos": "requisitos",
    "pasos": "pasos",
    "procedimiento": "pasos",
    "pago": "pago",
    "pagos": "pago",
    "costo": "pago",
    "costos": "pago",
    "plazo": "plazo",
    "plazos": "plazo",
    "enviar a": "enviar_a",
    "entrega": "enviar_a",
    "donde enviar": "enviar_a",
    "siguiente fase": "siguiente_fase",
    "siguiente etapa": "siguiente_fase",
}
SECCIONES_POR_PALABRA = (
    (("costo", "pago", "monto", "cuanto"), ["pago"]),
    (("plazo", "tiempo", "dias", "duracion", "cuando"), ["plazo"]),
    (("correo", "enviar", "donde", "entrega", "destino"), ["enviar_a"]),
    (("requisito", "documento", "necesito"), ["requisitos"]),
    (("paso", "procedimiento", "como"), ["pasos"]),
    (("siguiente", "despues", "sigue"), ["siguiente_fase"]),
)


@dataclass
class ReporteProceso:
    clave: str
    fichas: int = 0
    publicadas: int = 0
    intents: int = 0
    ejemplos: int = 0
    casos: int = 0
    pendientes: int = 0
    plantillas: int = 0
    avisos: list[str] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)


@dataclass
class Reporte:
    procesos: list[ReporteProceso] = field(default_factory=list)

    @property
    def errores(self) -> int:
        return sum(len(p.errores) for p in self.procesos)

    @property
    def avisos(self) -> int:
        return sum(len(p.avisos) for p in self.procesos)


# --------------------------------------------------------------------- lectura


def _como_markdown(valor) -> str:
    """Convierte listas y dicts del YAML en texto Markdown legible."""
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor.strip()
    if isinstance(valor, dict):
        if "texto" in valor:
            return str(valor["texto"]).strip()
        partes = []
        for clave, v in valor.items():
            texto = _como_markdown(v)
            if texto:
                partes.append(f"- {str(clave).replace('_', ' ').capitalize()}: {texto}")
        return "\n".join(partes)
    if isinstance(valor, list):
        return "\n".join(f"- {_como_markdown(v)}" for v in valor if _como_markdown(v))
    return str(valor)


def leer_ficha_markdown(texto: str) -> tuple[dict, dict[str, str], str]:
    """Devuelve (metadatos, secciones del contrato, información adicional)."""
    m = RE_ENCABEZADO.match(texto)
    if not m:
        raise ValueError("sin encabezado YAML entre ---")
    meta = yaml.safe_load(m.group(1)) or {}
    cuerpo = m.group(2)

    secciones: dict[str, str] = {}
    adicional: list[str] = []
    titulos = list(RE_SECCION.finditer(cuerpo))
    for i, t in enumerate(titulos):
        fin = titulos[i + 1].start() if i + 1 < len(titulos) else len(cuerpo)
        contenido = cuerpo[t.end() : fin].strip()
        nombre = normalizar(t.group(1))
        clave = ALIAS_SECCION.get(nombre)
        if clave and clave not in secciones:
            secciones[clave] = contenido
        elif contenido and not nombre.startswith(("fuente y estado", "metadatos")):
            adicional.append(f"**{t.group(1).strip()}**\n{contenido}")

    datos = meta.get("datos") or {}
    respaldo = {
        "requisitos": datos.get("requisitos"),
        "pasos": datos.get("pasos"),
        "pago": datos.get("pagos", datos.get("pago")),
        "plazo": datos.get("plazo", datos.get("plazos")),
        "enviar_a": datos.get("enviar_a"),
        "siguiente_fase": meta.get("siguiente_fase"),
    }
    for clave, valor in respaldo.items():
        if not secciones.get(clave) and _como_markdown(valor):
            secciones[clave] = _como_markdown(valor)
    return meta, secciones, "\n\n".join(adicional)


def _vigencia(valor) -> tuple[date | None, str]:
    if isinstance(valor, date):
        return valor, ""
    texto = str(valor or "").strip()
    if RE_FECHA.match(texto):
        return date.fromisoformat(texto), ""
    return None, texto or "no indicada"


def _textos_de(fase: dict):
    def textos(clave: str) -> list[str]:
        return [x["texto"] if isinstance(x, dict) else str(x) for x in fase.get(clave) or []]

    return textos


def _fichas_tesis(ruta: Path) -> list[tuple[dict, dict[str, str], str]]:
    """Adapta 2_fichas_conocimiento.json al contrato (TES_F01 … TES_F09)."""
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    fuente = datos.get("fuente", "")
    vigencia = datos.get("fecha_vigencia", "no indicada")
    salida = []
    fases = [f for f in datos.get("fichas", []) if isinstance(f.get("fase"), int)]
    for i, f in enumerate(fases):
        textos = _textos_de(f)
        items = [x for c in ("requisitos", "pasos", "plazos") for x in f.get(c) or [] if isinstance(x, dict)]
        pendiente = any((x.get("metadatos") or {}).get("estado") == "pendiente" for x in items)
        pago = f.get("pago") or {}
        siguiente = f"TES_F{fases[i + 1]['fase']:02d}" if i + 1 < len(fases) else "Fin del proceso"
        pasos = textos("pasos")
        if f.get("tramite_login"):
            pasos.insert(0, f"Trámite en Login: {f['tramite_login']}.")
        meta = {
            "id": f"TES_F{f['fase']:02d}",
            "fase": f["fase"],
            "titulo": f.get("nombre", ""),
            "fuente": fuente,
            "vigencia": vigencia,
            "estado": "pendiente" if pendiente or pago.get("monto") is None else "confirmado",
        }
        secciones = {
            "requisitos": "\n".join(f"- {t}" for t in textos("requisitos")) or "No indicado",
            "pasos": "\n".join(f"{n}. {t}" for n, t in enumerate(pasos, start=1)) or "No indicado",
            "pago": pago.get("texto") or "No indicado",
            "plazo": "\n".join(f"- {t}" for t in textos("plazos")) or "No indicado",
            "enviar_a": f.get("correo_destino") or "No indicado",
            "siguiente_fase": siguiente,
        }
        adicional = "\n".join(f"- {t}" for t in textos("advertencias"))
        salida.append((meta, secciones, f"**Advertencias**\n{adicional}" if adicional else ""))
    return salida


def _lista_fichas(valor, codigos: list[str]) -> list[str]:
    if valor in (None, "", "null", []):
        return []
    if isinstance(valor, str):
        valor = [v.strip(" '\"") for v in valor.strip("[]").split(",")]
    encontrados = []
    for patron in valor:
        patron = str(patron).strip()
        if "*" in patron:
            regex = re.compile("^" + re.escape(patron).replace(r"\*", ".*") + "$")
            encontrados += [c for c in codigos if regex.match(c)]
        elif patron in codigos:
            encontrados.append(patron)
    return list(dict.fromkeys(encontrados))


def secciones_de_intent(nombre: str) -> list[str]:
    """Infiere qué secciones responde un intent a partir de su nombre (CPP_costo → pago)."""
    sufijo = normalizar(nombre.split("_", 1)[-1].replace("_", " "))
    if any(p in sufijo for p in ("info", "general", "diagnostico")):
        return []
    for palabras, secciones in SECCIONES_POR_PALABRA:
        if any(p in sufijo for p in palabras):
            return secciones
    return []


# ------------------------------------------------------------------- escritura


class Importador:
    def __init__(
        self, base: Path, *, publicar: bool = True, estricto: bool = False, usuario=None, solo=None, indexar=True
    ):
        """``indexar=False`` publica sin calcular embeddings; ``manage.py reindexar`` los completa después."""
        self.base = Path(base)
        self.indexar = indexar
        self.carpeta_procesos = self.base / "procesos"
        self.publicar = publicar
        self.estricto = estricto
        self.usuario = usuario
        self.solo = set(solo or [])

    def ejecutar(self) -> Reporte:
        catalogo = yaml.safe_load((self.base / "catalogo.yaml").read_text(encoding="utf-8"))
        facultad, _ = Facultad.objects.get_or_create(
            nombre=catalogo["facultad"]["nombre"], defaults={"sigla": catalogo["facultad"].get("sigla", "")}
        )
        programa, _ = Programa.objects.get_or_create(
            facultad=facultad,
            nombre=catalogo["programa"]["nombre"],
            defaults={"sigla": catalogo["programa"].get("sigla", "")},
        )
        reporte = Reporte()
        for definicion in catalogo["procesos"]:
            if self.solo and definicion["clave"] not in self.solo:
                continue
            parcial = ReporteProceso(clave=definicion["clave"])
            try:
                with transaction.atomic():
                    self._importar_proceso(programa, definicion, parcial)
            except Exception as exc:  # noqa: BLE001 - un proceso roto no detiene a los demás
                parcial.errores.append(f"{type(exc).__name__}: {exc}")
            reporte.procesos.append(parcial)
        return reporte

    def _importar_proceso(self, programa, d: dict, r: ReporteProceso):
        proceso, _ = Proceso.objects.update_or_create(
            programa=programa,
            clave=d["clave"],
            defaults={
                "nombre": d["nombre"],
                "descripcion": d.get("descripcion", ""),
                "prefijos": d.get("prefijos", []),
                "orden": d.get("orden", 0),
                "visible_en_portal": d.get("visible_en_portal", True),
                "activo": True,
            },
        )
        carpeta = self.carpeta_procesos / d["carpeta"]
        if not carpeta.is_dir():
            r.errores.append(f"no existe la carpeta {carpeta}")
            return

        if d.get("formato") == "json_tesis":
            leidas = _fichas_tesis(carpeta / "2_fichas_conocimiento.json")
            r.avisos.append(
                "formato JSON propio: se adaptó al contrato (TES_F01…); faltan intents.yaml y golden_set.csv"
            )
        else:
            leidas = []
            for archivo in sorted((carpeta / "fichas").glob("*.md")) if (carpeta / "fichas").is_dir() else []:
                try:
                    meta, secciones, adicional = leer_ficha_markdown(archivo.read_text(encoding="utf-8"))
                except (ValueError, yaml.YAMLError) as exc:
                    r.errores.append(f"{archivo.name}: {exc}")
                    continue
                if meta.get("id") and archivo.stem != meta["id"]:
                    r.avisos.append(f"{archivo.name}: el nombre del archivo no coincide con el id {meta['id']}")
                leidas.append((meta, secciones, adicional))

        for meta, secciones, adicional in leidas:
            self._guardar_ficha(proceso, meta, secciones, adicional, r)

        codigos = list(proceso.fichas.values_list("codigo", flat=True))
        if (carpeta / "intents.yaml").is_file():
            self._importar_intents(proceso, carpeta / "intents.yaml", codigos, r)
        if (carpeta / "golden_set.csv").is_file():
            self._importar_golden(proceso, carpeta / "golden_set.csv", r)
        elif (carpeta / "7_golden_set.csv").is_file():
            self._importar_golden(proceso, carpeta / "7_golden_set.csv", r, formato_tesis=True)
        if (carpeta / "pendientes.md").is_file():
            self._importar_pendientes(proceso, carpeta / "pendientes.md", r)
        if (carpeta / "plantillas.md").is_file():
            self._importar_plantillas(proceso, carpeta / "plantillas.md", r)

    def _guardar_ficha(self, proceso, meta: dict, secciones: dict, adicional: str, r: ReporteProceso):
        codigo = str(meta.get("id") or "").strip()
        if not codigo:
            r.errores.append("ficha sin id")
            return
        if meta.get("proceso") and meta["proceso"] != proceso.clave:
            r.avisos.append(f"{codigo}: proceso «{meta['proceso']}» en el archivo; se importa en «{proceso.clave}»")
        vigencia, vigencia_texto = _vigencia(meta.get("vigencia"))
        if vigencia is None and vigencia_texto not in ("no indicada",):
            r.avisos.append(f"{codigo}: vigencia «{vigencia_texto}» no es AAAA-MM-DD ni «no indicada»")
        estado = meta.get("estado") if meta.get("estado") in ("confirmado", "pendiente") else "pendiente"
        try:
            fase = int(meta.get("fase"))
        except (TypeError, ValueError):
            fase = 0
            r.avisos.append(f"{codigo}: fase «{meta.get('fase')}» no es un entero; se usa 0")

        ficha, _ = Ficha.objects.get_or_create(proceso=proceso, codigo=codigo, defaults={"titulo": codigo})
        ficha.fase = fase
        ficha.titulo = str(meta.get("titulo") or codigo)[:300]
        ficha.fuente = str(meta.get("fuente") or "")
        ficha.vigencia, ficha.vigencia_texto = vigencia, vigencia_texto
        ficha.estado_dato = estado
        ficha.palabras_clave = meta.get("palabras_clave") or []
        ficha.informacion_adicional = adicional
        for seccion in SECCIONES:
            setattr(ficha, seccion, secciones.get(seccion, ""))
        ficha.actualizada_por = self.usuario
        if ficha.estado_revision != Ficha.EstadoRevision.EN_REVISION:
            ficha.estado_revision = Ficha.EstadoRevision.BORRADOR
        ficha.save()
        r.fichas += 1

        errores = errores_de_ficha(ficha)
        for campo, mensaje in errores.items():
            r.avisos.append(f"{codigo}.{campo}: {mensaje}")
        if not self.publicar or (self.estricto and errores):
            return
        if ficha.tiene_cambios_sin_publicar:
            if self.indexar:
                publicar(ficha, self.usuario, "Importación desde knowledge-base", indexar_en_segundo_plano=False)
            else:
                publicar(ficha, self.usuario, "Importación desde knowledge-base", indexar=False)
        else:
            ficha.estado_revision = Ficha.EstadoRevision.PUBLICADA
            ficha.save(update_fields=["estado_revision"])
        r.publicadas += 1

    def _importar_intents(self, proceso, ruta: Path, codigos: list[str], r: ReporteProceso):
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
        lista = datos if isinstance(datos, list) else datos.get("intents", [])
        for item in lista:
            if not isinstance(item, dict) or not item.get("intent"):
                continue
            nombre = str(item["intent"]).strip()
            transversal = nombre.startswith("GEN_")
            destino = self._proceso_general(proceso) if transversal else proceso
            existente = Intent.objects.filter(nombre=nombre).exclude(proceso=destino).first()
            if existente and not transversal:
                r.avisos.append(f"intent {nombre}: ya existe en «{existente.proceso.clave}»; se omite")
                continue
            fichas = _lista_fichas(item.get("ficha_relacionada"), codigos)
            if item.get("ficha_relacionada") not in (None, "", "null", []) and not fichas:
                r.avisos.append(f"intent {nombre}: ficha_relacionada {item['ficha_relacionada']} no existe")
            si_falta = item.get("si_falta_entidad")
            valores = {
                "proceso": destino,
                "descripcion": str(item.get("descripcion") or ""),
                "entidades": item.get("entidades") or [],
                "si_falta_entidad": "" if si_falta in (None, "null") else str(si_falta),
                "respuesta_fija": str(item.get("respuesta_fija") or ""),
                "secciones": item.get("secciones") or secciones_de_intent(nombre),
                "activo": True,
            }
            intent = Intent.objects.filter(nombre=nombre).first()
            if intent is None:
                intent = Intent.objects.create(nombre=nombre, **valores)
            else:
                # Un intent transversal puede venir de varias carpetas: no se pisa lo ya definido.
                for campo, valor in valores.items():
                    if valor or not transversal:
                        setattr(intent, campo, valor)
                intent.save()
            if not transversal:
                intent.fichas.set(proceso.fichas.filter(codigo__in=fichas))
            ejemplos = [str(e).strip() for e in item.get("ejemplos") or [] if str(e).strip()]
            if len(ejemplos) < 10:
                r.avisos.append(f"intent {nombre}: {len(ejemplos)} ejemplos (mínimo 10)")
            actuales = set(intent.ejemplos.values_list("texto", flat=True))
            if transversal:
                ejemplos = sorted(actuales | set(ejemplos))
            if actuales != set(ejemplos):
                intent.ejemplos.all().delete()
                EjemploIntent.objects.bulk_create(EjemploIntent(intent=intent, texto=e[:500]) for e in ejemplos)
            r.intents += 1
            r.ejemplos += len(ejemplos)

    @staticmethod
    def _proceso_general(proceso):
        general, _ = Proceso.objects.get_or_create(
            programa=proceso.programa,
            clave="general",
            defaults={"nombre": "Consultas generales", "prefijos": ["GEN"], "orden": 99, "visible_en_portal": False},
        )
        return general

    def _importar_golden(self, proceso, ruta: Path, r: ReporteProceso, formato_tesis: bool = False):
        with ruta.open(encoding="utf-8-sig", newline="") as fh:
            filas = list(csv.DictReader(fh))
        for fila in filas:
            codigo = (fila.get("id") or "").strip()
            pregunta = (fila.get("pregunta") or "").strip()
            if not codigo or not pregunta:
                continue
            if formato_tesis:
                fase = (fila.get("fase") or "").strip()
                intent, ficha = "", f"TES_F{int(fase):02d}" if fase.isdigit() else ""
                clave = ""
            else:
                intent = (fila.get("intent_esperado") or fila.get("intent") or "").strip()
                ficha = (fila.get("ficha_esperada") or "").strip()
                if ficha == "NO_APLICA":  # el caso no espera ninguna ficha
                    ficha = ""
                clave = (fila.get("respuesta_clave") or fila.get("dato_clave") or "").strip()
            CasoEvaluacion.objects.update_or_create(
                proceso=proceso,
                codigo=codigo,
                defaults={
                    "pregunta": pregunta,
                    "intent_esperado": intent,
                    "ficha_esperada": ficha,
                    "respuesta_clave": clave,
                    "tipo": (fila.get("tipo") or "").strip(),
                },
            )
            r.casos += 1
        if filas and "respuesta_clave" not in filas[0]:
            r.avisos.append("golden_set.csv: encabezado distinto del contrato; se mapearon las columnas")

    def _importar_pendientes(self, proceso, ruta: Path, r: ReporteProceso):
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if not linea.startswith("|"):
                continue
            celdas = [c.strip().strip("`") for c in linea.strip().strip("|").split("|")]
            if not celdas or not RE_ID_PENDIENTE.match(celdas[0]) or celdas[0].upper() == "ID":
                continue
            pregunta = next((c for c in celdas if "¿" in c), "")
            descripcion = " · ".join(c for c in celdas[1:4] if c and c != pregunta)
            estado = celdas[-1].lower()
            pendiente, _ = Pendiente.objects.update_or_create(
                proceso=proceso,
                codigo=celdas[0],
                defaults={
                    "descripcion": descripcion or celdas[0],
                    "pregunta": pregunta,
                    "resuelto": estado.startswith(("resuelto", "confirmado", "cerrado")),
                },
            )
            pendiente.fichas.set(proceso.fichas.filter(codigo__in=RE_CODIGO.findall(linea)))
            r.pendientes += 1

    def _importar_plantillas(self, proceso, ruta: Path, r: ReporteProceso):
        texto = ruta.read_text(encoding="utf-8")
        titulos = list(RE_PLANTILLA.finditer(texto))
        for i, t in enumerate(titulos):
            fin = titulos[i + 1].start() if i + 1 < len(titulos) else len(texto)
            bloque = texto[t.end() : fin].split("\n## ")[0].split("\n---")[0]
            cuerpo = "\n".join(linea.removeprefix(">").strip() for linea in bloque.strip().splitlines()).strip()
            if cuerpo:
                Plantilla.objects.update_or_create(proceso=proceso, clave=t.group(1), defaults={"texto": cuerpo})
                r.plantillas += 1
