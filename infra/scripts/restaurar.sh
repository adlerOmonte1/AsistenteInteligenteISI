#!/usr/bin/env bash
# Restaura un respaldo de la base de datos. Uso:
#   infra/scripts/restaurar.sh /var/backups/asistente/base-20261201-0200.dump
# Detiene la API y el worker mientras restaura.
set -euo pipefail

ARCHIVO="${1:?Indique el archivo .dump a restaurar}"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
COMPOSE=(docker compose -f "$RAIZ/infra/docker-compose.yml" --env-file "$RAIZ/.env")
source "$RAIZ/.env"

read -r -p "Se reemplazará la base $POSTGRES_DB con $ARCHIVO. ¿Continuar? (escriba SI) " RESPUESTA
[ "$RESPUESTA" = "SI" ] || { echo "Cancelado."; exit 1; }

"${COMPOSE[@]}" stop api worker
"${COMPOSE[@]}" exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists < "$ARCHIVO"
"${COMPOSE[@]}" start api worker
echo "Restauración terminada."
