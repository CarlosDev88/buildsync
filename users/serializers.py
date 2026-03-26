from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extiende el payload del JWT con datos del usuario para que el frontend
    no necesite hacer un request adicional a /me/ solo para saber el rol.

    Payload extra incluido en el token:
      - role       → para mostrar el menú correcto en el frontend
      - full_name  → para el saludo en la UI
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = f"{user.first_name} {user.last_name}".strip() or user.username
        return token
