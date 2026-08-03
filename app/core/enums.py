from enum import Enum


class CurrencyCode(str, Enum):
    EUR = "EUR"
    USD = "USD"
    UAH = "UAH"


class JobStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"