from django.contrib import admin
from .models import Resource, Activity, APUDetail, ProjectPhase, Task, TaskConsumption

# ==========================================
# 1. INLINES (Tablas Anidadas)
# ==========================================

class APUDetailInline(admin.TabularInline):
    """Permite armar la receta (los insumos) dentro de la misma pantalla de la Actividad."""
    model = APUDetail
    extra = 1  # Deja una fila en blanco lista para agregar un nuevo insumo
    autocomplete_fields = ['resource'] # ¡Súper útil si tienes miles de insumos!

class TaskInline(admin.TabularInline):
    """Permite crear las tarjetas del Kanban directamente desde la Fase del Proyecto."""
    model = Task
    extra = 1
    autocomplete_fields = ['activity']

class TaskConsumptionInline(admin.TabularInline):
    """Permite registrar lo que se gastó en la obra dentro de la tarjeta de la tarea."""
    model = TaskConsumption
    extra = 1
    autocomplete_fields = ['resource']

# ==========================================
# 2. REGISTROS PRINCIPALES
# ==========================================

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_type', 'unit_of_measure', 'unit_price')
    list_filter = ('resource_type', 'unit_of_measure')
    search_fields = ('name',)
    # Esto es obligatorio si queremos usar autocomplete_fields en los Inlines
    search_help_text = "Busca por nombre del insumo o recurso"

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'unit_of_measure')
    search_fields = ('code', 'name')
    # Aquí inyectamos la receta
    inlines = [APUDetailInline]

@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'start_date', 'end_date')
    list_filter = ('project',)
    search_fields = ('name', 'project__name')
    # Aquí inyectamos las tareas del Kanban
    inlines = [TaskInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('activity', 'phase', 'status', 'planned_quantity', 'executed_quantity')
    # Podemos filtrar por estado del Kanban o por el proyecto padre
    list_filter = ('status', 'phase__project')
    search_fields = ('activity__name', 'phase__name')
    # Aquí inyectamos los reportes de consumo diario
    inlines = [TaskConsumptionInline]

# Nota: No registramos TaskConsumption o APUDetail solos con @admin.register 
# porque no tiene sentido verlos huérfanos; siempre viven dentro de su padre (Task o Activity).
