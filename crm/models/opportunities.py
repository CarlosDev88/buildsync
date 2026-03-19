import uuid
from django.db import models
from django.conf import settings
from catalogue.models.properties import Property
from .clients import Client

class Opportunity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # --- LAS 3 LLAVES MAESTRAS ---
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='opportunities')
    property_of_interest = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')
    # Apunta al CustomUser que creamos al inicio (El Asesor)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_opportunities')
    
    # --- EL EMBUDO DE 8 PASOS las tipificaciones---
    class StageChoices(models.TextChoices):
        LEAD = '1_LEAD', '1. Captación (Lead)'
        QUALIFYING = '2_QUALIFYING', '2. Perfilamiento'
        RESERVATION = '3_RESERVATION', '3. Separación (Reserva)'
        DOCUMENTS = '4_DOCUMENTS', '4. Gestión de Documentos'
        PRE_APPROVED = '5_PRE_APPROVED', '5. Pre-Aprobación Bancaria' # Tu Motor Dummy
        PROMISE = '6_PROMISE', '6. Promesa de Compraventa'
        FINAL_APPROVAL = '7_FINAL_APPROVAL', '7. Aprobación y Escrituración'
        DELIVERED = '8_DELIVERED', '8. Entrega'
        # Estados de pérdida
        LOST = 'LOST', 'Perdido / Rechazado'
        
    stage = models.CharField(max_length=20, choices=StageChoices.choices, default=StageChoices.LEAD)
    
    # --- RESULTADOS DEL MOTOR DUMMY ---
    dummy_bank_score = models.IntegerField(null=True, blank=True, help_text="Puntaje generado por el motor de simulación (0-1000)")
    is_pre_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Se actualiza solo cada vez que cambias de etapa

    class Meta:
        verbose_name = "Oportunidad de Venta"
        verbose_name_plural = "Oportunidades de Vent"

    def __str__(self):
        prop_name = self.property_of_interest.property_name if self.property_of_interest else "Sin inmueble definido"
        return f"Opp: {self.client.first_name} -> {prop_name} ({self.get_stage_display()})"