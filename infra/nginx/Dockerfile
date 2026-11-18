# Compila el portal, el panel y el widget, y los sirve con Nginx junto al proxy de la API.
# El servidor no necesita Node instalado: todo ocurre dentro de esta imagen.
#   docker build -f infra/nginx/Dockerfile -t asistente-web .
FROM node:24-alpine AS compilacion
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ .
RUN npm run build

FROM nginx:1.29-alpine
COPY infra/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=compilacion /frontend/dist/portal/browser /usr/share/nginx/portal
COPY --from=compilacion /frontend/dist/admin/browser /usr/share/nginx/admin
COPY --from=compilacion /frontend/dist/widget/browser /usr/share/nginx/widget
