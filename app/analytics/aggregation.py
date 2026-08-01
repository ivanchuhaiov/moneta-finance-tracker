from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import repository
from app.analytics.conversion import find_rate_for_date, convert_amount, round_money
from app.analytics.helpers import (
    get_month_range, build_category_label, get_transaction_display_info, is_wallet_included_in_balance,
)
from app.analytics.schemas import CategoryBreakdownSchema
from app.analytics.helpers import calculate_percentage_share


@dataclass
class CategorizedAmount:
    operation_code: str
    category: str
    amount: Decimal
    transaction_date: datetime


async def get_categorized_amounts(
    session: AsyncSession, user_id: int, date_from: datetime, date_to: datetime, target_currency: str
) -> list[CategorizedAmount]:
    transactions = await repository.get_transactions_for_period(session, user_id, date_from, date_to)

    raw_items = []
    for tx in transactions:
        if tx.operation_code not in ("credit", "debit"):
            continue

        if not is_wallet_included_in_balance(tx):
            continue

        amount, currency = get_transaction_display_info(tx)
        category = build_category_label(tx)
        raw_items.append((tx, amount, currency, category))

    pairs = set()
    for tx, amount, currency, category in raw_items:
        if currency != target_currency:
            pairs.add((currency, target_currency))

    rates_index = await repository.get_rates_batch(session, pairs, date_to)

    result = []
    for tx, amount, currency, category in raw_items:
        rate = find_rate_for_date(rates_index, currency, target_currency, tx.transaction_date)
        converted_amount = convert_amount(amount, currency, target_currency, rate, tx.transaction_date)

        categorized = CategorizedAmount(
            operation_code=tx.operation_code,
            category=category,
            amount=converted_amount,
            transaction_date=tx.transaction_date,
        )
        result.append(categorized)

    return result


def sum_by_operation(items: list[CategorizedAmount], operation_code: str) -> Decimal:
    total = Decimal("0")
    for item in items:
        if item.operation_code == operation_code:
            total += item.amount
    return total


def build_category_breakdown(items: list[CategorizedAmount], operation_code: str) -> list[CategoryBreakdownSchema]:
    totals: dict[str, Decimal] = {}

    for item in items:
        if item.operation_code != operation_code:
            continue
        if item.category not in totals:
            totals[item.category] = Decimal("0")
        totals[item.category] += item.amount

    grand_total = Decimal("0")
    for amount in totals.values():
        grand_total += amount

    result = []
    for category, amount in totals.items():
        breakdown = CategoryBreakdownSchema(
            category=category,
            total=round_money(amount),
            percentage=calculate_percentage_share(amount, grand_total),
        )
        result.append(breakdown)

    return result


async def get_month_totals(
    session: AsyncSession, user_id: int, target_date: date, target_currency: str
) -> tuple[Decimal, Decimal]:
    date_from, date_to = get_month_range(target_date)
    items = await get_categorized_amounts(session, user_id, date_from, date_to, target_currency)

    income = sum_by_operation(items, "credit")
    expense = sum_by_operation(items, "debit")

    return round_money(income), round_money(expense)