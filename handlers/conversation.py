"""
handlers/conversation.py
Kredit hisoblash suhbatining asosiy oqimi.
"""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config.settings import settings
from handlers.states import CHOOSE_TYPE, ENTER_AMOUNT, ENTER_RATE, ENTER_TERM
from models.credit import CREDIT_CATALOG, UserSession
from services.calculator import calculate
from utils.formatters import build_result_message
from utils.keyboards import (
    after_result_keyboard,
    back_keyboard,
    main_menu_keyboard,
    rate_hint_keyboard,
    term_hint_keyboard,
)

log = logging.getLogger(__name__)

SESSION_KEY = "session"


def _session(context: ContextTypes.DEFAULT_TYPE) -> UserSession:
    if SESSION_KEY not in context.user_data:
        context.user_data[SESSION_KEY] = UserSession()
    return context.user_data[SESSION_KEY]


# ── 1. Kredit turi tanlash ─────────────────────────────────────────────────

async def on_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    credit_key = query.data.split(":", 1)[1]
    product = CREDIT_CATALOG.get(credit_key)
    if not product:
        await query.answer("Noma'lum kredit turi.", show_alert=True)
        return CHOOSE_TYPE

    session = _session(context)
    session.reset()
    session.credit_key = credit_key
    log.debug("Kredit tanlandi: %s | user_id=%s", credit_key, query.from_user.id)

    text = (
        f"{product.icon} *{product.label}* tanlandi!\n\n"
        f"📝 {product.description}\n"
        f"💡 Odatdagi stavka: *{product.default_rate}% yillik*\n"
        f"📅 Odatdagi muddat: *{product.typical_term}*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 *Kredit summasini kiriting (so'mda):*\n\n"
        f"_Misol: `50000000` → 50 mln so'm_\n"
        f"_(Faqat raqam, vergul va bo'shliqsiz)_"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard())
    return ENTER_AMOUNT


# ── 2. Summa ───────────────────────────────────────────────────────────────

async def on_amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.text.strip().replace(" ", "").replace(",", "")
    try:
        amount = float(raw)
        _validate_amount(amount)
    except (ValueError, ArithmeticError) as exc:
        await update.message.reply_text(f"❌ {exc}\n\nIltimos, to'g'ri miqdor kiriting.")
        return ENTER_AMOUNT

    session = _session(context)
    session.amount = amount
    product = CREDIT_CATALOG[session.credit_key]

    text = (
        f"✅ Summa qabul qilindi.\n\n"
        f"📊 *Yillik foiz stavkasini kiriting (%):*\n\n"
        f"  Minimal: *{product.min_rate}%*\n"
        f"  Tavsiya:  *{product.default_rate}%*\n\n"
        f"_Misol: `18` yoki `18.5`_"
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=rate_hint_keyboard(product.default_rate, product.min_rate),
    )
    return ENTER_RATE


def _validate_amount(value: float) -> None:
    if value <= 0:
        raise ValueError("Summa musbat son bo'lishi kerak.")
    if value < settings.MIN_AMOUNT:
        raise ValueError(f"Minimal summa: {settings.MIN_AMOUNT:,.0f} so'm.")
    if value > settings.MAX_AMOUNT:
        raise ValueError(f"Maksimal summa: {settings.MAX_AMOUNT:,.0f} so'm.")


# ── 3. Foiz (matn) ─────────────────────────────────────────────────────────

async def on_rate_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.text.strip().replace(",", ".")
    try:
        rate = float(raw)
        _validate_rate(rate)
    except (ValueError, ArithmeticError) as exc:
        await update.message.reply_text(f"❌ {exc}\n\nMisol: `18` yoki `18.5`",
                                        parse_mode="Markdown")
        return ENTER_RATE

    return await _save_rate_and_ask_term(update.message.reply_text, context, rate)


async def on_rate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    rate = float(query.data.split(":", 1)[1])
    return await _save_rate_and_ask_term(query.message.reply_text, context, rate)


async def _save_rate_and_ask_term(reply_fn, context, rate: float) -> int:
    _session(context).annual_rate = rate

    text = (
        f"✅ Stavka: *{rate}% yillik*\n\n"
        f"📅 *Kredit muddatini kiriting (oyda):*\n\n"
        f"  6 oy → `6`  •  1 yil → `12`\n"
        f"  3 yil → `36`  •  5 yil → `60`\n\n"
        f"_(1 dan 360 gacha)_"
    )
    await reply_fn(text, parse_mode="Markdown", reply_markup=term_hint_keyboard())
    return ENTER_TERM


def _validate_rate(value: float) -> None:
    if value <= 0:
        raise ValueError("Foiz musbat son bo'lishi kerak.")
    if value < settings.MIN_RATE:
        raise ValueError(f"Minimal foiz: {settings.MIN_RATE}%.")
    if value > settings.MAX_RATE:
        raise ValueError(f"Maksimal foiz: {settings.MAX_RATE}%.")


# ── 4. Muddat (matn) ───────────────────────────────────────────────────────

async def on_term_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.text.strip()
    try:
        months = int(raw)
        _validate_term(months)
    except (ValueError, ArithmeticError) as exc:
        await update.message.reply_text(f"❌ {exc}\n\nMisol: `12` (1 yil) yoki `60` (5 yil)",
                                        parse_mode="Markdown")
        return ENTER_TERM

    session = _session(context)
    session.term_months = months
    return await _show_result(update.message.reply_text, session)


async def on_term_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    months = int(query.data.split(":", 1)[1])
    session = _session(context)
    session.term_months = months
    return await _show_result(query.message.reply_text, session)


def _validate_term(value: int) -> None:
    if value < settings.MIN_TERM_MONTHS:
        raise ValueError(f"Minimal muddat: {settings.MIN_TERM_MONTHS} oy.")
    if value > settings.MAX_TERM_MONTHS:
        raise ValueError(f"Maksimal muddat: {settings.MAX_TERM_MONTHS} oy.")


# ── 5. Natija ──────────────────────────────────────────────────────────────

async def _show_result(reply_fn, session: UserSession) -> int:
    result = calculate(session.amount, session.annual_rate, session.term_months)
    text = build_result_message(result, session.credit_key)
    await reply_fn(text, parse_mode="Markdown", reply_markup=after_result_keyboard())
    return ConversationHandler.END


# ── Tizimdan tashqari xabarlar ─────────────────────────────────────────────

async def on_restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """'Qayta hisoblash' va 'Menyu' tugmalari."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    await query.edit_message_text(
        "💰 Qaysi kredit turini hisoblashni xohlaysiz? 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    return CHOOSE_TYPE


async def on_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from handlers.start import HELP_TEXT
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(HELP_TEXT, parse_mode="Markdown")
    return CHOOSE_TYPE


async def on_unexpected_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "😊 Kredit hisoblash uchun /start ni bosing!",
    )
