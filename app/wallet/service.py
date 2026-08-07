from sqlalchemy.ext.asyncio import AsyncSession

from app.core.log_audit_event import log_audit_event
from app.core.enums import AuditAction, EntityType
from app.models import Wallet, WalletType, Currency
from app.wallet import repository
from app.wallet.schemas import WalletCreate, WalletUpdate, WalletTypeCreate


async def create_wallet(session: AsyncSession, data: WalletCreate, user_id: int) -> Wallet:
    wallet = await repository.create_wallet(session, data, user_id)

    await log_audit_event(
        session=session,
        user_id=user_id,
        action=AuditAction.CREATE,
        entity_type=EntityType.WALLET,
        entity_id=wallet.id,
        details={"name": wallet.name, "balance": str(wallet.balance)},
    )

    await session.commit()
    await session.refresh(wallet)
    return wallet


async def get_wallet_by_id(session: AsyncSession, wallet_id: int) -> Wallet | None:
    return await repository.get_wallet_by_id(session, wallet_id)


async def get_wallets_by_user(session: AsyncSession, user_id: int) -> list[Wallet]:
    return await repository.get_wallets_by_user(session, user_id)


async def update_wallet(session: AsyncSession, wallet: Wallet, data: WalletUpdate) -> Wallet:
    update_data = data.model_dump(exclude_unset=True)
    wallet = await repository.update_wallet(session, wallet, data)

    await log_audit_event(
        session=session,
        user_id=wallet.user_id,
        action=AuditAction.UPDATE,
        entity_type=EntityType.WALLET,
        entity_id=wallet.id,
        details=update_data,
    )

    await session.commit()
    await session.refresh(wallet)
    return wallet


async def delete_wallet(session: AsyncSession, wallet: Wallet) -> None:
    wallet_id = wallet.id
    user_id = wallet.user_id

    await log_audit_event(
        session=session,
        user_id=user_id,
        action=AuditAction.DELETE,
        entity_type=EntityType.WALLET,
        entity_id=wallet_id,
    )

    await repository.delete_wallet(session, wallet)
    await session.commit()


async def deactivate_wallet(session: AsyncSession, wallet: Wallet) -> Wallet:
    wallet = await repository.deactivate_wallet(session, wallet)

    await log_audit_event(
        session=session,
        user_id=wallet.user_id,
        action=AuditAction.UPDATE,
        entity_type=EntityType.WALLET,
        entity_id=wallet.id,
        details={"is_active": False},
    )

    await session.commit()
    await session.refresh(wallet)
    return wallet

async def create_wallet_type(session, user_id, data: WalletTypeCreate) -> WalletType:
    wallet_type = await repository.create_wallet_type(session, data, user_id)

    await log_audit_event(
        session=session,
        user_id=user_id,
        action=AuditAction.CREATE,
        entity_type=EntityType.WALLET,
        entity_id=wallet_type.id,
        details={"name": wallet_type.name},
    )

    await session.commit()
    await session.refresh(wallet_type)
    return wallet_type

async def get_wallet_types_by_user(session, user_id) -> list[WalletType]:
    return await repository.get_wallet_types_by_user(session, user_id)

async def get_all_currencies(session: AsyncSession) -> list[Currency]:
    return await repository.get_all_currencies(session)