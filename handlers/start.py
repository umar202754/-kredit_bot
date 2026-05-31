"""
handlers/start.py
/start va /help buyruqlari.
"""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from handlers.states import CHOOSE_TYPE
from utils.keyboards import main_menu_keyboard

log = logging.getLogger(__name__)

WELCOME_TEXT = (
    "✨ *Assalomu alaykum, {name}!* ✨\n\n"
    "💰 *Kredit Kalkulyator Botga xush kelibsiz!*\n\n"
    "Men sizga har qanday turdagi kreditni tez va aniq "
    "hisoblab beraman 🎯\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📊 *Kredit turlari:*\n"
    "🏠 Ipoteka  •  🚗 Avto  •  🛍️ Iste'mol\n"
    "💼 Biznes  •  🎓 Ta'lim  •  🌾 Qishloq xo'jaligi\n\n"
    "📐 *Hisoblash usullari:*\n"
    "• Annuitet — har oy teng to'lov\n"
    "• Differensiyal — kamayib boruvchi to'lov\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Qaysi kredit turini hisoblashni xohlaysiz? 👇"
)

HELP_TEXT = (
    "📖 *YORDAM*\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "*Annuitet usuli*\n"
    "Har oy bir xil to'lov. Bank uchun qulay, siz uchun taxminlash oson.\n\n"
    "*Differensiyal usul*\n"
    "Birinchi oylar ko'p, keyinchalik kamayadi. "
    "Jami to'lanadigan foiz kamroq bo'ladi.\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ Hisob-kitoblar *taxminiy* bo'lib, bank shartlari farq qilishi mumkin.\n\n"
    "/start — Yangi hisoblash boshlash"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Botni boshlash yoki qayta boshlash."""
    user = update.effective_user
    context.user_data.clear()
    log.info("Yangi suhbat: user_id=%s", user.id)

    await update.effective_message.reply_text(
        WELCOME_TEXT.format(name=user.first_name),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    return CHOOSE_TYPE


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(HELP_TEXT, parse_mode="Markdown")
