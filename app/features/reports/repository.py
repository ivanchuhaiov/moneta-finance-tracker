from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TransactionHistory, CreditOperation, DebitOperation, Wallet


async def get_transactions_by_period(
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
            TransactionHistory.transaction_date < date_to,
        )
        .order_by(desc(TransactionHistory.transaction_date))
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())