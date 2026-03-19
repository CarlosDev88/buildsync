import uuid
from django.db import models
from django.conf import settings
from .opportunities import Opportunity

class InteractionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class InteractionTypeChoices(models.TextChoices):
        CALL = 'CALL', 'Llamada'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        MEETING = 'MEETING', 'Reunión Presencial / Sala de Ventas'
        SYSTEM_NOTE = 'SYSTEM_NOTE', 'Nota del Sistema' # Ej: "Motor Dummy aprobó el crédito"
        
    interaction_type = models.CharField(max_length=20, choices=InteractionTypeChoices.choices, default=InteractionTypeChoices.WHATSAPP)
    notes = models.TextField(help_text="Resumen de lo que se habló con el cliente")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date'] # Siempre muestra el más reciente primero
        verbose_name = "Registro de Interacción"
        verbose_name_plural = "Registros de Interacciones"  

    def __str__(self):
        return f"{self.get_interaction_type_display()} - {self.date.strftime('%Y-%m-%d')} ({self.opportunity.client.first_name})"