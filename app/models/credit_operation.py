from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from app.core.database import Base


class CreditOperation(Base):
    __tablename__ = "credit_operation"

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int | None] = mapped_column(ForeignKey("wallet.id"), nullable=False)
    operation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    credit_type_id: Mapped[int | None] = mapped_column(ForeignKey("credit_type.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

