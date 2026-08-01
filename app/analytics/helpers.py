from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from calendar import monthrange

from app.models import TransactionHistory
from app.analytics.conversion import round_money


def get_month_range(target_date: date) -> tuple[datetime, datetime]:
    year, month = target_date.year, target_date.month
    days_in_month = monthrange(year, month)[1]

    date_from = datetime(year, month, 1, tzinfo=timezone.utc)
    date_to = datetime(year, month, days_in_month, 23, 59, 59, tzinfo=timezone.utc)

    return date_from, date_to


def get_previous_month_date(target_date: date) -> date:
    if target_date.month == 1:
        return date(target_date.year - 1, 12, 1)
    return date(target_date.year, target_date.month - 1, 1)


def get_iso_week_start(target_date: date) -> date:
    return target_date - timedelta(days=target_date.weekday())


def build_datetime_range(date_from: date, date_to: date) -> tuple[datetime, datetime]:
    range_from = datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc)
    range_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59, tzinfo=timezone.utc)
    return range_from, range_to


def calculate_percentage_change(current: Decimal, previous: Decimal) -> Decimal:
    if previous == Decimal("0"):
        return Decimal("0")
    change = (current - previous) / previous * Decimal("100")
    return round_money(change)


def calculate_percentage_share(part: Decimal, total: Decimal) -> Decimal:
    if total == Decimal("0"):
        return Decimal("0")
    share = part / total * Decimal("100")
    return round_money(share)


def build_category_label(tx: TransactionHistory) -> str:
    if tx.operation_code == "credit":
        if tx.credit_operation and tx.credit_operation.credit_type:
            return tx.credit_operation.credit_type.name
        return "Без категории"

    if tx.operation_code == "debit":
        if tx.debit_operation and tx.debit_operation.debit_type:
            return tx.debit_operation.debit_type.name
        return "Без категории"

    return "Без категории"


def get_transaction_display_info(tx: TransactionHistory) -> tuple[Decimal, str]:
    if tx.operation_code == "credit":
        return tx.from_amount, tx.to_wallet.currency.code
    if tx.operation_code == "debit":
        return tx.from_amount, tx.from_wallet.currency.code
    return tx.from_amount, tx.from_wallet.currency.code


def is_wallet_included_in_balance(tx: TransactionHistory) -> bool:
    if tx.operation_code == "credit":
        return tx.to_wallet.is_include_in_balance
    if tx.operation_code == "debit":
        return tx.from_wallet.is_include_in_balance
    return True