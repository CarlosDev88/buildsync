from django.contrib import admin
from .models import LoanProduct, LoanApplication, AmortizationSchedule, StatusHistory


# ==========================================
# 1. INLINES
# ==========================================

class AmortizationScheduleInline(admin.TabularInline):
    """Tabla de amortización dentro de la solicitud. Solo lectura — la genera el motor."""
    model = AmortizationSchedule
    extra = 0
    readonly_fields = ('period', 'due_date', 'principal', 'interest', 'balance', 'paid_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class StatusHistoryInline(admin.TabularInline):
    """Historial de transiciones de estado. Inmutable — solo el sistema inserta aquí."""
    model = StatusHistory
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'notes', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ==========================================
# 2. REGISTROS PRINCIPALES
# ==========================================

@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'amortization_type', 'nominal_rate', 'min_term_months',
                    'max_term_months', 'max_quota_income_ratio', 'is_active')
    list_filter = ('amortization_type', 'is_active')
    search_fields = ('name',)
    search_help_text = "Busca por nombre del producto de crédito"


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'amount', 'term_months', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status', 'product')
    search_fields = ('opportunity__client__first_name', 'opportunity__client__last_name',
                     'opportunity__client__identification')
    search_help_text = "Busca por nombre o cédula del cliente"
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AmortizationScheduleInline, StatusHistoryInline]

# Nota: AmortizationSchedule y StatusHistory no se registran solos.
# Solo tienen sentido dentro de su solicitud padre (LoanApplication).
