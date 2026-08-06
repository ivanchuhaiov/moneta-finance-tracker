from enum import Enum


class CurrencyCode(str, Enum):
    EUR = "EUR"
    USD = "USD"
    UAH = "UAH"


class JobStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class EntityType(str, Enum):
    WALLET = "WALLET"
    TRANSACTION = "TRANSACTION"
    REPORT = "REPORT"

