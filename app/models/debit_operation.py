from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from app.core.database import Base


class DebitOperation(Base):
    __tablename__ = "debit_operation"

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int | None] = mapped_column(ForeignKey("wallet.id"), nullable=True)
    operation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    debit_type_id: Mapped[int | None] = mapped_column(ForeignKey("debit_type.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


