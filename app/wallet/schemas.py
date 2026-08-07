from datetime import datetime
from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class WalletCreate(BaseModel):
    name: str
    wallet_type_id: int
    currency_id: int
    balance: Decimal

class WalletUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None

class WalletResponse(BaseModel):
    id: int
    name: str
    balance: Decimal
    currency_id: int
    wallet_type_id: int
    is_active: bool
    is_include_in_balance: bool
    created_at: datetime
    updated_at: datetime
    blocked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class WalletTypeCreate(BaseModel):
    code: str
    name: str

class WalletTypeResponse(BaseModel):
    id: int
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class CurrencyResponse(BaseModel):
    name: str
    code: str

