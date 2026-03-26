import uuid
from django.db import models


class LoanProduct(models.Model):
    """
    Producto de crédito hipotecario configurable por el administrador.
    Define los parámetros base con los que opera el motor de amortización.
    Ej: "Crédito VIS 30 años" o "Leasing Habitacional No VIS".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, verbose_name="Nombre del Producto",
                            help_text="Ej: Crédito Hipotecario VIS, Leasing No VIS")

    class AmortizationTypeChoices(models.TextChoices):
        FRANCESA = 'FRANCESA', 'Francesa (cuota fija)'
        ALEMANA = 'ALEMANA', 'Alemana (capital fijo)'

    amortization_type = models.CharField(
        max_length=10,
        choices=AmortizationTypeChoices.choices,
        default=AmortizationTypeChoices.FRANCESA,
        verbose_name="Tipo de Amortización",
        help_text="Francesa: cuota total fija. Alemana: capital fijo, cuota decrece."
    )

    # Tasa nominal anual en porcentaje. Ej: 12.5 = 12.5% anual
    nominal_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name="Tasa Nominal Anual (%)",
        help_text="Ej: 12.50 para una tasa del 12.5% anual"
    )

    min_term_months = models.IntegerField(verbose_name="Plazo mínimo (meses)", help_text="Ej: 60 meses = 5 años")
    max_term_months = models.IntegerField(verbose_name="Plazo máximo (meses)", help_text="Ej: 360 meses = 30 años")

    min_amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Monto mínimo del crédito")
    max_amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Monto máximo del crédito")

    # Regla de elegibilidad: la cuota mensual no puede superar este % del ingreso del cliente.
    # El estándar del sector en Colombia es 30%.
    max_quota_income_ratio = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=30.00,
        verbose_name="Relación máxima cuota/ingreso (%)",
        help_text="Límite de la cuota sobre el ingreso. Ej: 30.00 = la cuota no puede superar el 30% del salario."
    )

    is_active = models.BooleanField(default=True, verbose_name="Activo",
                                    help_text="Solo los productos activos aparecen en el simulador.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto de Crédito"
        verbose_name_plural = "1. Productos de Crédito"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.nominal_rate}% anual - {self.amortization_type})"
