"""
Permission classes basadas en roles para la API de PropSync.

Uso en vistas:
    from users.permissions import IsAsesor, IsAdminOrGerente

    class MyView(APIView):
        permission_classes = [IsAsesor]

Composición con OR:
    permission_classes = [IsAdmin | IsGerente]

Composición con AND (autenticado Y con rol):
    permission_classes = [IsAuthenticated, IsJefeObra]
"""
from rest_framework.permissions import BasePermission
from .models import CustomUser


class _HasRole(BasePermission):
    """Base interna. No usar directamente."""
    allowed_roles: tuple = ()

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsAdmin(_HasRole):
    """Solo SUPER_ADMIN. Gestión de catálogos, productos de crédito, usuarios."""
    allowed_roles = (CustomUser.RoleChoices.SUPER_ADMIN,)


class IsGerente(_HasRole):
    """Solo GERENTE. Dashboards, reportes, vista de cartera y rentabilidad."""
    allowed_roles = (CustomUser.RoleChoices.GERENTE,)


class IsAsesor(_HasRole):
    """Solo ASESOR. CRM: clientes, oportunidades, documentos."""
    allowed_roles = (CustomUser.RoleChoices.ASESOR,)


class IsAnalistaCredito(_HasRole):
    """Solo ANALISTA_CREDITO. Revisión y aprobación de solicitudes."""
    allowed_roles = (CustomUser.RoleChoices.ANALISTA_CREDITO,)


class IsJefeObra(_HasRole):
    """Solo JEFE_OBRA. Kanban de tareas y reporte de consumos."""
    allowed_roles = (CustomUser.RoleChoices.JEFE_OBRA,)


# ── Combinaciones frecuentes ──────────────────────────────────────────────────

class IsAdminOrGerente(_HasRole):
    """Admin o Gerente. Acceso a configuración y reportes ejecutivos."""
    allowed_roles = (
        CustomUser.RoleChoices.SUPER_ADMIN,
        CustomUser.RoleChoices.GERENTE,
    )


class IsAdminOrAsesor(_HasRole):
    """Admin o Asesor. Operaciones del CRM."""
    allowed_roles = (
        CustomUser.RoleChoices.SUPER_ADMIN,
        CustomUser.RoleChoices.ASESOR,
    )


class IsAdminOrAnalista(_HasRole):
    """Admin o Analista. Gestión de solicitudes de crédito."""
    allowed_roles = (
        CustomUser.RoleChoices.SUPER_ADMIN,
        CustomUser.RoleChoices.ANALISTA_CREDITO,
    )


class IsAdminOrJefeObra(_HasRole):
    """Admin o Jefe de Obra. Gestión del ERP de construcción."""
    allowed_roles = (
        CustomUser.RoleChoices.SUPER_ADMIN,
        CustomUser.RoleChoices.JEFE_OBRA,
    )


class IsAnyStaff(_HasRole):
    """Cualquier usuario interno (no DEMO_GUEST). Para endpoints generales."""
    allowed_roles = (
        CustomUser.RoleChoices.SUPER_ADMIN,
        CustomUser.RoleChoices.GERENTE,
        CustomUser.RoleChoices.ASESOR,
        CustomUser.RoleChoices.ANALISTA_CREDITO,
        CustomUser.RoleChoices.JEFE_OBRA,
    )
