from decimal import Decimal
from pydantic import BaseModel


class SummarySchema(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net: Decimal
    currency: str


class CategoryBreakdownSchema(BaseModel):
    category: str
    total: Decimal
    type: str  # "income" или "expense"


class WalletSummarySchema(BaseModel):
    wallet_id: int
    wallet_name: str
    wallet_currency: str
    total_in_wallet_currency: Decimal
    total_in_target_currency: Decimal


class TrendPointSchema(BaseModel):
    period: str  # например "2026-07"
    income: Decimal
    expense: Decimal
    net: Decimal