import uuid
from django.conf import settings
from django.db import models
from .applications import LoanApplication


class StatusHistory(models.Model):
    """
    Registro inmutable de cada transición de estado de una solicitud de crédito.
    Es la auditoría completa de la máquina de estados: quién cambió qué, cuándo y por qué.
    Nunca se actualiza ni se borra — solo se inserta.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name="Solicitud de Crédito"
    )

    from_status = models.CharField(
        max_length=20,
        verbose_name="Estado Anterior",
        help_text="Estado desde el que se hizo la transición."
    )
    to_status = models.CharField(
        max_length=20,
        verbose_name="Estado Nuevo",
        help_text="Estado al que se transitó."
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='loan_status_changes',
        verbose_name="Cambiado por",
        help_text="Usuario que ejecutó la transición. Null si fue el sistema automáticamente."
    )

    notes = models.TextField(
        blank=True, null=True,
        verbose_name="Notas",
        help_text="Observaciones del analista o descripción automática del evento."
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Cambio")

    class Meta:
        verbose_name = "Historial de Estado"
        verbose_name_plural = "4. Historial de Estados"
        ordering = ['application', 'created_at']

    def __str__(self):
        actor = self.changed_by.username if self.changed_by else "Sistema"
        return f"{self.from_status} → {self.to_status} por {actor} ({self.created_at:%Y-%m-%d %H:%M})"
