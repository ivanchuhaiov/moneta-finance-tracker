from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.models import Wallet
from app.wallet.schemas import WalletCreate, WalletUpdate


async def create_wallet(session: AsyncSession, data: WalletCreate, user_id: int) -> Wallet:
    wallet = Wallet(
        name=data.name,
        wallet_type_id=data.wallet_type_id,
        currency_id=data.currency_id,
        user_id=user_id,
        balance=data.balance
    )
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    return wallet

async def get_wallet_by_id(session: AsyncSession, wallet_id: int) -> Wallet | None:
    result = await session.execute(select(Wallet).where(Wallet.id == wallet_id))
    return result.scalar_one_or_none()

async def get_wallet_by_user(session: AsyncSession, user_id: int) -> list[Wallet]:
    result = await session.execute(select(Wallet).where(Wallet.user_id == user_id))
    return list(result.scalars().all())

async def update_wallet(session: AsyncSession, wallet: Wallet, data: WalletUpdate) -> Wallet:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wallet, field, value)
    await session.commit()
    await session.refresh(wallet)
    return wallet

async def delete_wallet(session: AsyncSession, wallet: Wallet) -> None:
    await session.delete(wallet)
    await session.commit()

async def deactivate_wallet(session: AsyncSession, wallet: Wallet) -> Wallet:
    wallet.is_active = False
    wallet.blocked_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(wallet)
    return wallet






