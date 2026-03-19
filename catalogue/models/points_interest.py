import uuid
from django.db import models
from .projects import Project

class POICategory(models.Model):
    """Categorías principales: Centros Comerciales, Parques, Transmilenio, etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, help_text="Ej: Parques, Supermercados")
    icon_identifier = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Clave para el frontend (ej: 'icon-park', 'icon-mall')"
    )

    def __str__(self):
        return self.name


class PointOfInterest(models.Model):
    """El sitio específico y a qué distancia está del Proyecto"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='points_of_interest')
    category = models.ForeignKey(POICategory, on_delete=models.RESTRICT, related_name='pois')
    
    name = models.CharField(max_length=100, help_text="Ej: Centro Comercial Hayuelos")
    
    # Manejo exacto de los iconos de la imagen (caminando, carro, bici)
    class TravelModeChoices(models.TextChoices):
        WALKING = 'WALKING', 'Caminando'
        DRIVING = 'DRIVING', 'Carro'
        BIKING = 'BIKING', 'Bicicleta'
        TRANSIT = 'TRANSIT', 'Transporte Público'

    travel_mode = models.CharField(max_length=20, choices=TravelModeChoices.choices, default=TravelModeChoices.WALKING)
    time_in_minutes = models.IntegerField(help_text="Tiempo de desplazamiento en minutos")

    class Meta:
        verbose_name_plural = "Points of Interest"
        # Para que en el admin se ordenen por categoría automáticamente
        ordering = ['category__name', 'time_in_minutes'] 

    def __str__(self):
        return f"{self.name} ({self.time_in_minutes} min {self.get_travel_mode_display()}) - {self.project.name}"