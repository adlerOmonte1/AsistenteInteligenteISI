from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from comun.permisos import EsLector, EsSuperadmin

from . import services
from .models import Usuario
from .serializers import LoginSerializer, UsuarioActualSerializer, UsuarioSerializer


def _respuesta_sesion(usuario, refresh):
    respuesta = Response({"access": str(refresh.access_token), "usuario": UsuarioActualSerializer(usuario).data})
    services.poner_cookie_refresh(respuesta, str(refresh))
    return respuesta


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=LoginSerializer, responses={200: dict})
    def post(self, request):
        datos = LoginSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        usuario, refresh = services.iniciar_sesion(**datos.validated_data)
        return _respuesta_sesion(usuario, refresh)


class RefreshView(APIView):
    """Renueva el access leyendo el refresh de la cookie HttpOnly; rota el refresh."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=None, responses={200: dict})
    def post(self, request):
        token = services.leer_cookie_refresh(request)
        if not token:
            return Response({"detalle": "Sesión no iniciada.", "errores": {}}, status=401)
        try:
            anterior = RefreshToken(token)
            usuario = Usuario.objects.get(pk=anterior["user_id"], is_active=True)
            anterior.blacklist()
        except (TokenError, Usuario.DoesNotExist):
            respuesta = Response({"detalle": "La sesión expiró.", "errores": {}}, status=401)
            services.borrar_cookie_refresh(respuesta)
            return respuesta
        return _respuesta_sesion(usuario, services.emitir_refresh(usuario))


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        token = services.leer_cookie_refresh(request)
        if token:
            try:
                RefreshToken(token).blacklist()
            except TokenError:
                pass
        respuesta = Response(status=status.HTTP_204_NO_CONTENT)
        services.borrar_cookie_refresh(respuesta)
        return respuesta


class MeView(APIView):
    permission_classes = [EsLector]

    @extend_schema(responses=UsuarioActualSerializer)
    def get(self, request):
        return Response(UsuarioActualSerializer(request.user).data)


class UsuarioViewSet(viewsets.ModelViewSet):
    """Cuentas del panel. Solo el Centro de Cómputo las crea; no se borran, se desactivan."""

    queryset = Usuario.objects.select_related("facultad")
    serializer_class = UsuarioSerializer
    permission_classes = [EsSuperadmin]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        rol = self.request.query_params.get("rol")
        return qs.filter(rol=rol) if rol else qs
