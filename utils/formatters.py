"""
utils/formatters.py
Sonlar va matnlarni formatlash yordamchilari.
"""

from __future__ import annotations

from models.credit import CalcResult, CREDIT_CATALOG


def fmt_money(value: float) -> str:
    """1 234 567 so'm ko'rinishida formatlash."""
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.3g} mlrd so'm"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.4g} mln so'm"
    return f"{value:,.0f} so'm".replace(",", " ")


def fmt_term(months: int) -> str:
    """36 → '3 yil', 18 → '1 yil 6 oy', 5 → '5 oy'"""
    years, rem = divmod(months, 12)
    parts: list[str] = []
    if years:
        parts.append(f"{years} yil")
    if rem:
        parts.append(f"{rem} oy")
    return " ".join(parts) or "0 oy"


def build_result_message(result: CalcResult, credit_key: str) -> str:
    product = CREDIT_CATALOG.get(credit_key)
    header_icon = product.icon if product else "💰"
    header_name = product.label if product else "Kredit"

    ann = result.annuity
    dif = result.differential
    savings_line = (
        f"✅ Differensiyal usul bilan *{fmt_money(result.savings)}* tejaysiz!"
        if result.savings > 0
        else "ℹ️ Ikkala usul deyarli teng."
    )

    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *KREDIT HISOB-KITOBI*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{header_icon} *{header_name}*\n\n"
        f"📋 *Kirish ma'lumotlari:*\n"
        f"  💵 Summa:   *{fmt_money(result.amount)}*\n"
        f"  📊 Stavka:  *{result.annual_rate}% yillik*\n"
        f"  📅 Muddat:  *{result.term_months} oy ({fmt_term(result.term_months)})*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *1. ANNUITET* — teng to'lovlar\n"
        f"  💳 Oylik to'lov:  *{fmt_money(ann.monthly_payment)}*\n"
        f"  💰 Jami to'lov:   *{fmt_money(ann.total_payment)}*\n"
        f"  📈 Jami foiz:     *{fmt_money(ann.total_interest)}*\n\n"
        f"📌 *2. DIFFERENSIYAL* — kamayib boruvchi\n"
        f"  💳 1-oy to'lovi:  *{fmt_money(dif.first_payment)}*\n"
        f"  💳 Oxirgi to'lov: *{fmt_money(dif.last_payment)}*\n"
        f"  💰 Jami to'lov:   *{fmt_money(dif.total_payment)}*\n"
        f"  📈 Jami foiz:     *{fmt_money(dif.total_interest)}*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Xulosa:* {savings_line}\n\n"
        f"🏦 _Aniq shartlar uchun bankka murojaat qiling._"
    )
