"""Valida que las carpetas de proceso cumplan el contrato común de la Fase 2.

Uso:
    python validar_contrato.py <carpeta_raiz_o_de_proceso> [--md]

Si la carpeta contiene fichas/ se valida como un proceso; si no, se valida cada
subcarpeta de proceso (se omite 00_arquitectura). Con --md imprime además una
tabla Markdown lista para pegar en el informe final.

Solo usa la biblioteca estándar (no requiere PyYAML).
"""
import csv
import re
import sys
from pathlib import Path

PREFIJOS = {
    "TES": "titulo_tesis",
    "TSP": "titulo_tsp",
    "PPP": "ppp",
    "BAC": "bachiller_conv_ppp",
    "CPP": "bachiller_conv_ppp",
    "TRA": "traslados_generales",
    "GEN": "traslados_generales",
}
CAMPOS = ["id", "facultad", "programa", "proceso", "fase", "titulo", "fuente", "vigencia", "estado"]
OPCIONALES = {"version", "actualizado", "actualizado_por", "reemplazada_por", "pendientes", "palabras_clave"}
SECCIONES = ["Requisitos", "Pasos", "Pago", "Plazo", "Enviar a", "Siguiente fase"]
CLAVES_INTENT = ["descripcion", "entidades", "ejemplos", "ficha_relacionada", "si_falta_entidad"]
RE_ID = re.compile(r"^(TES|TSP|PPP|BAC|CPP|TRA|GEN)_[A-Z][0-9]{2}$")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MIN_EJEMPLOS = 10
MIN_GOLDEN = 10


def leer_encabezado(texto):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", texto, re.S)
    if not m:
        return None, texto
    campos = {}
    for linea in m.group(1).splitlines():
        if ":" in linea and not linea.startswith(" "):
            clave, valor = linea.split(":", 1)
            campos[clave.strip()] = valor.split("  #")[0].strip()
    return campos, m.group(2)


def validar_fichas(carpeta, errores, avisos):
    fichas = {}
    dir_fichas = carpeta / "fichas"
    if not dir_fichas.is_dir():
        errores.append("falta la carpeta fichas/")
        return fichas
    for f in sorted(dir_fichas.glob("*.md")):
        enc, cuerpo = leer_encabezado(f.read_text(encoding="utf-8"))
        if enc is None:
            errores.append(f"{f.name}: sin encabezado ---")
            continue
        for c in CAMPOS:
            if not enc.get(c):
                errores.append(f"{f.name}: campo vacío o ausente '{c}'")
        extra = set(enc) - set(CAMPOS) - OPCIONALES
        if extra:
            errores.append(f"{f.name}: campos no previstos {sorted(extra)}")
        fid = enc.get("id", "")
        if not RE_ID.match(fid):
            errores.append(f"{f.name}: id '{fid}' no cumple PREFIJO_X00")
        elif f.stem != fid:
            errores.append(f"{f.name}: el nombre del archivo no coincide con id '{fid}'")
        elif PREFIJOS[fid[:3]] != enc.get("proceso"):
            errores.append(f"{f.name}: prefijo {fid[:3]} no corresponde a proceso '{enc.get('proceso')}'")
        if enc.get("estado") not in ("confirmado", "pendiente"):
            errores.append(f"{f.name}: estado debe ser confirmado | pendiente")
        if not (RE_FECHA.match(enc.get("vigencia", "")) or enc.get("vigencia") == "no indicada"):
            errores.append(f"{f.name}: vigencia debe ser AAAA-MM-DD o 'no indicada'")
        if not enc.get("fase", "").isdigit():
            errores.append(f"{f.name}: fase debe ser un entero >= 0")
        titulos = re.findall(r"^## (.+?)\s*$", cuerpo, re.M)
        faltan = [s for s in SECCIONES if s not in titulos]
        if faltan:
            errores.append(f"{f.name}: faltan secciones {faltan}")
        fichas[fid] = enc
    if not fichas:
        errores.append("fichas/ no contiene fichas .md")
    return fichas


def leer_intents(ruta):
    """Parser mínimo para el formato de intents.yaml del contrato."""
    intents, actual, en_ejemplos = [], None, False
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s*#", linea) or not linea.strip():
            continue
        m = re.match(r"^- intent:\s*(\S+)", linea)
        if m:
            actual = {"intent": m.group(1), "claves": set(), "n_ejemplos": 0}
            intents.append(actual)
            en_ejemplos = False
            continue
        if actual is None:
            continue
        m = re.match(r"^  (\w+):(.*)$", linea)
        if m:
            clave, valor = m.group(1), m.group(2).strip()
            actual["claves"].add(clave)
            actual[clave] = valor
            en_ejemplos = clave == "ejemplos"
        elif en_ejemplos and re.match(r"^    - \S", linea):
            actual["n_ejemplos"] += 1
    return intents


