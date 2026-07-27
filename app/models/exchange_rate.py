from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Numeric, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ExchangeRate(Base):
    __tablename__ = "exchange_rate"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_currency: Mapped[str] = mapped_column(String(3))
    target_currency: Mapped[str] = mapped_column(String(3))
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    __table_args__ = (
        Index("ix_exchange_rate_pair_date", "base_currency", "target_currency", "fetched_at"),
    )