from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.models import User, Wallet
from app.wallet.dependencies import get_active_owned_wallet
from app.transaction.schema import (
    CreditOperationRequest,
    CreditOperationResponse,
    DebitOperationRequest,
    DebitOperationResponse,
    TransferRequest,
    TransactionHistoryResponse,
    WalletBalanceResponse, TotalBalanceResponse, OperationsListResponse,
)
from app.transaction.service import (
    create_credit_operation,
    create_debit_operation,
    get_wallet_balance,
    transfer_between_wallets,
    get_transaction_history, get_operations_by_wallet, get_total_balance,
)

router = APIRouter(tags=["transactions"])
@router.post("/transactions/transfer", response_model=TransactionHistoryResponse)
async def transfer(
    data: TransferRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await transfer_between_wallets(session, data, current_user)


@router.get("/transactions/history", response_model=list[TransactionHistoryResponse])
async def transaction_history(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_transaction_history(session, current_user.id)

@router.get("/wallets/summary/total-balance", response_model=TotalBalanceResponse)
async def get_total_wallet_balance(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    balance = await get_total_balance(session, current_user.id)
    return TotalBalanceResponse(user_id=current_user.id, balance=balance)

@router.get("/wallets/{wallet_id}/operations", response_model=OperationsListResponse)
async def get_operations(
    wallet: Wallet = Depends(get_active_owned_wallet),
    session: AsyncSession = Depends(get_db),
):
    return await get_operations_by_wallet(session, wallet.id)

@router.post("/wallets/{wallet_id}/credit", response_model=CreditOperationResponse)
async def create_credit(
    data: CreditOperationRequest,
    wallet: Wallet = Depends(get_active_owned_wallet),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_credit_operation(session, wallet.id, data, current_user)


@router.post("/wallets/{wallet_id}/debit", response_model=DebitOperationResponse)
async def create_debit(
    data: DebitOperationRequest,
    wallet: Wallet = Depends(get_active_owned_wallet),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),

):
    return await create_debit_operation(session, wallet.id, data, current_user)


@router.get("/wallets/{wallet_id}/balance", response_model=WalletBalanceResponse)
async def get_balance(
    wallet: Wallet = Depends(get_active_owned_wallet),
    session: AsyncSession = Depends(get_db),
):
    balance = await get_wallet_balance(session, wallet.id)
    return WalletBalanceResponse(wallet_id=wallet.id, balance=balance)

