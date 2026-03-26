import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Usar UUID en lugar de IDs secuenciales (1, 2, 3) es vital para seguridad en APIs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Definición estricta de Roles usando TextChoices
    class RoleChoices(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Administrador'
        GERENTE = 'GERENTE', 'Gerente de Proyecto'
        ASESOR = 'ASESOR', 'Asesor Comercial'
        ANALISTA_CREDITO = 'ANALISTA_CREDITO', 'Analista de Crédito'
        JEFE_OBRA = 'JEFE_OBRA', 'Jefe de Obra'
        DEMO_GUEST = 'DEMO_GUEST', 'Invitado Demo'

    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.DEMO_GUEST,
        help_text="Rol principal del usuario en la plataforma."
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
