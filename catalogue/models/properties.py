import uuid
from django.db import models
from .projects import Project


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='properties')

    class PropertyTypeChoices(models.TextChoices):
        APARTMENT = 'APARTMENT', 'Apartamento'
        HOUSE = 'HOUSE', 'Casa'
        COMMERCIAL = 'COMMERCIAL', 'Local Comercial'
        RURAL_LOT = 'RURAL_LOT', 'Lote Campestre'

    property_type = models.CharField(max_length=20, choices=PropertyTypeChoices.choices, default=PropertyTypeChoices.APARTMENT)
    property_name = models.CharField(max_length=50, help_text="Ej: Apt 402, Local 1")
    tower_or_block = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: Torre 1, Manzana B, Interior 3")
    floor_number = models.IntegerField(blank=True, null=True, help_text="Piso o Nivel. Ej: 4 (Útil para precios escalonados)")
    base_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Precio base sin acabados extra")
    
    class StatusChoices(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Disponible'
        RESERVED = 'RESERVED', 'Reservado'
        SOLD = 'SOLD', 'Vendido'
        BUILDING = 'BUILDING', 'En Construcción'
        DELIVERED = 'DELIVERED', 'Entregado'
        
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.AVAILABLE)

    def __str__(self):
        return f"{self.property_name} - {self.project.name}"