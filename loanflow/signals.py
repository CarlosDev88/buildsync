"""
Signals de LoanFlow.

Escucha cambios en modelos de otros módulos para disparar lógica de integración.
El signal es solo el cable: detecta el evento y delega al service layer.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from crm.models.opportunities import Opportunity
from .services import create_loan_application_from_opportunity, LoanApplicationError

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Opportunity)
def on_opportunity_pre_approved(sender, instance, created, **kwargs):
    """
    CU-206: Cuando una Opportunity avanza a PRE_APPROVED, crea automáticamente
    la LoanApplication en el módulo LoanFlow.

    El guard `is_pre_approved` evita dispararse en saves que no sean el evento
    de pre-aprobación (ej: actualización de notas, cambio de asesor, etc.).
    """
    if not instance.is_pre_approved:
        return

    if instance.stage != Opportunity.StageChoices.PRE_APPROVED:
        return

    try:
        application = create_loan_application_from_opportunity(instance)
        logger.info(
            "LoanApplication %s creada desde Opportunity %s (CU-206).",
            application.id, instance.id
        )
    except LoanApplicationError as e:
        # Logueamos el error pero no lo propagamos para no romper el save del CRM.
        # En producción esto debería disparar una alerta al asesor.
        logger.error(
            "No se pudo crear LoanApplication para Opportunity %s: %s",
            instance.id, str(e)
        )
