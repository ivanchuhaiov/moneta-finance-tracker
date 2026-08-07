from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Wallet, WalletType, Currency
from app.wallet.schemas import WalletCreate, WalletUpdate, WalletTypeCreate


async def create_wallet(session: AsyncSession, data: WalletCreate, user_id: int) -> Wallet:
    wallet = Wallet(
        name=data.name,
        wallet_type_id=data.wallet_type_id,
        currency_id=data.currency_id,
        user_id=user_id,
        balance=data.balance,
    )
    session.add(wallet)
    await session.flush()
    return wallet


async def create_wallet_type(session: AsyncSession, data: WalletTypeCreate, user_id: int) -> WalletType:
    wallet_type = WalletType(
        name=data.name,
        code=data.code,
        user_id=user_id,
    )
    session.add(wallet_type)
    await session.flush()
    return wallet_type


async def get_wallet_by_id(session: AsyncSession, wallet_id: int) -> Wallet | None:
    result = await session.execute(
        select(Wallet)
        .options(selectinload(Wallet.currency))
        .where(Wallet.id == wallet_id)
    )
    return result.scalar_one_or_none()


async def get_wallets_by_user(session: AsyncSession, user_id: int) -> list[Wallet]:
    result = await session.execute(
        select(Wallet)
        .options(selectinload(Wallet.currency))
        .where(Wallet.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_wallet_types_by_user(session: AsyncSession, user_id: int) -> list[WalletType]:
    result = await session.execute(
        select(WalletType)
        .where(WalletType.user_id == user_id)
    )
    return list(result.scalars().all())


async def update_wallet(session: AsyncSession, wallet: Wallet, data: WalletUpdate) -> Wallet:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wallet, field, value)
    return wallet


async def delete_wallet(session: AsyncSession, wallet: Wallet) -> None:
    await session.delete(wallet)


async def deactivate_wallet(session: AsyncSession, wallet: Wallet) -> Wallet:
    wallet.is_active = False
    wallet.blocked_at = datetime.now(timezone.utc)
    return wallet

async def get_all_currencies(session: AsyncSession) -> list[Currency]:
    result = await session.execute(select(Currency))
    return list(result.scalars().all())