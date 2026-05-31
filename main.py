"""
Kredit Kalkulyator Telegram Bot
================================
Entry point — botni shu fayldan ishga tushiring:
    python main.py
"""

import asyncio
import logging
import sys

from telegram.ext import Application

from config.settings import settings
from config.logging_config import setup_logging
from handlers import register_all_handlers


async def post_init(application: Application) -> None:
    """Bot ishga tushgandan keyin bajarish."""
    bot_info = await application.bot.get_me()
    logging.getLogger(__name__).info(
        "Bot ishga tushdi: @%s (id=%s)", bot_info.username, bot_info.id
    )


def build_application() -> Application:
    application = (
        Application.builder()
        .token(settings.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    register_all_handlers(application)
    return application


def main() -> None:
    setup_logging(settings.LOG_LEVEL)
    log = logging.getLogger(__name__)

    try:
        app = build_application()
        log.info("Polling boshlanmoqda...")
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        log.info("Bot to'xtatildi.")
        sys.exit(0)
    except Exception:
        log.critical("Bot ishga tushmadi", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
