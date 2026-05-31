"""
config/settings.py
Bot sozlamalari — .env fayldan yoki muhit o'zgaruvchilaridan o'qiladi.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: _require_env("BOT_TOKEN"))
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Kredit cheklovlari
    MIN_AMOUNT: float = 100_000          # 100 000 so'm
    MAX_AMOUNT: float = 10_000_000_000   # 10 milliard so'm
    MIN_RATE: float = 1.0                # 1%
    MAX_RATE: float = 100.0              # 100%
    MIN_TERM_MONTHS: int = 1
    MAX_TERM_MONTHS: int = 360           # 30 yil


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"'{key}' muhit o'zgaruvchisi topilmadi. "
            f".env faylga qo'shing: {key}=your_token_here"
        )
    return value


settings = Settings()
