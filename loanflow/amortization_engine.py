"""
Motor de amortización de PropSync.

Implementa las dos fórmulas estándar del sector hipotecario:
  - Francesa: cuota total FIJA cada mes. El capital crece y los intereses decrecen.
  - Alemana:  capital FIJO cada mes. La cuota total decrece con el tiempo.

Principios de diseño:
  - Sin librerías externas. Solo `decimal.Decimal` para precisión financiera.
  - Funciones puras: mismos inputs → mismo output siempre. Sin side effects.
  - La persistencia (guardar en AmortizationSchedule) vive en services.py,
    no aquí. Este módulo solo calcula.

Uso típico:
    from loanflow.amortization_engine import build_schedule
    from loanflow.models import LoanProduct

    rows = build_schedule(
        principal=Decimal('150_000_000'),
        annual_rate=Decimal('12.5'),
        term_months=180,
        amortization_type=LoanProduct.AmortizationTypeChoices.FRANCESA,
        start_date=date(2026, 4, 1),
    )
    # rows es una lista de dicts listos para crear AmortizationSchedule instances.
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta


# Precisión monetaria: 2 decimales, redondeo estándar bancario.
CENT = Decimal('0.01')


def _monthly_rate(annual_rate_percent: Decimal) -> Decimal:
    """Convierte tasa nominal anual (%) a tasa mensual decimal."""
    return (annual_rate_percent / Decimal('100')) / Decimal('12')


def _french_fixed_quota(principal: Decimal, monthly_rate: Decimal, n: int) -> Decimal:
    """
    Cuota fija mensual para amortización francesa.
    Fórmula: C = P * i / (1 - (1+i)^-n)
    Donde P=capital, i=tasa mensual, n=número de cuotas.
    """
    if monthly_rate == 0:
        return (principal / Decimal(n)).quantize(CENT, ROUND_HALF_UP)

    i = monthly_rate
    factor = (1 + i) ** n
    quota = principal * i * factor / (factor - 1)
    return quota.quantize(CENT, ROUND_HALF_UP)


def _build_french_schedule(
    principal: Decimal,
    monthly_rate: Decimal,
    term_months: int,
    start_date: date,
) -> list[dict]:
    """
    Genera la tabla de amortización francesa (cuota fija).
    El primer vencimiento es un mes después de start_date.
    """
    fixed_quota = _french_fixed_quota(principal, monthly_rate, term_months)
    rows = []
    balance = principal

    for period in range(1, term_months + 1):
        interest = (balance * monthly_rate).quantize(CENT, ROUND_HALF_UP)
        capital = (fixed_quota - interest).quantize(CENT, ROUND_HALF_UP)

        # Ajuste de último período: el saldo puede quedar con centavos por redondeo.
        if period == term_months:
            capital = balance
            interest = (fixed_quota - capital).quantize(CENT, ROUND_HALF_UP)
            if interest < 0:
                interest = Decimal('0.00')

        balance = (balance - capital).quantize(CENT, ROUND_HALF_UP)
        due_date = start_date + relativedelta(months=period)

        rows.append({
            'period': period,
            'due_date': due_date,
            'principal': capital,
            'interest': interest,
            'balance': balance,
            'paid_at': None,
        })

    return rows


def _build_german_schedule(
    principal: Decimal,
    monthly_rate: Decimal,
    term_months: int,
    start_date: date,
) -> list[dict]:
    """
    Genera la tabla de amortización alemana (capital fijo).
    El abono a capital es constante; los intereses decrecen cada mes.
    """
    fixed_capital = (principal / Decimal(term_months)).quantize(CENT, ROUND_HALF_UP)
    rows = []
    balance = principal

    for period in range(1, term_months + 1):
        interest = (balance * monthly_rate).quantize(CENT, ROUND_HALF_UP)

        # Último período: ajuste de centavos por redondeo acumulado.
        capital = fixed_capital if period < term_months else balance

        balance = (balance - capital).quantize(CENT, ROUND_HALF_UP)
        due_date = start_date + relativedelta(months=period)

        rows.append({
            'period': period,
            'due_date': due_date,
            'principal': capital,
            'interest': interest,
            'balance': balance,
            'paid_at': None,
        })

    return rows


def build_schedule(
    principal: Decimal,
    annual_rate: Decimal,
    term_months: int,
    amortization_type: str,
    start_date: date,
) -> list[dict]:
    """
    Punto de entrada público del motor.

    Args:
        principal:          Monto del crédito en pesos.
        annual_rate:        Tasa nominal anual en porcentaje. Ej: Decimal('12.5').
        term_months:        Número de cuotas mensuales. Ej: 180.
        amortization_type:  'FRANCESA' o 'ALEMANA' (LoanProduct.AmortizationTypeChoices).
        start_date:         Fecha de desembolso. La cuota 1 vence un mes después.

    Returns:
        Lista de dicts, uno por período, con las claves:
        {period, due_date, principal, interest, balance, paid_at}
        Listos para crear instancias de AmortizationSchedule.

    Raises:
        ValueError: si amortization_type no es reconocido.
    """
    if principal <= 0:
        raise ValueError("El monto del crédito debe ser mayor a cero.")
    if term_months <= 0:
        raise ValueError("El plazo debe ser mayor a cero.")
    if annual_rate < 0:
        raise ValueError("La tasa no puede ser negativa.")

    monthly_rate = _monthly_rate(annual_rate)

    if amortization_type == 'FRANCESA':
        return _build_french_schedule(principal, monthly_rate, term_months, start_date)
    elif amortization_type == 'ALEMANA':
        return _build_german_schedule(principal, monthly_rate, term_months, start_date)
    else:
        raise ValueError(
            f"Tipo de amortización '{amortization_type}' no reconocido. "
            "Use 'FRANCESA' o 'ALEMANA'."
        )


def summarize_schedule(rows: list[dict]) -> dict:
    """
    Calcula totales del crédito a partir de la tabla generada.
    Útil para el simulador: muestra cuánto paga en total y cuánto son intereses.
    """
    total_principal = sum(r['principal'] for r in rows)
    total_interest = sum(r['interest'] for r in rows)
    total_payment = total_principal + total_interest
    first_quota = rows[0]['principal'] + rows[0]['interest'] if rows else Decimal('0')
    last_quota = rows[-1]['principal'] + rows[-1]['interest'] if rows else Decimal('0')

    return {
        'term_months': len(rows),
        'total_principal': total_principal.quantize(CENT, ROUND_HALF_UP),
        'total_interest': total_interest.quantize(CENT, ROUND_HALF_UP),
        'total_payment': total_payment.quantize(CENT, ROUND_HALF_UP),
        'first_quota': first_quota.quantize(CENT, ROUND_HALF_UP),
        'last_quota': last_quota.quantize(CENT, ROUND_HALF_UP),
    }
