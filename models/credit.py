"""
models/credit.py
Ma'lumot modellari (dataclass-lar).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class CreditType(str, Enum):
    IPOTEKA  = "ipoteka"
    AUTO     = "auto"
    ISTEМOL  = "istemol"
    BIZNES   = "biznes"
    TALIM    = "talim"
    QISHLOQ  = "qishloq"


@dataclass(frozen=True)
class CreditProduct:
    key: CreditType
    label: str          # Menyu tugmasi
    icon: str
    description: str
    default_rate: float # %
    min_rate: float     # %
    typical_term: str   # foydalanuvchiga ko'rsatish uchun

    # Barcha mahsulotlar ro'yxati
    CATALOG: ClassVar[list[CreditProduct]]


CreditProduct.CATALOG = [
    CreditProduct(
        key=CreditType.IPOTEKA,
        label="Ipoteka krediti",
        icon="🏠",
        description="Uy-joy sotib olish uchun",
        default_rate=16.0,
        min_rate=14.0,
        typical_term="10–30 yil",
    ),
    CreditProduct(
        key=CreditType.AUTO,
        label="Avto kredit",
        icon="🚗",
        description="Avtomobil sotib olish uchun",
        default_rate=20.0,
        min_rate=18.0,
        typical_term="1–5 yil",
    ),
    CreditProduct(
        key=CreditType.ISTEМOL,
        label="Iste'mol krediti",
        icon="🛍️",
        description="Shaxsiy ehtiyojlar uchun",
        default_rate=24.0,
        min_rate=20.0,
        typical_term="6 oy – 3 yil",
    ),
    CreditProduct(
        key=CreditType.BIZNES,
        label="Biznes krediti",
        icon="💼",
        description="Tadbirkorlik uchun",
        default_rate=24.0,
        min_rate=22.0,
        typical_term="1–7 yil",
    ),
    CreditProduct(
        key=CreditType.TALIM,
        label="Ta'lim krediti",
        icon="🎓",
        description="O'qish uchun",
        default_rate=14.0,
        min_rate=12.0,
        typical_term="1–5 yil",
    ),
    CreditProduct(
        key=CreditType.QISHLOQ,
        label="Qishloq xo'jaligi",
        icon="🌾",
        description="Fermerlar uchun",
        default_rate=12.0,
        min_rate=10.0,
        typical_term="1–10 yil",
    ),
]

# Tez qidirish uchun lug'at
CREDIT_CATALOG: dict[str, CreditProduct] = {p.key.value: p for p in CreditProduct.CATALOG}


@dataclass
class UserSession:
    """Foydalanuvchi suhbati davomida saqlanadigan ma'lumotlar."""
    credit_key: str | None = None
    amount: float | None = None
    annual_rate: float | None = None
    term_months: int | None = None

    def is_complete(self) -> bool:
        return all([self.credit_key, self.amount, self.annual_rate, self.term_months])

    def reset(self) -> None:
        self.credit_key = None
        self.amount = None
        self.annual_rate = None
        self.term_months = None


@dataclass(frozen=True)
class AnnuityResult:
    monthly_payment: float
    total_payment: float
    total_interest: float


@dataclass(frozen=True)
class DifferentialResult:
    first_payment: float
    last_payment: float
    total_payment: float
    total_interest: float


@dataclass(frozen=True)
class CalcResult:
    amount: float
    annual_rate: float
    term_months: int
    annuity: AnnuityResult
    differential: DifferentialResult
    savings: float          # differensiyal bilan tejash
