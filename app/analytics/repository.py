from datetime import datetime

from sqlalchemy import select, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TransactionHistory, CreditOperation, DebitOperation, Wallet, ExchangeRate
from app.analytics.conversion import RateEntry, RatesIndex


async def get_transactions_for_period(
    session: AsyncSession, user_id: int, date_from: datetime, date_to: datetime
) -> list[TransactionHistory]:
    stmt = (
        select(TransactionHistory)
        .options(
            selectinload(TransactionHistory.from_wallet).selectinload(Wallet.currency),
            selectinload(TransactionHistory.to_wallet).selectinload(Wallet.currency),
            selectinload(TransactionHistory.credit_operation).selectinload(CreditOperation.credit_type),
            selectinload(TransactionHistory.debit_operation).selectinload(DebitOperation.debit_type),
        )
        .where(
            TransactionHistory.user_id == user_id,
            TransactionHistory.transaction_date >= date_from,
            TransactionHistory.transaction_date <= date_to,
        )
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_wallets_for_analytics(session: AsyncSession, user_id: int) -> list[Wallet]:
    stmt = (
        select(Wallet)
        .options(selectinload(Wallet.currency))
        .where(Wallet.user_id == user_id, Wallet.is_include_in_balance.is_(True))
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_rates_batch(
    session: AsyncSession, pairs: set[tuple[str, str]], date_to: datetime
) -> RatesIndex:
    if not pairs:
        return {}

    conditions = [
        (ExchangeRate.base_currency == base) & (ExchangeRate.target_currency == target)
        for base, target in pairs
    ]

    stmt = (
        select(ExchangeRate.base_currency, ExchangeRate.target_currency, ExchangeRate.rate, ExchangeRate.fetched_at)
        .where(or_(*conditions), ExchangeRate.fetched_at <= date_to)
        .order_by(ExchangeRate.fetched_at.asc())
    )

    result = await session.execute(stmt)
    rows = result.all()

    rates_index: RatesIndex = {}
    for row in rows:
        key = (row.base_currency, row.target_currency)
        rates_index.setdefault(key, []).append(RateEntry(fetched_at=row.fetched_at, rate=row.rate))

    return rates_index

async def get_recent_transactions(
    session: AsyncSession, user_id: int, limit: int
) -> list[TransactionHistory]:
    stmt = (
        select(TransactionHistory)
        .options(
            selectinload(TransactionHistory.from_wallet).selectinload(Wallet.currency),
            selectinload(TransactionHistory.to_wallet).selectinload(Wallet.currency),
            selectinload(TransactionHistory.credit_operation).selectinload(CreditOperation.credit_type),
            selectinload(TransactionHistory.debit_operation).selectinload(DebitOperation.debit_type),
        )
        .where(TransactionHistory.user_id == user_id)
        .order_by(desc(TransactionHistory.transaction_date))
        .limit(limit)
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())