from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import repository
from app.analytics.aggregation import build_category_breakdown, get_categorized_amounts, get_month_totals
from app.analytics.conversion import convert_amount, find_rate_for_date, round_money
from app.analytics.helpers import (
    build_datetime_range, calculate_percentage_change, calculate_percentage_share,
    get_iso_week_start, get_previous_month_date, get_transaction_display_info,
)
from app.analytics.schemas import (
    CashflowWeekSchema, CategoryBreakdownSchema, DashboardSchema,
    PeriodComparisonSchema, RecentTransactionSchema, SavingsRateSchema, WalletBalanceSchema,
)
from app.transaction.service import calculate_balance


RECENT_TRANSACTIONS_LIMIT = 10
CASHFLOW_LOOKBACK_MONTHS = 3
DAYS_IN_CASHFLOW_MONTH = 30


@dataclass
class WeekAccumulator:
    week_start: date
    week_end: date
    income: Decimal = Decimal("0")
    expense: Decimal = Decimal("0")


async def get_expenses_by_category(
    session: AsyncSession, user_id: int, date_from: date, date_to: date, target_currency: str
) -> list[CategoryBreakdownSchema]:
    range_from, range_to = build_datetime_range(date_from, date_to)
    items = await get_categorized_amounts(session, user_id, range_from, range_to, target_currency)
    return build_category_breakdown(items, "debit")


async def get_income_by_category(
    session: AsyncSession, user_id: int, date_from: date, date_to: date, target_currency: str
) -> list[CategoryBreakdownSchema]:
    range_from, range_to = build_datetime_range(date_from, date_to)
    items = await get_categorized_amounts(session, user_id, range_from, range_to, target_currency)
    return build_category_breakdown(items, "credit")


async def get_summary(
    session: AsyncSession, user_id: int, target_currency: str
) -> PeriodComparisonSchema:
    today = date.today()
    previous_month_date = get_previous_month_date(today)

    current_income, current_expense = await get_month_totals(session, user_id, today, target_currency)
    previous_income, previous_expense = await get_month_totals(session, user_id, previous_month_date, target_currency)

    return PeriodComparisonSchema(
        current_income=current_income,
        previous_income=previous_income,
        income_change_percentage=calculate_percentage_change(current_income, previous_income),
        current_expense=current_expense,
        previous_expense=previous_expense,
        expense_change_percentage=calculate_percentage_change(current_expense, previous_expense),
        currency=target_currency,
    )


async def get_cashflow(
    session: AsyncSession, user_id: int, target_currency: str
) -> list[CashflowWeekSchema]:
    today = date.today()
    lookback_days = DAYS_IN_CASHFLOW_MONTH * CASHFLOW_LOOKBACK_MONTHS
    range_start_date = today - timedelta(days=lookback_days)
    first_week_start = get_iso_week_start(range_start_date)

    date_from, date_to = build_datetime_range(first_week_start, today)
    items = await get_categorized_amounts(session, user_id, date_from, date_to, target_currency)

    weeks: dict[date, WeekAccumulator] = {}
    week_start = first_week_start
    while week_start <= today:
        week_end = week_start + timedelta(days=6)
        weeks[week_start] = WeekAccumulator(week_start=week_start, week_end=week_end)
        week_start += timedelta(days=7)

    for item in items:
        item_week_start = get_iso_week_start(item.transaction_date.date())

        if item_week_start not in weeks:
            continue

        accumulator = weeks[item_week_start]

        if item.operation_code == "credit":
            accumulator.income += item.amount
        elif item.operation_code == "debit":
            accumulator.expense += item.amount

    result = []
    for week_start in sorted(weeks.keys()):
        accumulator = weeks[week_start]
        week_schema = CashflowWeekSchema(
            week_start=accumulator.week_start,
            week_end=accumulator.week_end,
            income=round_money(accumulator.income),
            expense=round_money(accumulator.expense),
        )
        result.append(week_schema)

    return result


async def get_savings_rate(
    session: AsyncSession, user_id: int, target_currency: str
) -> SavingsRateSchema:
    today = date.today()
    income, expense = await get_month_totals(session, user_id, today, target_currency)

    savings = income - expense
    rate = calculate_percentage_share(savings, income)

    return SavingsRateSchema(
        income=income,
        expense=expense,
        savings_rate_percentage=rate,
        currency=target_currency,
    )


async def get_dashboard(
    session: AsyncSession, user_id: int, target_currency: str
) -> DashboardSchema:
    wallets = await repository.get_wallets_for_analytics(session, user_id)

    pairs = set()
    for wallet in wallets:
        if wallet.currency.code != target_currency:
            pairs.add((wallet.currency.code, target_currency))

    now = datetime.now(timezone.utc)
    rates_index = await repository.get_rates_batch(session, pairs, now)

    wallet_schemas = []
    total_balance = Decimal("0")

    for wallet in wallets:
        balance = await calculate_balance(session, wallet)

        wallet_schema = WalletBalanceSchema(
            wallet_id=wallet.id,
            wallet_name=wallet.name,
            wallet_currency=wallet.currency.code,
            balance=balance,
        )
        wallet_schemas.append(wallet_schema)

        rate = find_rate_for_date(rates_index, wallet.currency.code, target_currency, now)
        converted_balance = convert_amount(balance, wallet.currency.code, target_currency, rate, now)
        total_balance += converted_balance

    recent_transactions = await repository.get_recent_transactions(session, user_id, RECENT_TRANSACTIONS_LIMIT)

    recent_transaction_schemas = []
    for tx in recent_transactions:
        amount, currency = get_transaction_display_info(tx)
        transaction_schema = RecentTransactionSchema(
            transaction_id=tx.id,
            transaction_date=tx.transaction_date,
            operation_code=tx.operation_code,
            description=tx.description,
            amount=amount,
            currency=currency,
        )
        recent_transaction_schemas.append(transaction_schema)

    current_month_income, current_month_expense = await get_month_totals(session, user_id, date.today(), target_currency)

    return DashboardSchema(
        wallets=wallet_schemas,
        total_balance=round_money(total_balance),
        currency=target_currency,
        recent_transactions=recent_transaction_schemas,
        current_month_income=current_month_income,
        current_month_expense=current_month_expense,
    )