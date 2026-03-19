from django.contrib import admin
from .models import Client, FinancialProfile, Opportunity, Document, PaymentPlan, InteractionLog

# --- INLINES (Las tablas anidadas dentro de la Oportunidad) ---

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0  # No muestra filas vacías por defecto, solo el botón "Agregar"

class InteractionLogInline(admin.TabularInline):
    model = InteractionLog
    extra = 1

class PaymentPlanInline(admin.StackedInline): 
    # Usamos StackedInline porque el plan de pagos tiene muchos campos 
    # y en formato tabla (Tabular) se vería muy amontonado.
    model = PaymentPlan

# --- REGISTROS PRINCIPALES ---

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'lead_source', 'created_at')
    list_filter = ('lead_source',)
    search_fields = ('first_name', 'last_name', 'phone', 'email')

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('client', 'property_of_interest', 'stage', 'assigned_to', 'is_pre_approved')
    list_filter = ('stage', 'is_pre_approved', 'assigned_to')
    # Permite buscar oportunidades escribiendo el nombre del cliente
    search_fields = ('client__first_name', 'client__last_name') 
    
    # ¡El poder del CRM! Anidamos todo el contexto de la venta aquí:
    inlines = [PaymentPlanInline, DocumentInline, InteractionLogInline]

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'document_type', 'status', 'uploaded_at')
    list_filter = ('status', 'document_type')
