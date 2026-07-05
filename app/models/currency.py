from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Currency(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(150))
    symbol: Mapped[str | None] = mapped_column(String(50))
    code: Mapped[str | None] = mapped_column(String(100))
