"""
services/calculator.py
Kredit hisoblash mantig'i — sof funksiyalar, biznes logikasi yo'q.
"""

from __future__ import annotations

from models.credit import AnnuityResult, DifferentialResult, CalcResult


def calc_annuity(amount: float, annual_rate: float, months: int) -> AnnuityResult:
    """
    Annuitet usulida oylik to'lovni hisoblash.

    Formulasi:
        M = P * r * (1+r)^n / ((1+r)^n - 1)
    Bu yerda:
        P = asosiy qarz
        r = oylik foiz stavkasi (yillik / 12 / 100)
        n = oylar soni
    """
    r = annual_rate / 100 / 12

    if r == 0:
        monthly = amount / months
    else:
        factor = (1 + r) ** months
        monthly = amount * r * factor / (factor - 1)

    total = monthly * months
    interest = total - amount

    return AnnuityResult(
        monthly_payment=round(monthly, 2),
        total_payment=round(total, 2),
        total_interest=round(interest, 2),
    )


def calc_differential(amount: float, annual_rate: float, months: int) -> DifferentialResult:
    """
    Differensiyal usulida hisoblash.

    Har oylik to'lov:
        D_i = P/n + (P - P*(i-1)/n) * r
    """
    r = annual_rate / 100 / 12
    principal_per_month = amount / months

    first_payment = principal_per_month + amount * r
    last_payment = principal_per_month + principal_per_month * r

    total = sum(
        principal_per_month + (amount - principal_per_month * (i - 1)) * r
        for i in range(1, months + 1)
    )
    interest = total - amount

    return DifferentialResult(
        first_payment=round(first_payment, 2),
        last_payment=round(last_payment, 2),
        total_payment=round(total, 2),
        total_interest=round(interest, 2),
    )


def calculate(amount: float, annual_rate: float, months: int) -> CalcResult:
    """Ikkala usulni hisoblaydi va natijani birlashtiradi."""
    annuity = calc_annuity(amount, annual_rate, months)
    diff = calc_differential(amount, annual_rate, months)
    savings = round(annuity.total_interest - diff.total_interest, 2)

    return CalcResult(
        amount=amount,
        annual_rate=annual_rate,
        term_months=months,
        annuity=annuity,
        differential=diff,
        savings=savings,
    )
