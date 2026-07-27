from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.exchange.service import get_latest_rate
from app.models import CreditOperation, DebitOperation, User, TransactionHistory, Wallet
from app.transaction.schema import CreditOperationRequest, DebitOperationRequest, TransferRequest
from app.wallet.service import get_wallet_by_id


async def create_credit_operation(session: AsyncSession, wallet_id: int, data: CreditOperationRequest, current_user: User):
    credit_operation = CreditOperation(
        wallet_id=wallet_id,
        amount=data.amount,
        credit_type_id=data.credit_type_id,
        operation_date=data.operation_date,
        created_at=datetime.now(timezone.utc),
    )
    session.add(credit_operation)
    await session.flush()

    transaction = TransactionHistory(
        user_id=current_user.id,
        operation_code="credit",
        transaction_date=data.operation_date,
        to_wallet_id=wallet_id,
        from_amount=data.amount,
        credit_operation_id=credit_operation.id,
    )
    session.add(transaction)

    await session.commit()
    await session.refresh(credit_operation)
    return credit_operation


async def create_debit_operation(session: AsyncSession, wallet_id: int, data: DebitOperationRequest, current_user: User):
    debit_operation = DebitOperation(
        wallet_id=wallet_id,
        amount=data.amount,
        debit_type_id=data.debit_type_id,
        operation_date=data.operation_date,
        created_at=datetime.now(timezone.utc),
    )
    session.add(debit_operation)
    await session.flush()

    transaction = TransactionHistory(
        user_id=current_user.id,
        operation_code="debit",
        transaction_date=data.operation_date,
        from_wallet_id=wallet_id,
        from_amount=data.amount,
        debit_operation_id=debit_operation.id,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(debit_operation)
    return debit_operation


async def get_operations_by_wallet(session: AsyncSession, wallet_id: int):
    debit_result = await session.execute(
        select(DebitOperation).where(DebitOperation.wallet_id == wallet_id)
    )
    credit_result = await session.execute(
        select(CreditOperation).where(CreditOperation.wallet_id == wallet_id)
    )

    debits = debit_result.scalars().all()
    credits = credit_result.scalars().all()

    return {"debits": debits, "credits": credits}


async def get_wallet_balance(session: AsyncSession, wallet_id: int) -> Decimal:
    wallet = await get_wallet_by_id(session, wallet_id)
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    credit_result = await session.execute(
        select(func.sum(CreditOperation.amount)).where(CreditOperation.wallet_id == wallet_id)
    )
    debit_result = await session.execute(
        select(func.sum(DebitOperation.amount)).where(DebitOperation.wallet_id == wallet_id)
    )

    total_credit = credit_result.scalar() or Decimal("0")
    total_debit = debit_result.scalar() or Decimal("0")

    return wallet.balance + total_credit - total_debit


async def get_total_balance(session: AsyncSession, user_id: int, target_currency: str) -> Decimal:
    result = await session.execute(
        select(Wallet)
        .options(selectinload(Wallet.currency))
        .where(Wallet.user_id == user_id, Wallet.is_include_in_balance == True)
    )
    wallets = result.scalars().all()
    total = Decimal("0")
    for wallet in wallets:
        wallet_balance = await get_wallet_balance(session, wallet.id)

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


async def transfer_between_wallets(session: AsyncSession, data: TransferRequest, current_user: User):
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
    if not to_wallet.is_active:
        raise HTTPException(status_code=400, detail="To wallet is not active")
    if to_wallet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your wallet")

    from_wallet_balance = await get_wallet_balance(session, data.from_wallet_id)  # TODO: avoid double wallet fetch
    if from_wallet_balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    if from_wallet.currency.code == to_wallet.currency.code:
        to_amount = data.amount
        rate_used = None
    else:
        rate_used = await get_latest_rate(session, base=from_wallet.currency.code, target=to_wallet.currency.code)
        if rate_used is None:
            raise HTTPException(status_code=400,
                                detail=f"No exchange rate available for {from_wallet.currency.code} -> {to_wallet.currency.code}")
        to_amount = (data.amount * rate_used).quantize(Decimal("0.01"))

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
    session.add(debit_operation)
    session.add(credit_operation)
    await session.flush()

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

    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


async def get_transaction_history(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(TransactionHistory)
        .where(TransactionHistory.user_id == user_id)
        .order_by(TransactionHistory.transaction_date.desc())
    )
    return result.scalars().all()