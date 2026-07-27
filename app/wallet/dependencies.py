from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.models import User, Wallet
from app.wallet.service import get_wallet_by_id


async def get_owned_wallet(
    wallet_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Wallet:
    wallet = await get_wallet_by_id(session, wallet_id)

    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    if wallet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your wallet")

    return wallet

async def get_active_owned_wallet(
    wallet: Wallet = Depends(get_owned_wallet),
) -> Wallet:
    if not wallet.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wallet is not active")
    return wallet