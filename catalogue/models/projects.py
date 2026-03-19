import uuid
from django.db import models

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, help_text="Nombre del proyecto de obra nueva")
    
    class StatusChoices(models.TextChoices):
        PLANNING = 'PLANNING', 'En Planos'
        CONSTRUCTION = 'CONSTRUCTION', 'En Construcción'
        DELIVERED = 'DELIVERED', 'Entregado'
        
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PLANNING)
    is_demo = models.BooleanField(default=False, help_text="Si es True, este proyecto lo verá el rol Invitado Demo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {'(DEMO)' if self.is_demo else ''}"