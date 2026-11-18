"""Comprueba que el modelo C4 y el código no se separen.

Cada app de backend/apps/ y cada feature de frontend/projects/*/src/app/features/
debe tener en docs/03-arquitectura/modelo-c4/workspace.dsl un elemento con la
propiedad "ruta" que apunte a ella, y cada "ruta" del modelo debe existir.

Uso: python scripts/validar_c4.py   (código de salida 1 si hay diferencias)
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DSL = RAIZ / "docs" / "03-arquitectura" / "modelo-c4" / "workspace.dsl"
RE_RUTA = re.compile(r'"ruta"\s+"([^"]+)"')


def rutas_en_codigo() -> set[str]:
    rutas = set()
    for app in (RAIZ / "backend" / "apps").iterdir():
        if app.is_dir() and (app / "apps.py").is_file():
            rutas.add(f"backend/apps/{app.name}")
    for proyecto in (RAIZ / "frontend" / "projects").iterdir():
        if not proyecto.is_dir():
            continue
        rutas.add(f"frontend/projects/{proyecto.name}")
        features = proyecto / "src" / "app" / "features"
        if features.is_dir():
            for feature in features.iterdir():
                if feature.is_dir():
                    rutas.add(f"frontend/projects/{proyecto.name}/src/app/features/{feature.name}")
    return rutas


def main() -> int:
    en_modelo = set(RE_RUTA.findall(DSL.read_text(encoding="utf-8")))
    en_codigo = rutas_en_codigo()
    sin_modelo = sorted(en_codigo - en_modelo)
    inexistentes = sorted(r for r in en_modelo if not (RAIZ / r).exists())

    for ruta in sin_modelo:
        print(f"FALTA EN C4   {ruta}: agregue un elemento con \"ruta\" \"{ruta}\" en workspace.dsl")
    for ruta in inexistentes:
        print(f"NO EXISTE     {ruta}: el modelo C4 apunta a una ruta que ya no está en el repositorio")
    if sin_modelo or inexistentes:
        return 1
    print(f"Modelo C4 al día: {len(en_codigo)} rutas de código con su elemento.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
