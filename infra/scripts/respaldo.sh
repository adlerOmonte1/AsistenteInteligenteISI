#!/usr/bin/env bash
# Respaldo diario de la base de datos y de los documentos subidos.
# Programar con cron (ver docs/05-despliegue/operacion.md):
#   0 2 * * * /opt/asistente/infra/scripts/respaldo.sh >> /var/log/asistente-respaldo.log 2>&1
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
DESTINO="${DESTINO_RESPALDOS:-/var/backups/asistente}"
DIAS="${DIAS_RETENCION:-14}"
FECHA="$(date +%Y%m%d-%H%M)"
COMPOSE=(docker compose -f "$RAIZ/infra/docker-compose.yml" --env-file "$RAIZ/.env")

mkdir -p "$DESTINO"
source "$RAIZ/.env"

"${COMPOSE[@]}" exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom \
  > "$DESTINO/base-$FECHA.dump"

"${COMPOSE[@]}" exec -T api tar -czf - -C /app media > "$DESTINO/media-$FECHA.tar.gz"

find "$DESTINO" -type f \( -name 'base-*.dump' -o -name 'media-*.tar.gz' \) -mtime +"$DIAS" -delete
echo "$(date -Is) respaldo completo en $DESTINO ($FECHA)"
