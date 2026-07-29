from datetime import date, datetime, timezone
from decimal import Decimal
from calendar import monthrange
from collections import defaultdict
from typing import NamedTuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TransactionHistory, Wallet
from app.analytics import repository
from app.analytics.conversion import RatesIndex, find_rate_for_date, convert_amount, round_money
from app.analytics.schemas import (
    SummarySchema, CategoryBreakdownSchema, WalletSummarySchema, TrendPointSchema, TransactionType,
)


class TransactionAmount(NamedTuple):
    transaction: TransactionHistory
    amount: Decimal | None
    currency: str | None
    category: str | None


def get_period_range(period: str, target_date: date) -> tuple[datetime, datetime]:
    if period != "month":
        raise ValueError(f"Unsupported period: {period}")

    year, month = target_date.year, target_date.month
    days_in_month = monthrange(year, month)[1]

    date_from = datetime(year, month, 1, tzinfo=timezone.utc)
    date_to = datetime(year, month, days_in_month, 23, 59, 59, tzinfo=timezone.utc)

    return date_from, date_to


def get_transaction_amount_and_currency(tx: TransactionHistory) -> tuple[Decimal | None, str | None, str | None]:
    if tx.operation_code == "credit":
        category = "Без категории"
        if tx.credit_operation and tx.credit_operation.credit_type:
            category = tx.credit_operation.credit_type.name
        return tx.from_amount, tx.to_wallet.currency.code, category

    if tx.operation_code == "debit":
        category = "Без категории"
        if tx.debit_operation and tx.debit_operation.debit_type:
            category = tx.debit_operation.debit_type.name
        return tx.from_amount, tx.from_wallet.currency.code, category

    return None, None, None


def filter_relevant_transactions(transactions: list[TransactionHistory]) -> list[TransactionHistory]:
    result = []
    for tx in transactions:
        if tx.operation_code != "transfer":
            result.append(tx)
    return result


def enrich_transactions(transactions: list[TransactionHistory]) -> list[TransactionAmount]:
    enriched = []
    for tx in transactions:
        amount, currency, category = get_transaction_amount_and_currency(tx)
        enriched.append(TransactionAmount(tx, amount, currency, category))
    return enriched


def collect_currency_pairs(enriched: list[TransactionAmount], target_currency: str) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for item in enriched:
        if item.currency is None or item.currency == target_currency:
            continue
        pairs.add((item.currency, target_currency))
    return pairs


async def _prepare_period_data(
    session: AsyncSession, user_id: int, period: str, target_date: date, target_currency: str
) -> tuple[list[TransactionAmount], RatesIndex, datetime]:

    date_from, date_to = get_period_range(period, target_date)
    transactions = await repository.get_transactions_for_period(session, user_id, date_from, date_to)

    relevant = filter_relevant_transactions(transactions)
    enriched = enrich_transactions(relevant)

    pairs = collect_currency_pairs(enriched, target_currency)
    rates_index = await repository.get_rates_batch(session, pairs, date_to)

    return enriched, rates_index, date_to


async def get_summary(
    session: AsyncSession, user_id: int, period: str, target_date: date, target_currency: str
) -> SummarySchema:
    enriched, rates_index, date_to = await _prepare_period_data(session, user_id, period, target_date, target_currency)

    total_income = Decimal("0")
    total_expense = Decimal("0")
    missing_count = 0

    for item in enriched:
        rate = find_rate_for_date(rates_index, item.currency, target_currency, item.transaction.transaction_date)
        converted = convert_amount(item.amount, item.currency, target_currency, rate, item.transaction.transaction_date)

        if converted is None:
            missing_count += 1
            continue

        if item.transaction.operation_code == "credit":
            total_income += converted
        else:
            total_expense += converted

    return SummarySchema(
        total_income=round_money(total_income),
        total_expense=round_money(total_expense),
        net=round_money(total_income - total_expense),
        currency=target_currency,
        has_missing_data=missing_count > 0,
        missing_count=missing_count,
    )


