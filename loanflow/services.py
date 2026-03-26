"""
Servicios de negocio del módulo LoanFlow.

Cada función aquí es lógica pura: recibe datos, ejecuta operaciones y retorna
un resultado o lanza una excepción. Sin magia, sin side effects ocultos.
Esto facilita el testing unitario y hace explícito el flujo de negocio.
"""
from datetime import date
from decimal import Decimal
from django.db import transaction
from .models import LoanApplication, LoanProduct, AmortizationSchedule, StatusHistory
from .amortization_engine import build_schedule


class LoanApplicationError(Exception):
    """Error de negocio al crear o procesar una solicitud de crédito."""
    pass


@transaction.atomic
def create_loan_application_from_opportunity(opportunity):
    """
    CU-206: Crea automáticamente una LoanApplication cuando una Opportunity
    avanza a la etapa de Pre-Aprobación.

    Flujo:
      1. Valida que no exista ya una solicitud para esta oportunidad.
      2. Verifica que la oportunidad tenga inmueble y perfil financiero.
      3. Busca el producto de crédito activo más económico en el que califica el cliente.
      4. Crea la LoanApplication en estado RADICADA.
      5. Registra la primera entrada en StatusHistory (auditoría).

    Args:
        opportunity: instancia de crm.Opportunity con stage == PRE_APPROVED.

    Returns:
        LoanApplication: la solicitud recién creada.

    Raises:
        LoanApplicationError: si faltan datos o no hay producto elegible.
    """
    # --- Guardia: idempotencia ---
    # Si la solicitud ya existe, no creamos una segunda. El servicio es seguro
    # de llamar más de una vez para la misma oportunidad.
    if hasattr(opportunity, 'loan_application'):
        return opportunity.loan_application

    # --- Validaciones de precondición ---
    if not opportunity.property_of_interest:
        raise LoanApplicationError(
            f"La oportunidad {opportunity.id} no tiene un inmueble asociado. "
            "No es posible crear la solicitud de crédito sin un valor de referencia."
        )

    if not hasattr(opportunity.client, 'financial_profile'):
        raise LoanApplicationError(
            f"El cliente {opportunity.client} no tiene perfil financiero registrado. "
            "El asesor debe completar el perfilamiento (CU-202) antes de pre-aprobar."
        )

    loan_amount = opportunity.property_of_interest.base_price
    monthly_income = opportunity.client.financial_profile.monthly_income

    # --- Selección del producto elegible ---
    # Criterio: producto activo donde el monto del inmueble cabe en el rango,
    # y la cuota estimada no supera el límite cuota/ingreso del producto.
    # De los elegibles, tomamos el de menor tasa nominal (mejor para el cliente).
    eligible_products = LoanProduct.objects.filter(
        is_active=True,
        min_amount__lte=loan_amount,
        max_amount__gte=loan_amount,
    ).order_by('nominal_rate')

    selected_product = None
    selected_term = None

    for product in eligible_products:
        # Calculamos la cuota aproximada con la tasa mensual y el plazo máximo
        # usando la fórmula de cuota fija (amortización francesa).
        # Esta es una estimación para la elegibilidad; la tabla exacta se genera aparte.
        monthly_rate = (product.nominal_rate / 100) / 12
        n = product.max_term_months

        if monthly_rate == 0:
            estimated_quota = loan_amount / n
        else:
            estimated_quota = loan_amount * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)

        quota_income_ratio = (estimated_quota / monthly_income) * 100

        if quota_income_ratio <= product.max_quota_income_ratio:
            selected_product = product
            selected_term = n
            break

    if not selected_product:
        raise LoanApplicationError(
            f"El cliente {opportunity.client} no califica para ningún producto activo "
            f"con el monto de {loan_amount}. Relación cuota/ingreso supera los límites configurados."
        )

    # --- Creación de la solicitud ---
    application = LoanApplication.objects.create(
        opportunity=opportunity,
        product=selected_product,
        amount=loan_amount,
        term_months=selected_term,
        status=LoanApplication.StatusChoices.RADICADA,
        credit_score=opportunity.dummy_bank_score,
    )

    # --- Registro inicial en auditoría ---
    # from_status vacío indica que es el estado inicial (no hubo transición previa).
    StatusHistory.objects.create(
        application=application,
        from_status='',
        to_status=LoanApplication.StatusChoices.RADICADA,
        changed_by=None,
        notes=(
            f"Solicitud creada automáticamente por pre-aprobación CRM (CU-206). "
            f"Producto asignado: {selected_product.name}. "
            f"Monto: {loan_amount}. Plazo: {selected_term} meses."
        ),
    )

    return application


