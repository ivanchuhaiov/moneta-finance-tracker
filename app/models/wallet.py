from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Numeric, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.id"), nullable=False)
    wallet_type_id: Mapped[int] = mapped_column(ForeignKey("wallet_type.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_include_in_balance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="wallets")
    wallet_type: Mapped["WalletType"] = relationship()
    currency: Mapped["Currency"] = relationship()


