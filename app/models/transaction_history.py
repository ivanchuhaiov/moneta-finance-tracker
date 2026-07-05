from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Text, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class TransactionHistory(Base):
    __tablename__ = 'transaction_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('app_user.id'), nullable=False)
    operation_code: Mapped[str] = mapped_column(String(100), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    from_wallet_id: Mapped[int | None] = mapped_column(ForeignKey('wallet.id'))
    to_wallet_id: Mapped[int | None] = mapped_column(ForeignKey('wallet.id'))
    from_amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    to_amount: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    exchange_rate: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable= True)
    debit_operation_id: Mapped[int | None] = mapped_column(ForeignKey('debit_operation.id'))
    credit_operation_id: Mapped[int | None] = mapped_column(ForeignKey('credit_operation.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

