from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, model_validator

from app.core.enums import CurrencyCode


class ReportGenerateRequest(BaseModel):
    date_from: date
    date_to: date
    target_currency: CurrencyCode = CurrencyCode.EUR
    include_summary: bool = True
    include_by_category: bool = True
    include_by_wallet: bool = True
    include_transactions: bool = False

    @model_validator(mode="after")
    def validate_report_request(self) -> "ReportGenerateRequest":
        if self.date_from > self.date_to:
            raise ValueError("date_from must be before or equal to date_to")

        if not any([
            self.include_summary,
            self.include_by_category,
            self.include_by_wallet,
            self.include_transactions,
        ]):
            raise ValueError("At least one report section must be included")
        return self

class ReportSummarySchema(BaseModel):
    date_from: date
    date_to: date
    total_income: Decimal
    total_expense: Decimal
    net: Decimal
    currency: str


class ReportCategoryItemSchema(BaseModel):
    category: str
    total: Decimal
    percentage: Decimal


class ReportWalletItemSchema(BaseModel):
    wallet_id: int
    wallet_name: str
    balance: Decimal
    currency: str


class ReportTransactionItemSchema(BaseModel):
    transaction_id: int
    transaction_date: datetime
    operation_code: str
    description: str | None
    amount: Decimal
    currency: str


class ReportData(BaseModel):
    date_from: date
    date_to: date
    target_currency: str
    summary: ReportSummarySchema | None = None
    by_category: list[ReportCategoryItemSchema] | None = None
    by_wallet: list[ReportWalletItemSchema] | None = None
    transactions: list[ReportTransactionItemSchema] | None = None