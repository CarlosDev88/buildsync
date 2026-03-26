import uuid
from django.conf import settings
from django.db import models
from crm.models.opportunities import Opportunity
from .products import LoanProduct


class LoanApplication(models.Model):
    """
    Solicitud de crédito hipotecario. Se crea automáticamente desde el CRM
    cuando una Opportunity avanza a pre-aprobación (CU-206).
    Es el nexo central entre el módulo CRM y el módulo LoanFlow.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Nexo con CRM: una oportunidad puede generar una sola solicitud de crédito.
    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.PROTECT,
        related_name='loan_application',
        verbose_name="Oportunidad de Venta",
        help_text="La oportunidad del CRM que originó esta solicitud."
    )

    product = models.ForeignKey(
        LoanProduct,
        on_delete=models.PROTECT,
        related_name='applications',
        verbose_name="Producto de Crédito"
    )

    # Monto y plazo acordados para esta solicitud específica
    amount = models.DecimalField(
        max_digits=14, decimal_places=2,
        verbose_name="Monto Solicitado",
        help_text="Valor del crédito en pesos. Generalmente = precio_base - cuota_inicial."
    )
    term_months = models.IntegerField(
        verbose_name="Plazo (meses)",
        help_text="Número de meses para pagar. Ej: 180 = 15 años."
    )

    # --- MÁQUINA DE ESTADOS ---
    # Cada transición queda auditada en StatusHistory.
    class StatusChoices(models.TextChoices):
        RADICADA = 'RADICADA', 'Radicada'
        EN_ESTUDIO = 'EN_ESTUDIO', 'En Estudio'
        APROBADA = 'APROBADA', 'Aprobada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        DESEMBOLSADA = 'DESEMBOLSADA', 'Desembolsada'

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.RADICADA,
        verbose_name="Estado de la Solicitud"
    )

    # Score crediticio dummy (0-1000). En producción vendría de una central de riesgo.
    credit_score = models.IntegerField(
        null=True, blank=True,
        verbose_name="Score Crediticio",
        help_text="Score calculado por el motor dummy (0-1000)."
    )

    # Analista que aprobó o rechazó la solicitud
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_applications',
        verbose_name="Revisado por",
        help_text="Analista de crédito que tomó la decisión final."
    )

    rejection_reason = models.TextField(
        blank=True, null=True,
        verbose_name="Motivo de Rechazo",
        help_text="Obligatorio si el estado es RECHAZADA."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitud de Crédito"
        verbose_name_plural = "2. Solicitudes de Crédito"
        ordering = ['-created_at']

    def __str__(self):
        client = self.opportunity.client
        return f"Solicitud #{str(self.id)[:8]} — {client.first_name} {client.last_name} [{self.get_status_display()}]"
