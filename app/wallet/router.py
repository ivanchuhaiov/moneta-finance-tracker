from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models import User, Wallet
from app.wallet.dependencies import get_owned_wallet
from app.wallet.schemas import (
    WalletCreate,
    WalletResponse,
    WalletUpdate,
    WalletTypeCreate,
    WalletTypeResponse, CurrencyResponse,
)
from app.wallet.service import (
    create_wallet,
    create_wallet_type,
    deactivate_wallet,
    get_wallets_by_user,
    get_wallet_types_by_user,
    update_wallet, get_all_currencies,
)

router = APIRouter(prefix="/wallets", tags=["wallets"])
wallet_type_router = APIRouter(prefix="/wallet-types", tags=["wallet-types"])


@router.post("", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet_endpoint(
    data: WalletCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_wallet(session, data, current_user.id)


@router.get("", response_model=list[WalletResponse])
async def list_wallets(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_wallets_by_user(session, current_user.id)

@router.get("/currencies", response_model=list[CurrencyResponse])
async def list_currencies(session: AsyncSession = Depends(get_db)):
    return await get_all_currencies(session)

@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(wallet: Wallet = Depends(get_owned_wallet)):
    return wallet


@router.patch("/{wallet_id}", response_model=WalletResponse)
async def update_wallet_endpoint(
    data: WalletUpdate,
    wallet: Wallet = Depends(get_owned_wallet),
    session: AsyncSession = Depends(get_db),
):
    return await update_wallet(session, wallet, data)


@router.delete("/{wallet_id}", response_model=WalletResponse)
async def deactivate_wallet_endpoint(
    wallet: Wallet = Depends(get_owned_wallet),
    session: AsyncSession = Depends(get_db),
):
    return await deactivate_wallet(session, wallet)


@wallet_type_router.post("", response_model=WalletTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet_type_endpoint(
    data: WalletTypeCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_wallet_type(session, current_user.id, data)


@wallet_type_router.get("", response_model=list[WalletTypeResponse])
async def list_wallet_types(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_wallet_types_by_user(session, current_user.id)
