from datetime import date
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.core.enums import CurrencyCode
from app.analytics import service
from app.analytics.schemas import (
    DashboardSchema, CategoryBreakdownSchema, PeriodComparisonSchema, CashflowWeekSchema, SavingsRateSchema,
)

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardSchema)
async def dashboard(
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_dashboard(session, current_user.id, currency.value)


@router.get("/analytics/expenses", response_model=list[CategoryBreakdownSchema])
async def expenses_by_category(
    date_from: date,
    date_to: date,
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_expenses_by_category(session, current_user.id, date_from, date_to, currency.value)


@router.get("/analytics/income", response_model=list[CategoryBreakdownSchema])
async def income_by_category(
    date_from: date,
    date_to: date,
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_income_by_category(session, current_user.id, date_from, date_to, currency.value)


@router.get("/analytics/summary", response_model=PeriodComparisonSchema)
async def summary(
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_summary(session, current_user.id, currency.value)


@router.get("/analytics/cashflow", response_model=list[CashflowWeekSchema])
async def cashflow(
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_cashflow(session, current_user.id, currency.value)


@router.get("/analytics/savings-rate", response_model=SavingsRateSchema)
async def savings_rate(
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_savings_rate(session, current_user.id, currency.value)