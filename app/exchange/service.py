from datetime import datetime, timezone
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_factory
from app.models import ExchangeRate


async def fetch_and_save_rates(session: AsyncSession, base: str, symbols: list[str]) -> list[ExchangeRate]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.frankfurter.dev/v2/rates",
                params={"base": base, "quotes": ",".join(symbols)},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()  # это list, а не dict!

            created_rates = []
            for row in data:
                exchange_rate = ExchangeRate(
                    base_currency=row["base"],
                    target_currency=row["quote"],
                    rate=Decimal(str(row["rate"])),
                    fetched_at=datetime.now(timezone.utc),
                )
                session.add(exchange_rate)
                created_rates.append(exchange_rate)

            await session.commit()
            return created_rates

        except httpx.TimeoutException:
            return []
        except httpx.HTTPStatusError:
            return []
        except httpx.RequestError:
            return []

async def update_all_rates(session: AsyncSession) -> list[ExchangeRate]:
    all_rates = []
    for base in settings.SUPPORTED_CURRENCIES:
        targets = [c for c in settings.SUPPORTED_CURRENCIES if c != base]
        rates = await fetch_and_save_rates(session, base=base, symbols=targets)
        all_rates.extend(rates)
    return all_rates


async def scheduled_update_rates():
    async with async_session_factory() as session:
        await update_all_rates(session)


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