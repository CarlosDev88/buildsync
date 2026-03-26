"""
Servicios de negocio del módulo CRM.

Contiene la lógica de dominio del proceso comercial: perfilamiento financiero,
pre-aprobación dummy y transiciones del embudo de ventas.
"""
from decimal import Decimal
from django.db import transaction
from .models.opportunities import Opportunity
from .models.clients import Client
from catalogue.models.properties import Property


class PreApprovalError(Exception):
    """Error de negocio durante el proceso de pre-aprobación."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Motor dummy de score crediticio
# ─────────────────────────────────────────────────────────────────────────────

def calculate_dummy_score(financial_profile, property_price: Decimal) -> int:
    """
    Calcula un score crediticio simulado (0-1000) basado en el perfil financiero.

    Criterios ponderados (sin bureaus externos, solo datos internos):
      - Relación cuota estimada / ingreso mensual  → peso más alto
      - Ahorro inicial vs. precio del inmueble     → capacidad de cuota inicial
      - Presencia de deudas reportadas             → penalización

    Este score es 'dummy' por diseño: en producción se reemplaza por
    la integración con DataCrédito o Transunion. La interfaz del servicio
    queda igual, solo cambia la implementación interna.

    Returns:
        int entre 0 y 1000.
    """
    score = Decimal('1000')

    monthly_income = financial_profile.monthly_income
    initial_savings = financial_profile.initial_savings
    has_debts = financial_profile.has_debts

    if monthly_income <= 0:
        return 0

    # ── Factor 1: Relación cuota estimada / ingreso (peso: 50%) ──────────────
    # Estimamos la cuota a 180 meses al 12% anual (referencia de mercado).
    ref_rate = Decimal('0.01')  # 1% mensual ≈ 12% anual
    n = 180
    estimated_quota = property_price * (ref_rate * (1 + ref_rate) ** n) / ((1 + ref_rate) ** n - 1)
    ratio = estimated_quota / monthly_income

    if ratio > Decimal('0.40'):
        score -= Decimal('500')      # Claramente fuera de rango
    elif ratio > Decimal('0.30'):
        score -= Decimal('300')      # En el límite
    elif ratio > Decimal('0.25'):
        score -= Decimal('150')      # Ajustado pero viable
    elif ratio > Decimal('0.20'):
        score -= Decimal('50')       # Cómodo
    # < 20% → sin penalización, cliente ideal

    # ── Factor 2: Ahorro inicial vs. precio (peso: 30%) ───────────────────────
    # Estándar: cuota inicial mínima del 20-30% del valor del inmueble.
    savings_ratio = initial_savings / property_price if property_price > 0 else Decimal('0')

    if savings_ratio < Decimal('0.10'):
        score -= Decimal('300')      # Menos del 10%: muy bajo
    elif savings_ratio < Decimal('0.20'):
        score -= Decimal('150')      # Entre 10-20%: bajo
    elif savings_ratio < Decimal('0.30'):
        score -= Decimal('50')       # Entre 20-30%: aceptable
    # >= 30% → sin penalización

    # ── Factor 3: Deudas reportadas (peso: 20%) ───────────────────────────────
    if has_debts:
        score -= Decimal('200')

    # Clamp: el score no puede ser negativo
    final_score = max(int(score), 0)
    return final_score


@transaction.atomic
def run_pre_approval(opportunity, min_score: int = 600) -> dict:
    """
    CU-205: Motor de pre-aprobación dummy.

    Evalúa el perfil financiero del cliente contra el inmueble de interés,
    calcula el score, decide si aprueba o rechaza, y actualiza la Opportunity.

    Si aprueba:
      - Marca la Opportunity como is_pre_approved=True y avanza a PRE_APPROVED.
      - Cambia el estado del inmueble a RESERVED.
      - El signal post_save de Opportunity dispara CU-206 (crea LoanApplication).

    Si rechaza:
      - Registra el score y mantiene la oportunidad en DOCUMENTS (o LOST si se decide así).

    Args:
        opportunity: instancia de Opportunity. Debe tener cliente con perfil
                     financiero e inmueble asociado.
        min_score:   umbral mínimo de aprobación (default 600/1000).

    Returns:
        dict con {approved: bool, score: int, reason: str}

    Raises:
        PreApprovalError: si faltan datos requeridos.
    """
    # ── Validaciones ─────────────────────────────────────────────────────────
    if not opportunity.property_of_interest:
        raise PreApprovalError(
            "La oportunidad no tiene un inmueble asociado. "
            "El asesor debe seleccionar el inmueble antes de pre-aprobar."
        )

    if not hasattr(opportunity.client, 'financial_profile'):
        raise PreApprovalError(
            "El cliente no tiene perfil financiero. "
            "Complete el perfilamiento (CU-202) antes de ejecutar la pre-aprobación."
        )

    if opportunity.is_pre_approved:
        raise PreApprovalError(
            "Esta oportunidad ya fue pre-aprobada. "
            "No se puede ejecutar el motor dos veces."
        )

    prop = opportunity.property_of_interest
    profile = opportunity.client.financial_profile
    score = calculate_dummy_score(profile, prop.base_price)

    # Guardamos el score siempre, independientemente del resultado
    opportunity.dummy_bank_score = score

    if score >= min_score:
        # ── APROBADO ─────────────────────────────────────────────────────────
        opportunity.is_pre_approved = True
        opportunity.stage = Opportunity.StageChoices.PRE_APPROVED
        opportunity.save(update_fields=['dummy_bank_score', 'is_pre_approved', 'stage', 'updated_at'])
        # El signal post_save detecta is_pre_approved=True y crea la LoanApplication (CU-206)

        prop.status = Property.StatusChoices.RESERVED
        prop.save(update_fields=['status'])

        reason = (
            f"Score {score}/1000 supera el umbral mínimo de {min_score}. "
            "Inmueble reservado y solicitud de crédito creada automáticamente."
        )
        return {'approved': True, 'score': score, 'reason': reason}

    else:
        # ── RECHAZADO ────────────────────────────────────────────────────────
        opportunity.save(update_fields=['dummy_bank_score', 'updated_at'])

        reason = (
            f"Score {score}/1000 no alcanza el umbral mínimo de {min_score}. "
            "El cliente no califica con el perfil financiero actual."
        )
        return {'approved': False, 'score': score, 'reason': reason}