def validar_intents(carpeta, fichas, errores):
    ruta = carpeta / "intents.yaml"
    if not ruta.is_file():
        errores.append("falta intents.yaml")
        return {}
    intents = leer_intents(ruta)
    if not intents:
        errores.append("intents.yaml no contiene intents")
    for it in intents:
        nombre = it["intent"]
        if nombre[:3] not in PREFIJOS or nombre[3] != "_":
            errores.append(f"intent {nombre}: prefijo no válido")
        for c in CLAVES_INTENT:
            if c not in it["claves"]:
                errores.append(f"intent {nombre}: falta '{c}'")
        if it["n_ejemplos"] < MIN_EJEMPLOS:
            errores.append(f"intent {nombre}: {it['n_ejemplos']} ejemplos (mínimo {MIN_EJEMPLOS})")
        ref = it.get("ficha_relacionada", "").strip("\"'")
        if ref:
            patron = re.compile("^" + re.escape(ref).replace(r"\*", ".*") + "$")
            if not any(patron.match(fid) for fid in fichas):
                errores.append(f"intent {nombre}: ficha_relacionada '{ref}' no coincide con ninguna ficha")
    return {it["intent"]: it for it in intents}


def validar_flujo(carpeta, errores, avisos):
    ruta = carpeta / "flujo.md"
    if not ruta.is_file():
        errores.append("falta flujo.md")
        return
    texto = ruta.read_text(encoding="utf-8")
    if "```mermaid" not in texto:
        errores.append("flujo.md: no contiene diagramas Mermaid")
    if "GEN_derivar_humano" not in texto:
        errores.append("flujo.md: no referencia GEN_derivar_humano")
    if not re.search(r"desambig", texto, re.I):
        avisos.append("flujo.md: no se menciona la desambiguación")
    if not re.search(r"cierre", texto, re.I):
        avisos.append("flujo.md: no se menciona el cierre")


def validar_golden(carpeta, fichas, intents, errores):
    ruta = carpeta / "golden_set.csv"
    if not ruta.is_file():
        errores.append("falta golden_set.csv")
        return 0
    with ruta.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    esperadas = ["id", "pregunta", "intent_esperado", "ficha_esperada", "respuesta_clave"]
    if not filas or list(filas[0].keys()) != esperadas:
        errores.append(f"golden_set.csv: encabezado debe ser {','.join(esperadas)}")
        return len(filas)
    por_prefijo = {}
    for fila in filas:
        por_prefijo[fila["id"][:3]] = por_prefijo.get(fila["id"][:3], 0) + 1
        for c in esperadas:
            if not (fila.get(c) or "").strip():
                errores.append(f"golden {fila['id']}: '{c}' vacío")
        if intents and fila["intent_esperado"] not in intents and not fila["intent_esperado"].startswith("GEN_"):
            errores.append(f"golden {fila['id']}: intent '{fila['intent_esperado']}' no existe en intents.yaml")
        if fichas and fila["ficha_esperada"] not in fichas:
            errores.append(f"golden {fila['id']}: ficha '{fila['ficha_esperada']}' no existe")
    for prefijo, n in por_prefijo.items():
        if n < MIN_GOLDEN:
            errores.append(f"golden_set.csv: {prefijo}_ tiene {n} preguntas (mínimo {MIN_GOLDEN})")
    return len(filas)


def validar_pendientes(carpeta, fichas, errores, avisos):
    ruta = carpeta / "pendientes.md"
    if not ruta.is_file():
        errores.append("falta pendientes.md")
        return
    texto = ruta.read_text(encoding="utf-8")
    for fid, enc in fichas.items():
        if enc.get("estado") == "pendiente" and fid not in texto:
            avisos.append(f"{fid} está pendiente pero no aparece en pendientes.md")


def validar_proceso(carpeta):
    errores, avisos = [], []
    fichas = validar_fichas(carpeta, errores, avisos)
    intents = validar_intents(carpeta, fichas, errores)
    validar_flujo(carpeta, errores, avisos)
    if not (carpeta / "plantillas.md").is_file():
        errores.append("falta plantillas.md")
    n_golden = validar_golden(carpeta, fichas, intents, errores)
    validar_pendientes(carpeta, fichas, errores, avisos)
    resumen = {
        "carpeta": carpeta.name,
        "fichas": len(fichas),
        "pendientes": sum(1 for e in fichas.values() if e.get("estado") == "pendiente"),
        "intents": len(intents),
        "golden": n_golden,
        "errores": errores,
        "avisos": avisos,
    }
    return resumen


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # consolas Windows (cp1252)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    raiz = Path(args[0] if args else ".").resolve()
    if (raiz / "fichas").is_dir():
        carpetas = [raiz]
    else:
        carpetas = [d for d in sorted(raiz.iterdir()) if d.is_dir() and not d.name.startswith(("00_", "."))]
    resultados = [validar_proceso(c) for c in carpetas]
    total_errores = 0
    for r in resultados:
        estado = "CUMPLE" if not r["errores"] else "NO CUMPLE"
        print(f"\n== {r['carpeta']}: {estado} "
              f"({r['fichas']} fichas, {r['pendientes']} pendientes, {r['intents']} intents, {r['golden']} preguntas)")
        for e in r["errores"]:
            print(f"  ERROR  {e}")
        for a in r["avisos"]:
            print(f"  AVISO  {a}")
        total_errores += len(r["errores"])
    if "--md" in sys.argv:
        print("\n| Carpeta | Fichas | Fichas pendientes | Intents | Golden set | Errores | Estado |")
        print("|---|---|---|---|---|---|---|")
        for r in resultados:
            estado = "✅ Cumple" if not r["errores"] else "❌ No cumple"
            print(f"| `{r['carpeta']}/` | {r['fichas']} | {r['pendientes']} | {r['intents']} | {r['golden']} | {len(r['errores'])} | {estado} |")
    sys.exit(1 if total_errores else 0)


if __name__ == "__main__":
    main()
