from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class MeView(APIView):
    """
    GET /api/auth/me/
    Devuelve el perfil del usuario autenticado.
    El frontend lo usa para mostrar nombre, rol y decidir qué menú renderizar.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'role': user.role,
            'role_display': user.get_role_display(),
        })
