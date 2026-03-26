import uuid
from django.db import models
from .opportunities import Opportunity

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='documents')
    
    class DocumentTypeChoices(models.TextChoices):
        ID_CARD = 'ID_CARD', 'Cédula de Ciudadanía'
        BANK_STATEMENT = 'BANK_STATEMENT', 'Extractos Bancarios (3 meses)'
        PAY_STUB = 'PAY_STUB', 'Desprendibles de Nómina'
        TAX_RETURN = 'TAX_RETURN', 'Declaración de Renta'
        PROMISE_CONTRACT = 'PROMISE_CONTRACT', 'Promesa de Compraventa Firmada'
        
    document_type = models.CharField(max_length=30, choices=DocumentTypeChoices.choices)
    
    # La key (ruta) del objeto en S3. Ej: "documents/clients/uuid/cedula.pdf"
    # Se usa para generar URLs presignadas en cada solicitud, no se guarda la URL que expira.
    s3_key = models.CharField(max_length=500, help_text="Ruta del objeto en AWS S3. Ej: documents/clients/{uuid}/cedula.pdf", blank=True, null=True)
    
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente de revisión'
        APPROVED = 'APPROVED', 'Aprobado'
        REJECTED = 'REJECTED', 'Rechazado / Ilegible'

    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.opportunity.client.first_name}"