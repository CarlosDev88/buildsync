import uuid
from django.db import models

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20)
    
    class LeadSourceChoices(models.TextChoices):
        FACEBOOK = 'FACEBOOK', 'Campaña Facebook'
        WALK_IN = 'WALK_IN', 'Sala de Ventas'
        REFERRAL = 'REFERRAL', 'Referido'
        WEBSITE = 'WEBSITE', 'Sitio Web'
        
    lead_source = models.CharField(max_length=20, choices=LeadSourceChoices.choices, default=LeadSourceChoices.WEBSITE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente Comercial"
        verbose_name_plural = "Clientes Comerciales"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class FinancialProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # OneToOne: Un cliente solo tiene un perfil financiero, y un perfil pertenece a un solo cliente
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='financial_profile')
    
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, help_text="Ingresos mensuales demostrables")
    initial_savings = models.DecimalField(max_digits=12, decimal_places=2, help_text="Ahorro disponible para la cuota inicial")
    has_debts = models.BooleanField(default=False, help_text="¿Tiene reportes o deudas altas?")

    def __str__(self):
        return f"Perfil Financiero - {self.client.first_name}"