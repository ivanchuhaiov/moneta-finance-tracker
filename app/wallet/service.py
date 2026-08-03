from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wallet
from app.wallet import repository
from app.wallet.schemas import WalletCreate, WalletUpdate


async def create_wallet(session: AsyncSession, data: WalletCreate, user_id: int) -> Wallet:
    return await repository.create_wallet(session, data, user_id)


async def get_wallet_by_id(session: AsyncSession, wallet_id: int) -> Wallet | None:
    return await repository.get_wallet_by_id(session, wallet_id)


async def get_wallets_by_user(session: AsyncSession, user_id: int) -> list[Wallet]:
    return await repository.get_wallet_by_user(session, user_id)


async def update_wallet(session: AsyncSession, wallet: Wallet, data: WalletUpdate) -> Wallet:
    return await repository.update_wallet(session, wallet, data)


async def delete_wallet(session: AsyncSession, wallet: Wallet) -> None:
    await repository.delete_wallet(session, wallet)


async def deactivate_wallet(session: AsyncSession, wallet: Wallet) -> Wallet:
    return await repository.deactivate_wallet(session, wallet)