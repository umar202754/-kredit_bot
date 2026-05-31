"""
utils/keyboards.py
Barcha InlineKeyboardMarkup'lar bir joyda.
"""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from models.credit import CreditProduct


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"{p.icon} {p.label}", callback_data=f"type:{p.key.value}")]
        for p in CreditProduct.CATALOG
    ]
    rows.append([InlineKeyboardButton("❓ Yordam", callback_data="help")])
    return InlineKeyboardMarkup(rows)


def rate_hint_keyboard(default_rate: float, min_rate: float) -> InlineKeyboardMarkup:
    rates = sorted({min_rate, default_rate, round(default_rate + 2, 1)})
    buttons = [
        InlineKeyboardButton(f"{r}%", callback_data=f"rate:{r}")
        for r in rates
    ]
    return InlineKeyboardMarkup([buttons])


def term_hint_keyboard() -> InlineKeyboardMarkup:
    options = [
        ("6 oy", 6), ("12 oy", 12), ("24 oy", 24),
        ("36 oy", 36), ("60 oy", 60), ("120 oy", 120),
    ]
    rows = [
        [InlineKeyboardButton(label, callback_data=f"term:{months}")]
        for label, months in options
    ]
    return InlineKeyboardMarkup(rows)


def after_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Qayta hisoblash", callback_data="restart"),
            InlineKeyboardButton("🏠 Menyu", callback_data="restart"),
        ]
    ])


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="restart")]
    ])
