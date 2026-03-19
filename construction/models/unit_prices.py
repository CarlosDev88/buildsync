import uuid
from django.db import models
from .resources import Resource

class Activity(models.Model):
    """
    La 'Receta' maestra. Representa 1 unidad de obra (ej: 1 m2 de muro, 1 ml de tubería).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, verbose_name="Código A.P.U.", help_text="Ej: MUR-01, EXC-05")
    name = models.CharField(max_length=200, verbose_name="Nombre de la Actividad", help_text="Ej: Muro en ladrillo prensado a la vista")
    
    # Las unidades para cobrar la obra terminada suelen ser un poco distintas a las de los insumos
    class UnitChoices(models.TextChoices):
        M2 = 'M2', 'Metro Cuadrado (m2)'
        M3 = 'M3', 'Metro Cúbico (m3)'
        ML = 'ML', 'Metro Lineal (ml)'
        UND = 'UND', 'Unidad (und)'
        GL = 'GL', 'Global (gl)'

    unit_of_measure = models.CharField(max_length=10, choices=UnitChoices.choices, verbose_name="Unidad de Medida", default=UnitChoices.M2)
    
    class Meta:
        verbose_name = "Actividad (A.P.U.)"
        verbose_name_plural = "2. Actividades (A.P.U.)"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_unit_of_measure_display()})"


class APUDetail(models.Model):
    """
    Los ingredientes de la receta. Cuánto insumo se gasta para hacer 1 unidad de la Actividad.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Las llaves foráneas que conectan el mundo
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='details', verbose_name="Actividad")
    resource = models.ForeignKey(Resource, on_delete=models.RESTRICT, related_name='apu_usages', verbose_name="Recurso / Insumo")
    
    # Fíjate que usamos 4 decimales. En obra, a veces usas 0.0025 m3 de algo.
    quantity = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Cantidad Unitaria", help_text="Cuánto se usa para 1 unidad de obra")
    
    waste_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="% Desperdicio", help_text="Ej: 5.00 para 5% de rotura/pérdida")

    class Meta:
        verbose_name = "Detalle de Insumo"
        verbose_name_plural = "Detalles del A.P.U."
        # Evita que el ingeniero meta dos veces "Cemento" en la misma receta
        unique_together = ('activity', 'resource') 

    def __str__(self):
        return f"{self.quantity} {self.resource.get_unit_of_measure_display()} de {self.resource.name}"