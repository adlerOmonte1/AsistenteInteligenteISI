# Guía de despliegue

Instalación del Asistente Académico en un servidor Linux con Docker. Está escrita para el Centro de Cómputo de la UDH, pero sirve para cualquier servidor o VPS.

Tiempo estimado: una hora, la mayor parte esperando descargas.

## 1. Requisitos

| Recurso | Mínimo |
|---|---|
| Sistema operativo | Ubuntu 22.04 o 24.04 LTS |
| CPU / RAM / disco | 2 vCPU · 4 GB · 40 GB |
| Red | IP pública (o publicada por el firewall de la UDH) con los puertos 80 y 443 abiertos |
| Dominio | Un subdominio (p. ej. `asistente.udh.edu.pe`) apuntando a esa IP |
| Servicios externos | Una API key de Gemini (u otro proveedor, ver ADR-0004) |

Si no hay servidor disponible, un VPS equivalente cuesta entre 6 y 12 USD al mes.

## 2. Preparar el servidor

```bash
sudo apt update && sudo apt upgrade -y
```

```bash
curl -fsSL https://get.docker.com | sudo sh
```

```bash
sudo usermod -aG docker $USER
```

Cierre la sesión SSH y vuelva a entrar para que el grupo `docker` tenga efecto. Compruebe:

```bash
docker compose version
```

## 3. Obtener el código

```bash
sudo mkdir -p /opt/asistente && sudo chown $USER /opt/asistente
```

```bash
git clone https://github.com/adlerOmonte1/AsistenteInteligenteISI.git /opt/asistente
```

Todos los comandos siguientes se ejecutan desde `/opt/asistente`. Para abreviar, defina:

```bash
cd /opt/asistente && alias dc='docker compose -f infra/docker-compose.yml --env-file .env'
```

## 4. Configurar el entorno

```bash
cp .env.example .env && chmod 600 .env
```

Edite `.env` (`nano .env`) y complete como mínimo:

| Variable | Valor |
|---|---|
| `DOMINIO` | El subdominio asignado, sin `https://` |
| `DJANGO_SECRET_KEY` | Una clave aleatoria: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_ALLOWED_HOSTS` | El mismo subdominio |
| `CSRF_TRUSTED_ORIGINS` | `https://` + subdominio |
| `CORS_ALLOWED_ORIGINS` | `https://` + subdominio y cada dominio que inserte el widget |
| `POSTGRES_PASSWORD` | Una contraseña larga; repítala dentro de `DATABASE_URL` |
| `LLM_API_KEY` | La clave de Gemini |
| `LIMITE_USD_MES` | Tope interno de gasto (por defecto 8) |

Borre la línea `DEMO_PASSWORD`: las cuentas de demostración no se usan en producción.

## 5. Certificado HTTPS (primera vez)

Nginx no arranca sin certificado, así que el primero se pide antes de levantar el sistema, con certbot en modo autónomo (usa el puerto 80 un momento):

```bash
dc --profile certificados run --rm -p 80:80 certbot certonly --standalone -d "$(grep ^DOMINIO .env | cut -d= -f2)" --email correo-del-centro@udh.edu.pe --agree-tos --no-eff-email
```

El certificado queda en `infra/certbot/conf/`. Si falla, revise que el subdominio ya apunte a la IP del servidor (`ping <subdominio>`).

## 6. Levantar el sistema

```bash
dc up -d --build
```

La primera vez tarda varios minutos (compila el frontend dentro de la imagen). Al terminar:

```bash
dc ps
```

Los servicios `db`, `api`, `worker` y `web` deben estar `running`, y `api` en estado `healthy`. La API aplica las migraciones sola al arrancar.

## 7. Carga inicial

Cree la cuenta del Centro de Cómputo (rol `superadmin`):

```bash
dc exec api python manage.py createsuperuser
```

Cargue la base de conocimiento sin gastar cuota del proveedor:

```bash
dc exec api python manage.py importar_conocimiento --sin-indexar
```

Calcule los embeddings con Gemini (con el plan gratuito puede tardar dos días por la cuota diaria; vuelva a ejecutarlo hasta que diga «Índice completo»):

```bash
dc exec api python manage.py reindexar
```

## 8. Verificación

| Prueba | Resultado esperado |
|---|---|
| `https://<subdominio>/api/v1/health/` | `{"estado": "ok"}` |
| `https://<subdominio>/` | Portal con la lista de trámites |
| `https://<subdominio>/admin/` | Pantalla de ingreso del panel |
| Panel → Configuración | Proveedor `gemini` y modelo correcto |
| Panel → Probador: «¿cuántas fotos necesito para el bachiller?» | Vía determinista, ficha `BAC_P02` |
| Panel → Golden set → Ejecutar | Termina en estado «completada» (prueba que el worker funciona) |

## 9. Tareas programadas del servidor

Edite el cron del usuario (`crontab -e`) y agregue:

```cron
# Respaldo diario a las 02:00 (base de datos + documentos), 14 días de retención
0 2 * * * /opt/asistente/infra/scripts/respaldo.sh >> /var/log/asistente-respaldo.log 2>&1
# Renovación del certificado HTTPS, dos veces por semana
30 3 * * 1,4 cd /opt/asistente && docker compose -f infra/docker-compose.yml --env-file .env --profile certificados run --rm certbot renew --webroot -w /var/www/certbot --quiet && docker compose -f infra/docker-compose.yml --env-file .env exec web nginx -s reload
```

```bash
chmod +x infra/scripts/*.sh && sudo touch /var/log/asistente-respaldo.log && sudo chown $USER /var/log/asistente-respaldo.log
```

La purga de consultas con más de 12 meses la hace el worker todos los días; no necesita cron.

## 10. Monitoreo

Registre `https://<subdominio>/api/v1/health/` en un servicio de monitoreo (UptimeRobot o el que use el Centro de Cómputo) con revisión cada 5 minutos. Responde 503 si la base de datos no está disponible.

## 11. Actualizar a una versión nueva

```bash
cd /opt/asistente && git pull && dc up -d --build
```

Las migraciones se aplican solas. Si la versión nueva trae fichas nuevas en `knowledge-base/`, ejecute también `importar_conocimiento` (y `reindexar` si se indicó `--sin-indexar`).

## 12. Demostración sin dominio ni HTTPS

Para mostrar el sistema en una red interna antes de tener subdominio:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.http.yml --env-file .env up -d --build
```

Se accede por `http://<ip-del-servidor>/`. El portal y el chat funcionan; el panel funciona, pero pide ingresar de nuevo al recargar la página, porque la cookie de sesión exige HTTPS (ADR-0010). No use este modo en producción.

## 13. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `web` se reinicia en bucle | No existe el certificado | Paso 5; revise `dc logs web` |
| `api` queda `unhealthy` | `.env` incompleto o base inaccesible | `dc logs api`; revise `DATABASE_URL` y `DJANGO_SECRET_KEY` |
| El panel dice «No hay conexión con el servidor» | La API no responde | `dc ps` y `dc logs api` |
| El chat responde copiando fichas, sin redactar | Sin clave, cuota agotada o tope de gasto | Panel → Conversaciones: motivo `error_proveedor_llm` o `limite_de_gasto` |
| El widget no carga en otra web | Dominio no autorizado | Agregar el dominio a `CORS_ALLOWED_ORIGINS` y `dc up -d` |
| Evaluaciones quedan «pendiente» | El worker no corre | `dc logs worker`; `dc restart worker` |
