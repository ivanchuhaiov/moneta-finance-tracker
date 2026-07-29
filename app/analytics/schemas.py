from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class SummarySchema(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net: Decimal
    currency: str
    has_missing_data: bool
    missing_count: int


class CategoryBreakdownSchema(BaseModel):
    category: str
    total: Decimal
    type: TransactionType
    has_missing_data: bool
    missing_count: int


class WalletSummarySchema(BaseModel):
    wallet_id: int
    wallet_name: str
    wallet_currency: str
    total_in_wallet_currency: Decimal
    total_in_target_currency: Decimal
    has_missing_data: bool
    missing_count: int


class TrendPointSchema(BaseModel):
    period: str
    income: Decimal
    expense: Decimal
    net: Decimal