import uuid
from django.conf import settings
from django.db import models
# ¡Aquí ocurre la magia! Traemos el Proyecto desde el catálogo
from catalogue.models import Project
from catalogue.models.properties import Property
from .unit_prices import Activity
from .resources import Resource

class ProjectPhase(models.Model):
    """Las etapas grandes de la obra (Ej: Cimentación, Estructura, Acabados)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Conectamos con el proyecto que se creó en la vitrina
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases', verbose_name="Proyecto")
    
    name = models.CharField(max_length=100, verbose_name="Nombre de la Fase", help_text="Ej: Torre 1 - Cimentación")
    start_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio Estimada")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Fin Estimada")

    class PhaseStatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        ACTIVE = 'ACTIVE', 'Activa'
        PAUSED = 'PAUSED', 'Pausada'
        COMPLETED = 'COMPLETED', 'Completada'

    status = models.CharField(max_length=20, choices=PhaseStatusChoices.choices, default=PhaseStatusChoices.PENDING, verbose_name="Estado de la Fase")

    class Meta:
        verbose_name = "Fase del Proyecto"
        verbose_name_plural = "3. Fases de Obra"
        ordering = ['project', 'start_date']

    def __str__(self):
        return f"{self.name} - {self.project.name}"


class Task(models.Model):
    """La Tarjeta del Kanban. Lo que el maestro de obra tiene que hacer hoy."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, related_name='tasks', verbose_name="Fase de la Obra")
    # Unidad (apartamento/local) a la que corresponde esta tarea. Null = área común.
    unit = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='construction_tasks', verbose_name="Unidad del Proyecto", help_text="Apartamento o local que se está construyendo. Vacío si es área común.")

    # ¿Qué A.P.U. (receta) vamos a construir en esta tarjeta?
    activity = models.ForeignKey(Activity, on_delete=models.RESTRICT, verbose_name="Actividad (A.P.U.) a ejecutar")

    # --- EL CORAZÓN DEL KANBAN ---
    class StatusChoices(models.TextChoices):
        TODO = 'TODO', 'Por Hacer'
        IN_PROGRESS = 'IN_PROGRESS', 'En Progreso'
        REVIEW = 'REVIEW', 'En Revisión / Calidad'
        DONE = 'DONE', 'Terminada'

    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.TODO, verbose_name="Estado Kanban")

    # --- LO PLANEADO VS LO REAL ---
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Cantidad Planeada", help_text="Cuánto se mandó a hacer. Ej: 50 (m2)")
    executed_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Cantidad Ejecutada", help_text="Cuánto lleva hecho el contratista")

    class Meta:
        verbose_name = "Tarea (Kanban)"
        verbose_name_plural = "4. Tareas (Kanban)"

    def __str__(self):
        return f"[{self.get_status_display()}] {self.activity.name} - {self.phase.name}"


class TaskConsumption(models.Model):
    """
    El 'Dolor de Cabeza' de toda constructora: Lo que REALMENTE se gastaron en la obra
    vs lo que decía la receta (A.P.U.).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='consumptions', verbose_name="Tarea")
    resource = models.ForeignKey(Resource, on_delete=models.RESTRICT, verbose_name="Insumo Gastado")
    
    quantity_used = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Cantidad Real Usada")
    date_reported = models.DateField(auto_now_add=True, verbose_name="Fecha del Reporte")
    logged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='consumption_reports', verbose_name="Reportado por", help_text="Usuario que registró este consumo real.")

    class Meta:
        verbose_name = "Reporte de Consumo"
        verbose_name_plural = "5. Consumos Reales"

    def __str__(self):
        return f"Gastó {self.quantity_used} {self.resource.get_unit_of_measure_display()} de {self.resource.name} en {self.task.activity.code}"