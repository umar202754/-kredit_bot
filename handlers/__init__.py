"""
handlers/__init__.py
Barcha handlerlarni Application'ga ro'yxatdan o'tkazish.
"""

from __future__ import annotations

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.conversation import (
    on_help_callback,
    on_rate_callback,
    on_amount_entered,
    on_rate_entered,
    on_restart,
    on_term_callback,
    on_term_entered,
    on_type_selected,
    on_unexpected_message,
)
from handlers.start import cmd_help, cmd_start
from handlers.states import CHOOSE_TYPE, ENTER_AMOUNT, ENTER_RATE, ENTER_TERM


def register_all_handlers(app: Application) -> None:
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
            CallbackQueryHandler(on_restart, pattern=r"^restart$"),
        ],
        states={
            CHOOSE_TYPE: [
                CallbackQueryHandler(on_type_selected, pattern=r"^type:"),
                CallbackQueryHandler(on_help_callback, pattern=r"^help$"),
            ],
            ENTER_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_amount_entered),
                CallbackQueryHandler(on_restart, pattern=r"^restart$"),
            ],
            ENTER_RATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_rate_entered),
                CallbackQueryHandler(on_rate_callback, pattern=r"^rate:"),
            ],
            ENTER_TERM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_term_entered),
                CallbackQueryHandler(on_term_callback, pattern=r"^term:"),
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CommandHandler("help", cmd_help),
            CallbackQueryHandler(on_restart, pattern=r"^restart$"),
        ],
        per_message=False,
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_unexpected_message)
    )
