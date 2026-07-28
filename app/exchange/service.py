from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable, Awaitable

import httpx
from sqlalchemy import select
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory

from app.core.config import settings
from app.core.enums import JobStatus
from app.models import ExchangeRate
from app.models.scheduled_job_log import ScheduledJobLog


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
    await run_with_logging("update_exchange_rates", update_all_rates)


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


async def run_with_logging(job_name: str, job_func: Callable[[AsyncSession], Awaitable[Any]]) -> None:
    async with async_session_factory() as session:
        log_entry = ScheduledJobLog(job_name=job_name, status=JobStatus.RUNNING, started_at=datetime.now(timezone.utc))
        session.add(log_entry)
        await session.commit()
        await session.refresh(log_entry)

    async with async_session_factory() as session:
        try:
            result = await job_func(session)
            log_entry.status = JobStatus.SUCCESS
            if isinstance(result, list):
                log_entry.details = f"processed {len(result)} items"
            else:
                log_entry.details = str(result) if result else None
        except Exception as e:
            log_entry.status = JobStatus.FAILED
            log_entry.error_message = str(e)
        finally:
            log_entry.finished_at = datetime.now(timezone.utc)
            await session.merge(log_entry)
            await session.commit()

