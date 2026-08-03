from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExchangeRate


async def save_rate(session: AsyncSession, base: str, target: str, rate: Decimal) -> ExchangeRate:
    exchange_rate = ExchangeRate(
        base_currency=base,
        target_currency=target,
        rate=rate,
        fetched_at=datetime.now(timezone.utc),
    )
    session.add(exchange_rate)
    return exchange_rate


async def get_latest_rate(session: AsyncSession, base: str, target: str) -> Decimal | None:
    result = await session.execute(
        select(ExchangeRate.rate)
        .where(
            ExchangeRate.base_currency == base,
            ExchangeRate.target_currency == target,
        )
        .order_by(ExchangeRate.fetched_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()