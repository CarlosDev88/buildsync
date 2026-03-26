import uuid
from django.db import models
from .applications import LoanApplication


class AmortizationSchedule(models.Model):
    """
    Tabla de amortización generada por el motor de crédito al aprobar una solicitud.
    Cada fila es una cuota mensual: muestra cuánto va a capital, cuánto a intereses
    y cuál es el saldo pendiente. Es la fuente de verdad para el portal del comprador
    y para el worker nocturno de mora.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='amortization_schedule',
        verbose_name="Solicitud de Crédito"
    )

    # Número de cuota (1, 2, 3 ... n)
    period = models.PositiveIntegerField(verbose_name="Número de Cuota")

    due_date = models.DateField(verbose_name="Fecha de Vencimiento")

    # Descomposición de la cuota: capital + intereses = cuota total
    principal = models.DecimalField(
        max_digits=14, decimal_places=2,
        verbose_name="Abono a Capital",
        help_text="Porción de la cuota que reduce el saldo del crédito."
    )
    interest = models.DecimalField(
        max_digits=14, decimal_places=2,
        verbose_name="Intereses",
        help_text="Porción de la cuota que corresponde a intereses del período."
    )

    # Saldo restante después de pagar esta cuota
    balance = models.DecimalField(
        max_digits=14, decimal_places=2,
        verbose_name="Saldo Pendiente",
        help_text="Capital pendiente de pago después de esta cuota."
    )

    # Cuándo pagó el cliente. Null = aún no ha pagado.
    # El worker nocturno de mora consulta esta columna para detectar vencidos.
    paid_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Fecha de Pago",
        help_text="Se registra cuando el cliente paga. Null = pendiente de pago."
    )

    class Meta:
        verbose_name = "Cuota de Amortización"
        verbose_name_plural = "3. Tabla de Amortización"
        ordering = ['application', 'period']
        # Garantiza que no haya dos cuotas con el mismo número para la misma solicitud
        unique_together = [('application', 'period')]

    def __str__(self):
        status = "Pagada" if self.paid_at else "Pendiente"
        return f"Cuota {self.period} — {self.due_date} — Saldo: {self.balance} [{status}]"

    @property
    def total_payment(self):
        """Cuota total = capital + intereses."""
        return self.principal + self.interest
