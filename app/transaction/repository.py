from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import CreditOperation, DebitOperation, TransactionHistory, Wallet
from app.models import CreditOperation, CreditType, DebitOperation, DebitType, TransactionHistory, Wallet

async def get_debit_operations(session: AsyncSession, wallet_id: int) -> list[DebitOperation]:
    result = await session.execute(
        select(DebitOperation).where(DebitOperation.wallet_id == wallet_id)
    )
    return list(result.scalars().all())


async def get_credit_operations(session: AsyncSession, wallet_id: int) -> list[CreditOperation]:
    result = await session.execute(
        select(CreditOperation).where(CreditOperation.wallet_id == wallet_id)
    )
    return list(result.scalars().all())


async def get_credit_sum(session: AsyncSession, wallet_id: int) -> Decimal | None:
    result = await session.execute(
        select(func.sum(CreditOperation.amount)).where(CreditOperation.wallet_id == wallet_id)
    )
    return result.scalar()


async def get_debit_sum(session: AsyncSession, wallet_id: int) -> Decimal | None:
    result = await session.execute(
        select(func.sum(DebitOperation.amount)).where(DebitOperation.wallet_id == wallet_id)
    )
    return result.scalar()


async def get_wallets_included_in_balance(session: AsyncSession, user_id: int) -> list[Wallet]:
    result = await session.execute(
        select(Wallet)
        .options(selectinload(Wallet.currency))
        .where(Wallet.user_id == user_id, Wallet.is_include_in_balance.is_(True))
    )
    return list(result.scalars().all())


async def save_credit_operation(session: AsyncSession, credit_operation: CreditOperation) -> CreditOperation:
    session.add(credit_operation)
    await session.flush()
    return credit_operation


async def save_debit_operation(session: AsyncSession, debit_operation: DebitOperation) -> DebitOperation:
    session.add(debit_operation)
    await session.flush()
    return debit_operation


async def save_transaction(session: AsyncSession, transaction: TransactionHistory) -> TransactionHistory:
    session.add(transaction)
    await session.flush()
    return transaction


async def get_transaction_history(session: AsyncSession, user_id: int) -> list[TransactionHistory]:
    result = await session.execute(
        select(TransactionHistory)
        .where(TransactionHistory.user_id == user_id)
        .order_by(TransactionHistory.transaction_date.desc())
    )
    return list(result.scalars().all())

async def save_credit_type(session: AsyncSession, credit_type: CreditType) -> CreditType:
    session.add(credit_type)
    await session.flush()
    return credit_type


async def save_debit_type(session: AsyncSession, debit_type: DebitType) -> DebitType:
    session.add(debit_type)
    await session.flush()
    return debit_type


async def get_credit_types_by_user(session: AsyncSession, user_id: int) -> list[CreditType]:
    result = await session.execute(
        select(CreditType).where(CreditType.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_debit_types_by_user(session: AsyncSession, user_id: int) -> list[DebitType]:
    result = await session.execute(
        select(DebitType).where(DebitType.user_id == user_id)
    )
    return list(result.scalars().all())