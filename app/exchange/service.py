from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.job_runner import run_with_logging
from app.exchange import rates_provider, repository
from app.models import ExchangeRate


async def fetch_and_save_rates(session: AsyncSession, base: str, symbols: list[str]) -> list[ExchangeRate]:
    data = await rates_provider.fetch_rates(base, symbols)
    if data is None:
        return []

    created_rates = []
    for row in data:
        rate = await repository.save_rate(
            session, base=row["base"], target=row["quote"], rate=Decimal(str(row["rate"]))
        )
        created_rates.append(rate)

    await session.commit()
    return created_rates


async def update_all_rates(session: AsyncSession) -> list[ExchangeRate]:
    all_rates = []
    for base in settings.supported_currencies:
        targets = [c for c in settings.SUPPORTED_CURRENCIES if c != base]
        rates = await fetch_and_save_rates(session, base=base, symbols=targets)
        all_rates.extend(rates)
    return all_rates


async def scheduled_update_rates() -> None:
    await run_with_logging("update_exchange_rates", update_all_rates)


async def get_latest_rate(session: AsyncSession, base: str, target: str) -> Decimal | None:
    return await repository.get_latest_rate(session, base, target)