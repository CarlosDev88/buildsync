import uuid
from django.db import models

class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nombre del Insumo", help_text="Ej: Cemento Gris, Oficial de Construcción, Mezcladora")
    
    # 1. LA CATEGORÍA DEL INSUMO
    class ResourceTypeChoices(models.TextChoices):
        MATERIAL = 'MATERIAL', 'Material'
        LABOR = 'LABOR', 'Mano de Obra'
        EQUIPMENT = 'EQUIPMENT', 'Equipo / Herramienta'
        
    resource_type = models.CharField(max_length=20, choices=ResourceTypeChoices.choices, verbose_name="Tipo de Recurso")

    # 2. UNIDADES DE MEDIDA ESTÁNDAR EN CONSTRUCCIÓN
    class UnitChoices(models.TextChoices):
        KG = 'KG', 'Kilogramo (kg)'
        TON = 'TON', 'Tonelada (ton)'
        M3 = 'M3', 'Metro Cúbico (m3)'
        M2 = 'M2', 'Metro Cuadrado (m2)'
        ML = 'ML', 'Metro Lineal (ml)'
        UND = 'UND', 'Unidad (und)'
        BAG = 'BAG', 'Bulto (50kg)'
        HOUR = 'HOUR', 'Hora (hr)'
        DAY = 'DAY', 'Día (dia)'
        GL = 'GL', 'Galón (gl)'

    unit_of_measure = models.CharField(max_length=10, choices=UnitChoices.choices, verbose_name="Unidad de Medida")
    
    # 3. EL COSTO
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Costo Unitario ($)", help_text="Costo base sin impuestos")

    class Meta:
        verbose_name = "Recurso / Insumo"
        verbose_name_plural = "1. Recursos e Insumos" # El '1.' es un truco para que salga de primero en el menú del admin
        ordering = ['resource_type', 'name']

    def __str__(self):
        return f"[{self.get_resource_type_display()}] {self.name} - ${self.unit_price}/{self.get_unit_of_measure_display()}"