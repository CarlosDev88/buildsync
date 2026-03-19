import uuid
from django.db import models
from .properties import Property

class FeatureCatalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, help_text="Ej: Habitaciones, Baños, Área m2, Parqueadero")
    
    class DataTypeChoices(models.TextChoices):
        NUMBER = 'NUMBER', 'Número'
        BOOLEAN = 'BOOLEAN', 'Sí/No'
        TEXT = 'TEXT', 'Texto Libre'
        
    data_type = models.CharField(max_length=20, choices=DataTypeChoices.choices, default=DataTypeChoices.NUMBER)

    def __str__(self):
        return self.name
    


class PropertyFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='features')
    feature = models.ForeignKey(FeatureCatalog, on_delete=models.RESTRICT)
    value = models.CharField(max_length=100, help_text="El valor real. Ej: '3' para habitaciones, 'True' para parqueadero")

    class Meta:
        # Evita que a una misma propiedad le asignen dos veces la característica "Habitaciones"
        unique_together = ('property', 'feature')

    def __str__(self):
        return f"{self.property.property_name} -> {self.feature.name}: {self.value}"    