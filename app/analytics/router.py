from fastapi import APIRouter, Depends
from datetime import date

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.core.enums import CurrencyCode
from app.analytics import service
from app.analytics.schemas import SummarySchema, CategoryBreakdownSchema, WalletSummarySchema, TrendPointSchema

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=SummarySchema)
async def summary(
    period: str = "month",
    target_date: date = date.today(),
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_summary(session, current_user.id, period, target_date, currency.value)


@router.get("/by-category", response_model=list[CategoryBreakdownSchema])
async def by_category(
    period: str = "month",
    target_date: date = date.today(),
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_by_category(session, current_user.id, period, target_date, currency.value)


@router.get("/by-wallet", response_model=list[WalletSummarySchema])
async def by_wallet(
    period: str = "month",
    target_date: date = date.today(),
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_by_wallet(session, current_user.id, period, target_date, currency.value)


@router.get("/trend", response_model=list[TrendPointSchema])
async def trend(
    months: int = 6,
    currency: CurrencyCode = CurrencyCode.EUR,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.get_trend(session, current_user.id, months, currency.value)