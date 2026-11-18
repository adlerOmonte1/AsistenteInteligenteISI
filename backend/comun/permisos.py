"""Permisos por rol, compartidos por todas las apps del panel.

El frontend oculta lo que un rol no puede hacer, pero el control real está aquí.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

JERARQUIA = {"lector": 1, "editor": 2, "revisor": 3, "superadmin": 4}


def tiene_rol(usuario, minimo: str) -> bool:
    if not usuario or not usuario.is_authenticated:
        return False
    return JERARQUIA.get(usuario.rol, 0) >= JERARQUIA[minimo]


class EsLector(BasePermission):
    def has_permission(self, request, view):
        return tiene_rol(request.user, "lector")


class EsEditor(BasePermission):
    def has_permission(self, request, view):
        return tiene_rol(request.user, "editor")


class EsRevisor(BasePermission):
    def has_permission(self, request, view):
        return tiene_rol(request.user, "revisor")


class EsSuperadmin(BasePermission):
    def has_permission(self, request, view):
        return tiene_rol(request.user, "superadmin")


class LecturaLectorEscrituraEditor(BasePermission):
    """GET para cualquier rol del panel; POST/PATCH/DELETE desde editor."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return tiene_rol(request.user, "lector")
        return tiene_rol(request.user, "editor")


class MismaFacultad(BasePermission):
    """Un usuario con facultad asignada solo opera objetos de esa facultad."""

    def has_object_permission(self, request, view, obj):
        facultad_usuario = getattr(request.user, "facultad_id", None)
        if facultad_usuario is None or request.user.rol == "superadmin":
            return True
        facultad_obj = getattr(obj, "facultad_id", None)
        if facultad_obj is None and hasattr(obj, "proceso"):
            facultad_obj = obj.proceso.programa.facultad_id
        return facultad_obj in (None, facultad_usuario)
