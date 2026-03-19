import uuid
from django.db import models
from .opportunities import Opportunity

class PaymentPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.OneToOneField(Opportunity, on_delete=models.CASCADE, related_name='payment_plan')
    
    # PASO 3: Separación
    reservation_fee = models.DecimalField(max_digits=12, decimal_places=2, help_text="Dinero dado para separar el inmueble")
    reservation_date = models.DateField(null=True, blank=True)
    
    # PASO 6: Promesa y Cuota Inicial
    down_payment_total = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total de la cuota inicial (ej: 30%)")
    monthly_installments = models.IntegerField(help_text="Número de meses para pagar la cuota inicial", default=1)
    monthly_fee = models.DecimalField(max_digits=12, decimal_places=2, help_text="Valor de la cuota mensual")
    
    is_signed = models.BooleanField(default=False, help_text="¿Ya firmaron la Promesa de Compraventa?")

    class Meta:
        verbose_name = "Plan de Pagos"
        verbose_name_plural = "Planes de Pagos"

    def __str__(self):
        return f"Plan de Pagos - Opp: {self.opportunity.id}"