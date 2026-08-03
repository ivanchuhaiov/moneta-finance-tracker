from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Currency(Base):
    __tablename__ = "currency"
    __table_args__ = (
        UniqueConstraint("code", name="uq_currency_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(150))
    symbol: Mapped[str | None] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(10), nullable=False)