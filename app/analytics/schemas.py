from datetime import date as date_type, datetime
from decimal import Decimal
from pydantic import BaseModel


class WalletBalanceSchema(BaseModel):
    wallet_id: int
    wallet_name: str
    wallet_currency: str
    balance: Decimal


class RecentTransactionSchema(BaseModel):
    transaction_id: int
    transaction_date: datetime
    operation_code: str
    description: str | None
    amount: Decimal
    currency: str


class DashboardSchema(BaseModel):
    wallets: list[WalletBalanceSchema]
    total_balance: Decimal
    currency: str
    recent_transactions: list[RecentTransactionSchema]
    current_month_income: Decimal
    current_month_expense: Decimal


class CategoryBreakdownSchema(BaseModel):
    category: str
    total: Decimal
    percentage: Decimal


class PeriodComparisonSchema(BaseModel):
    current_income: Decimal
    previous_income: Decimal
    income_change_percentage: Decimal
    current_expense: Decimal
    previous_expense: Decimal
    expense_change_percentage: Decimal
    currency: str


class CashflowWeekSchema(BaseModel):
    week_start: date_type
    week_end: date_type
    income: Decimal
    expense: Decimal


class SavingsRateSchema(BaseModel):
    income: Decimal
    expense: Decimal
    savings_rate_percentage: Decimal
    currency: str