async def get_by_category(
    session: AsyncSession, user_id: int, period: str, target_date: date, target_currency: str
) -> list[CategoryBreakdownSchema]:
    enriched, rates_index, date_to = await _prepare_period_data(session, user_id, period, target_date, target_currency)

    totals: dict[tuple[str, TransactionType], Decimal] = defaultdict(lambda: Decimal("0"))
    missing_counts: dict[tuple[str, TransactionType], int] = defaultdict(int)

    for item in enriched:
        rate = find_rate_for_date(rates_index, item.currency, target_currency, item.transaction.transaction_date)
        converted = convert_amount(item.amount, item.currency, target_currency, rate, item.transaction.transaction_date)

        if item.transaction.operation_code == "credit":
            type_label = TransactionType.INCOME
        else:
            type_label = TransactionType.EXPENSE

        key = (item.category, type_label)

        if converted is None:
            missing_counts[key] += 1
            continue

        totals[key] += converted

    result = []
    for key, total in totals.items():
        category = key[0]
        type_label = key[1]
        missing_count = missing_counts[key]

        breakdown = CategoryBreakdownSchema(
            category=category,
            total=round_money(total),
            type=type_label,
            has_missing_data=missing_count > 0,
            missing_count=missing_count,
        )
        result.append(breakdown)

    return result

def _new_wallet_entry(wallet: Wallet) -> dict:
    return {
        "wallet_name": wallet.name,
        "wallet_currency": wallet.currency.code,
        "total_in_wallet_currency": Decimal("0"),
        "total_in_target_currency": Decimal("0"),
        "missing_count": 0,
    }


def _apply_wallet_delta(
    wallet_totals: dict, wallet_id: int, amount: Decimal, converted: Decimal | None, sign: int
) -> None:
    entry = wallet_totals[wallet_id]
    entry["total_in_wallet_currency"] += sign * amount

    if converted is None:
        entry["missing_count"] += 1
        return

    entry["total_in_target_currency"] += sign * converted


async def get_by_wallet(
    session: AsyncSession, user_id: int, period: str, target_date: date, target_currency: str
) -> list[WalletSummarySchema]:
    date_from, date_to = get_period_range(period, target_date)
    transactions = await repository.get_transactions_for_period(session, user_id, date_from, date_to)

    wallets = await repository.get_wallets_for_analytics(session, user_id)

    wallet_totals = {}
    for wallet in wallets:
        wallet_totals[wallet.id] = _new_wallet_entry(wallet)

    included_wallet_ids = set(wallet_totals.keys())

    pairs = set()
    for wallet in wallets:
        if wallet.currency.code != target_currency:
            pairs.add((wallet.currency.code, target_currency))

    rates_index = await repository.get_rates_batch(session, pairs, date_to)

    for tx in transactions:
        legs = []

        if tx.operation_code == "credit" and tx.to_wallet_id in included_wallet_ids:
            legs.append((tx.to_wallet_id, tx.to_wallet.currency.code, tx.from_amount, 1))

        elif tx.operation_code == "debit" and tx.from_wallet_id in included_wallet_ids:
            legs.append((tx.from_wallet_id, tx.from_wallet.currency.code, tx.from_amount, -1))

        elif tx.operation_code == "transfer":
            if tx.from_wallet_id in included_wallet_ids:
                legs.append((tx.from_wallet_id, tx.from_wallet.currency.code, tx.from_amount, -1))
            if tx.to_wallet_id in included_wallet_ids:
                legs.append((tx.to_wallet_id, tx.to_wallet.currency.code, tx.to_amount, 1))

        for wallet_id, currency, amount, sign in legs:
            rate = find_rate_for_date(rates_index, currency, target_currency, tx.transaction_date)
            converted = convert_amount(amount, currency, target_currency, rate, tx.transaction_date)
            _apply_wallet_delta(wallet_totals, wallet_id, amount, converted, sign)

    result = []
    for wallet_id, data in wallet_totals.items():
        summary = WalletSummarySchema(
            wallet_id=wallet_id,
            wallet_name=data["wallet_name"],
            wallet_currency=data["wallet_currency"],
            total_in_wallet_currency=round_money(data["total_in_wallet_currency"]),
            total_in_target_currency=round_money(data["total_in_target_currency"]),
            has_missing_data=data["missing_count"] > 0,
            missing_count=data["missing_count"],
        )
        result.append(summary)

    return result


async def get_trend(
    session: AsyncSession, user_id: int, months: int, target_currency: str
) -> list[TrendPointSchema]:
    today = date.today()
    points = []

    for i in range(months - 1, -1, -1):
        month_offset = today.month - 1 - i
        year = today.year + month_offset // 12
        month = month_offset % 12 + 1
        point_date = date(year, month, 1)

        summary = await get_summary(session, user_id, "month", point_date, target_currency)

        points.append(
            TrendPointSchema(
                period=f"{year}-{month:02d}",
                income=summary.total_income,
                expense=summary.total_expense,
                net=summary.net,
            )
        )

    return points