@transaction.atomic
def approve_loan_and_generate_schedule(application, reviewed_by, disbursement_date=None):
    """
    Transiciona una LoanApplication a APROBADA y genera su tabla de amortización.

    Este es el momento en que el crédito se vuelve real: el analista aprueba,
    el motor calcula la tabla cuota a cuota y queda lista para el portal del cliente
    y para el worker nocturno de mora.

    Args:
        application:       instancia de LoanApplication en estado EN_ESTUDIO.
        reviewed_by:       CustomUser (analista) que aprueba.
        disbursement_date: date desde la que se calculan los vencimientos.
                           Si es None, se usa hoy.

    Returns:
        LoanApplication actualizada con status=APROBADA y su schedule generado.

    Raises:
        LoanApplicationError: si el estado actual no permite la aprobación.
    """
    VALID_PRIOR_STATES = {
        LoanApplication.StatusChoices.RADICADA,
        LoanApplication.StatusChoices.EN_ESTUDIO,
    }
    if application.status not in VALID_PRIOR_STATES:
        raise LoanApplicationError(
            f"No se puede aprobar una solicitud en estado '{application.get_status_display()}'. "
            f"Estados válidos previos: {', '.join(VALID_PRIOR_STATES)}."
        )

    if application.amortization_schedule.exists():
        raise LoanApplicationError(
            "Esta solicitud ya tiene una tabla de amortización generada. "
            "No se puede regenerar después de la aprobación."
        )

    start_date = disbursement_date or date.today()

    # Genera la tabla con el motor puro
    rows = build_schedule(
        principal=application.amount,
        annual_rate=application.product.nominal_rate,
        term_months=application.term_months,
        amortization_type=application.product.amortization_type,
        start_date=start_date,
    )

    # Persiste todas las cuotas en un solo bulk_create (eficiente para 180-360 filas)
    AmortizationSchedule.objects.bulk_create([
        AmortizationSchedule(
            application=application,
            period=row['period'],
            due_date=row['due_date'],
            principal=row['principal'],
            interest=row['interest'],
            balance=row['balance'],
            paid_at=None,
        )
        for row in rows
    ])

    from_status = application.status

    application.status = LoanApplication.StatusChoices.APROBADA
    application.reviewed_by = reviewed_by
    application.save(update_fields=['status', 'reviewed_by', 'updated_at'])

    StatusHistory.objects.create(
        application=application,
        from_status=from_status,
        to_status=LoanApplication.StatusChoices.APROBADA,
        changed_by=reviewed_by,
        notes=f"Crédito aprobado. Tabla de amortización generada ({len(rows)} cuotas). Primer vencimiento: {rows[0]['due_date']}.",
    )

    return application


@transaction.atomic
def reject_loan(application, reviewed_by, reason):
    """
    Transiciona una LoanApplication a RECHAZADA y libera el inmueble.

    Cuando se rechaza el crédito, el inmueble vuelve a AVAILABLE
    para que pueda ser ofrecido a otro comprador.

    Args:
        application: instancia de LoanApplication.
        reviewed_by: CustomUser (analista) que rechaza.
        reason:      str con el motivo del rechazo (requerido).

    Returns:
        LoanApplication actualizada con status=RECHAZADA.
    """
    VALID_PRIOR_STATES = {
        LoanApplication.StatusChoices.RADICADA,
        LoanApplication.StatusChoices.EN_ESTUDIO,
    }
    if application.status not in VALID_PRIOR_STATES:
        raise LoanApplicationError(
            f"No se puede rechazar una solicitud en estado '{application.get_status_display()}'."
        )

    if not reason or not reason.strip():
        raise LoanApplicationError("El motivo de rechazo es obligatorio.")

    from_status = application.status

    application.status = LoanApplication.StatusChoices.RECHAZADA
    application.reviewed_by = reviewed_by
    application.rejection_reason = reason
    application.save(update_fields=['status', 'reviewed_by', 'rejection_reason', 'updated_at'])

    StatusHistory.objects.create(
        application=application,
        from_status=from_status,
        to_status=LoanApplication.StatusChoices.RECHAZADA,
        changed_by=reviewed_by,
        notes=f"Rechazado. Motivo: {reason}",
    )

    # Liberar el inmueble: vuelve a Disponible para nuevas oportunidades
    property_obj = application.opportunity.property_of_interest
    if property_obj and property_obj.status == 'RESERVED':
        property_obj.status = 'AVAILABLE'
        property_obj.save(update_fields=['status'])

    return application
