from datetime import datetime
from pydantic import BaseModel, ConfigDict
from decimal import Decimal



class CreditOperationRequest(BaseModel):
    amount: Decimal
    credit_type_id: int
    operation_date: datetime

class DebitOperationRequest(BaseModel):
    amount: Decimal
    debit_type_id: int
    operation_date: datetime

class CreditOperationResponse(BaseModel):
    id: int
    wallet_id: int
    amount: Decimal
    credit_type_id: int | None = None
    operation_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DebitOperationResponse(BaseModel):
    id: int
    wallet_id: int
    amount: Decimal
    debit_type_id: int | None = None
    operation_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransferRequest(BaseModel):
    from_wallet_id: int
    to_wallet_id: int
    amount: Decimal
    description: str | None = None

class TransactionHistoryResponse(BaseModel):
    id: int
    from_wallet_id: int | None
    to_wallet_id: int | None
    from_amount: Decimal
    to_amount: Decimal | None
    operation_code: str
    transaction_date: datetime
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WalletBalanceResponse(BaseModel):
    wallet_id: int
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)

class TotalBalanceResponse(BaseModel):
    user_id: int
    balance: Decimal
    currency: str

    model_config = ConfigDict(from_attributes=True)

class OperationsListResponse(BaseModel):
    debits: list[DebitOperationResponse]
    credits: list[CreditOperationResponse]

class CreditTypeCreate(BaseModel):
    code: str
    name: str

class CreditTypeResponse(BaseModel):
    id: int
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class DebitTypeCreate(BaseModel):
    code: str
    name: str

class DebitTypeResponse(BaseModel):
    id: int
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class CurrencyResponse(BaseModel):
    id: int
    code: str
    name: str
    symbol: str

    model_config = ConfigDict(from_attributes=True)
