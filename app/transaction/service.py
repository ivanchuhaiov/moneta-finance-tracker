from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.exchange.service import get_latest_rate
from app.models import CreditOperation, DebitOperation, TransactionHistory, User, Wallet
from app.transaction import repository
from app.transaction.schemas import CreditOperationRequest, DebitOperationRequest, TransferRequest
from app.wallet.service import get_wallet_by_id


async def create_credit_operation(
    session: AsyncSession, wallet_id: int, data: CreditOperationRequest, current_user: User
) -> CreditOperation:
    credit_operation = CreditOperation(
        wallet_id=wallet_id,
        amount=data.amount,
        credit_type_id=data.credit_type_id,
        operation_date=data.operation_date,
        created_at=datetime.now(timezone.utc),
    )
    await repository.save_credit_operation(session, credit_operation)

    transaction = TransactionHistory(
        user_id=current_user.id,
        operation_code="credit",
        transaction_date=data.operation_date,
        to_wallet_id=wallet_id,
        from_amount=data.amount,
        credit_operation_id=credit_operation.id,
    )
    await repository.save_transaction(session, transaction)
    await session.refresh(credit_operation)

    return credit_operation


async def create_debit_operation(
    session: AsyncSession, wallet_id: int, data: DebitOperationRequest, current_user: User
) -> DebitOperation:
    debit_operation = DebitOperation(
        wallet_id=wallet_id,
        amount=data.amount,
        debit_type_id=data.debit_type_id,
        operation_date=data.operation_date,
        created_at=datetime.now(timezone.utc),
    )
    await repository.save_debit_operation(session, debit_operation)

    transaction = TransactionHistory(
        user_id=current_user.id,
        operation_code="debit",
        transaction_date=data.operation_date,
        from_wallet_id=wallet_id,
        from_amount=data.amount,
        debit_operation_id=debit_operation.id,
    )
    await repository.save_transaction(session, transaction)
    await session.refresh(debit_operation)

    return debit_operation


async def get_operations_by_wallet(session: AsyncSession, wallet_id: int) -> dict:
    debits = await repository.get_debit_operations(session, wallet_id)
    credits = await repository.get_credit_operations(session, wallet_id)
    return {"debits": debits, "credits": credits}


async def calculate_balance(session: AsyncSession, wallet: Wallet) -> Decimal:
    total_credit = await repository.get_credit_sum(session, wallet.id) or Decimal("0")
    total_debit = await repository.get_debit_sum(session, wallet.id) or Decimal("0")
    return wallet.balance + total_credit - total_debit


async def get_wallet_balance(session: AsyncSession, wallet_id: int) -> Decimal:
    wallet = await get_wallet_by_id(session, wallet_id)
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    return await calculate_balance(session, wallet)


async def get_total_balance(session: AsyncSession, user_id: int, target_currency: str) -> Decimal:
    wallets = await repository.get_wallets_included_in_balance(session, user_id)

    total = Decimal("0")
    for wallet in wallets:
        wallet_balance = await calculate_balance(session, wallet)

        if wallet.currency.code == target_currency:
            converted_balance = wallet_balance
        else:
            rate = await get_latest_rate(session, base=wallet.currency.code, target=target_currency)
            if rate is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"No exchange rate available for {wallet.currency.code} -> {target_currency}"
                )
            converted_balance = (wallet_balance * rate).quantize(Decimal("0.01"))

        total += converted_balance

    return total


async def _validate_transfer(session: AsyncSession, data: TransferRequest, current_user: User) -> tuple[Wallet, Wallet]:
    if data.from_wallet_id == data.to_wallet_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same wallet")

    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    from_wallet = await get_wallet_by_id(session, data.from_wallet_id)
    if from_wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="From wallet not found")
    if from_wallet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your wallet")
    if not from_wallet.is_active:
        raise HTTPException(status_code=400, detail="From wallet is not active")

    to_wallet = await get_wallet_by_id(session, data.to_wallet_id)
    if to_wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To wallet not found")
    if to_wallet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your wallet")
    if not to_wallet.is_active:
        raise HTTPException(status_code=400, detail="To wallet is not active")

    return from_wallet, to_wallet


async def _convert_transfer_amount(
    session: AsyncSession, amount: Decimal, from_wallet: Wallet, to_wallet: Wallet
) -> tuple[Decimal, Decimal | None]:
    if from_wallet.currency.code == to_wallet.currency.code:
        return amount, None

    rate = await get_latest_rate(session, base=from_wallet.currency.code, target=to_wallet.currency.code)
    if rate is None:
        raise HTTPException(
            status_code=400,
            detail=f"No exchange rate available for {from_wallet.currency.code} -> {to_wallet.currency.code}"
        )

    to_amount = (amount * rate).quantize(Decimal("0.01"))
    return to_amount, rate


async def transfer_between_wallets(session: AsyncSession, data: TransferRequest, current_user: User) -> TransactionHistory:
    from_wallet, to_wallet = await _validate_transfer(session, data, current_user)

    from_wallet_balance = await calculate_balance(session, from_wallet)
    if from_wallet_balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    to_amount, rate_used = await _convert_transfer_amount(session, data.amount, from_wallet, to_wallet)

    now = datetime.now(timezone.utc)

    debit_operation = DebitOperation(
        wallet_id=data.from_wallet_id,
        amount=data.amount,
        operation_date=now,
        created_at=now,
    )
    credit_operation = CreditOperation(
        wallet_id=data.to_wallet_id,
        amount=to_amount,
        operation_date=now,
        created_at=now,
    )

    await repository.save_debit_operation(session, debit_operation)
    await repository.save_credit_operation(session, credit_operation)

    transaction = TransactionHistory(
        user_id=current_user.id,
        operation_code="transfer",
        transaction_date=now,
        from_wallet_id=data.from_wallet_id,
        to_wallet_id=data.to_wallet_id,
        from_amount=data.amount,
        to_amount=to_amount,
        exchange_rate=rate_used,
        description=data.description,
        debit_operation_id=debit_operation.id,
        credit_operation_id=credit_operation.id,
    )

    return await repository.save_transaction(session, transaction)


async def get_transaction_history(session: AsyncSession, user_id: int) -> list[TransactionHistory]:
    return await repository.get_transaction_history(session, user_id)