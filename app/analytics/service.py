from datetime import date, datetime, timezone
from decimal import Decimal
from calendar import monthrange
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.models import (
    TransactionHistory, CreditOperation, DebitOperation,
    CreditType, DebitType, Wallet, Currency, ExchangeRate,
)
from app.analytics.schemas import (
    SummarySchema, CategoryBreakdownSchema, WalletSummarySchema, TrendPointSchema,
)


def get_period_range(period: str, target_date: date) -> tuple[datetime, datetime]:
    if period == "month":
        year, month = target_date.year, target_date.month
        days_in_month = monthrange(year, month)[1]

        date_from = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        date_to = datetime(year, month, days_in_month, 23, 59, 59, tzinfo=timezone.utc)

        return date_from, date_to

    raise ValueError(f"Unsupported period: {period}")


async def get_transactions_for_period(
    session: AsyncSession, user_id: int, date_from: datetime, date_to: datetime
) -> list[dict]:
    FromWallet = aliased(Wallet)
    ToWallet = aliased(Wallet)
    FromCurrency = aliased(Currency)
    ToCurrency = aliased(Currency)

    stmt = (
        select(
            TransactionHistory.operation_code,
            TransactionHistory.transaction_date,
            TransactionHistory.from_amount,
            TransactionHistory.to_amount,
            TransactionHistory.from_wallet_id,
            TransactionHistory.to_wallet_id,
            FromWallet.name.label("from_wallet_name"),
            ToWallet.name.label("to_wallet_name"),
            FromCurrency.code.label("from_currency"),
            ToCurrency.code.label("to_currency"),
            CreditType.name.label("credit_category"),
            DebitType.name.label("debit_category"),
        )
        .outerjoin(CreditOperation, TransactionHistory.credit_operation_id == CreditOperation.id)
        .outerjoin(CreditType, CreditOperation.credit_type_id == CreditType.id)
        .outerjoin(DebitOperation, TransactionHistory.debit_operation_id == DebitOperation.id)
        .outerjoin(DebitType, DebitOperation.debit_type_id == DebitType.id)
        .outerjoin(FromWallet, TransactionHistory.from_wallet_id == FromWallet.id)
        .outerjoin(ToWallet, TransactionHistory.to_wallet_id == ToWallet.id)
        .outerjoin(FromCurrency, FromWallet.currency_id == FromCurrency.id)
        .outerjoin(ToCurrency, ToWallet.currency_id == ToCurrency.id)
        .where(
            TransactionHistory.user_id == user_id,
            TransactionHistory.transaction_date >= date_from,
            TransactionHistory.transaction_date <= date_to,
        )
    )

    result = await session.execute(stmt)
    rows = result.all()

    transactions = []
    for row in rows:
        if row.operation_code == "credit":
            amount = row.from_amount
            currency = row.to_currency
            category = row.credit_category or "Без категории"
        elif row.operation_code == "debit":
            amount = row.from_amount
            currency = row.from_currency
            category = row.debit_category or "Без категории"
        else:  # transfer
            amount = None
            currency = None
            category = None

        transactions.append({
            "operation_code": row.operation_code,
            "transaction_date": row.transaction_date,
            "amount": amount,
            "currency": currency,
            "category": category,
            "from_wallet_id": row.from_wallet_id,
            "to_wallet_id": row.to_wallet_id,
            "from_wallet_name": row.from_wallet_name,
            "to_wallet_name": row.to_wallet_name,
            "from_amount": row.from_amount,
            "to_amount": row.to_amount,
            "from_currency": row.from_currency,
            "to_currency": row.to_currency,
        })

    return transactions


async def get_rates_batch(
    session: AsyncSession, pairs: set[tuple[str, str]], date_to: datetime
) -> dict[tuple[str, str], list[tuple[datetime, Decimal]]]:
    if not pairs:
        return {}

    conditions = [
        (ExchangeRate.base_currency == base) & (ExchangeRate.target_currency == target)
        for base, target in pairs
    ]
    from sqlalchemy import or_

    stmt = (
        select(ExchangeRate.base_currency, ExchangeRate.target_currency, ExchangeRate.rate, ExchangeRate.fetched_at)
        .where(or_(*conditions), ExchangeRate.fetched_at <= date_to)
        .order_by(ExchangeRate.fetched_at.asc())
    )

    result = await session.execute(stmt)
    rows = result.all()

    rates_index: dict[tuple[str, str], list[tuple[datetime, Decimal]]] = defaultdict(list)
    for row in rows:
        key = (row.base_currency, row.target_currency)
        rates_index[key].append((row.fetched_at, row.rate))

    return rates_index


def find_rate_for_date(
    rates_index: dict, base: str, target: str, target_date: datetime
) -> Decimal | None:
    entries = rates_index.get((base, target))
    if not entries:
        return None

    matching_rate = None
    for fetched_at, rate in entries:
        if fetched_at <= target_date:
            matching_rate = rate
        else:
            break

    return matching_rate


def convert_amount(
    amount: Decimal, from_currency: str, to_currency: str, rate: Decimal | None
) -> Decimal:
    if from_currency == to_currency:
        return amount
    if rate is None:
        return Decimal("0")
    return (amount * rate).quantize(Decimal("0.01"))


async def get_summary(
    session: AsyncSession, user_id: int, period: str, target_date: date, target_currency: str
) -> SummarySchema:
    date_from, date_to = get_period_range(period, target_date)
    transactions = await get_transactions_for_period(session, user_id, date_from, date_to)

    relevant = [t for t in transactions if t["operation_code"] != "transfer"]

    pairs = {(t["currency"], target_currency) for t in relevant if t["currency"] != target_currency}
    rates_index = await get_rates_batch(session, pairs, date_to)

    total_income = Decimal("0")
    total_expense = Decimal("0")

    for t in relevant:
        rate = find_rate_for_date(rates_index, t["currency"], target_currency, t["transaction_date"])
        converted = convert_amount(t["amount"], t["currency"], target_currency, rate)

        if t["operation_code"] == "credit":
            total_income += converted
        else:
            total_expense += converted

    return SummarySchema(
        total_income=total_income,
        total_expense=total_expense,
        net=total_income - total_expense,
        currency=target_currency,
    )


async def get_by_category(
    session: AsyncSession, user_id: int, period: str, target_date: date, target_currency: str
) -> list[CategoryBreakdownSchema]:
    date_from, date_to = get_period_range(period, target_date)
    transactions = await get_transactions_for_period(session, user_id, date_from, date_to)

    relevant = [t for t in transactions if t["operation_code"] != "transfer"]

    pairs = {(t["currency"], target_currency) for t in relevant if t["currency"] != target_currency}
    rates_index = await get_rates_batch(session, pairs, date_to)

    totals: dict[tuple[str, str], Decimal] = defaultdict(lambda: Decimal("0"))

    for t in relevant:
        rate = find_rate_for_date(rates_index, t["currency"], target_currency, t["transaction_date"])
        converted = convert_amount(t["amount"], t["currency"], target_currency, rate)

        type_label = "income" if t["operation_code"] == "credit" else "expense"
        key = (t["category"], type_label)
        totals[key] += converted

    return [
        CategoryBreakdownSchema(category=category, total=total, type=type_label)
        for (category, type_label), total in totals.items()
    ]


async def get_by_wallet(session, user_id, period, target_date, target_currency):
    date_from, date_to = get_period_range(period, target_date)
    transactions = await get_transactions_for_period(session, user_id, date_from, date_to)

    # Новый шаг: подтягиваем ВСЕ кошельки юзера заранее
    wallets_result = await session.execute(
        select(Wallet).options(selectinload(Wallet.currency)).where(Wallet.user_id == user_id)
    )
    all_wallets = wallets_result.scalars().all()

    wallet_totals = {
        w.id: {
            "wallet_name": w.name,
            "wallet_currency": w.currency.code,
            "total_in_wallet_currency": Decimal("0"),
            "total_in_target_currency": Decimal("0"),
        }
        for w in all_wallets
    }
    def ensure_wallet(wallet_id: int, wallet_name: str, wallet_currency: str):
        if wallet_id not in wallet_totals:
            wallet_totals[wallet_id] = {
                "wallet_name": wallet_name,
                "wallet_currency": wallet_currency,
                "total_in_wallet_currency": Decimal("0"),
                "total_in_target_currency": Decimal("0"),
            }

    pairs = set()
    for t in transactions:
        if t["from_currency"] and t["from_currency"] != target_currency:
            pairs.add((t["from_currency"], target_currency))
        if t["to_currency"] and t["to_currency"] != target_currency:
            pairs.add((t["to_currency"], target_currency))

    rates_index = await get_rates_batch(session, pairs, date_to)

    for t in transactions:
        if t["operation_code"] == "credit":
            ensure_wallet(t["to_wallet_id"], t["to_wallet_name"], t["to_currency"])
            wallet_totals[t["to_wallet_id"]]["total_in_wallet_currency"] += t["from_amount"]
            rate = find_rate_for_date(rates_index, t["to_currency"], target_currency, t["transaction_date"])
            converted = convert_amount(t["from_amount"], t["to_currency"], target_currency, rate)
            wallet_totals[t["to_wallet_id"]]["total_in_target_currency"] += converted

        elif t["operation_code"] == "debit":
            ensure_wallet(t["from_wallet_id"], t["from_wallet_name"], t["from_currency"])
            wallet_totals[t["from_wallet_id"]]["total_in_wallet_currency"] -= t["from_amount"]
            rate = find_rate_for_date(rates_index, t["from_currency"], target_currency, t["transaction_date"])
            converted = convert_amount(t["from_amount"], t["from_currency"], target_currency, rate)
            wallet_totals[t["from_wallet_id"]]["total_in_target_currency"] -= converted

        else:  # transfer
            ensure_wallet(t["from_wallet_id"], t["from_wallet_name"], t["from_currency"])
            ensure_wallet(t["to_wallet_id"], t["to_wallet_name"], t["to_currency"])

            wallet_totals[t["from_wallet_id"]]["total_in_wallet_currency"] -= t["from_amount"]
            rate_from = find_rate_for_date(rates_index, t["from_currency"], target_currency, t["transaction_date"])
            converted_from = convert_amount(t["from_amount"], t["from_currency"], target_currency, rate_from)
            wallet_totals[t["from_wallet_id"]]["total_in_target_currency"] -= converted_from

            wallet_totals[t["to_wallet_id"]]["total_in_wallet_currency"] += t["to_amount"]
            rate_to = find_rate_for_date(rates_index, t["to_currency"], target_currency, t["transaction_date"])
            converted_to = convert_amount(t["to_amount"], t["to_currency"], target_currency, rate_to)
            wallet_totals[t["to_wallet_id"]]["total_in_target_currency"] += converted_to

    return [
        WalletSummarySchema(
            wallet_id=wallet_id,
            wallet_name=data["wallet_name"],
            wallet_currency=data["wallet_currency"],
            total_in_wallet_currency=data["total_in_wallet_currency"],
            total_in_target_currency=data["total_in_target_currency"],
        )
        for wallet_id, data in wallet_totals.items()
    ]


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

        points.append(TrendPointSchema(
            period=f"{year}-{month:02d}",
            income=summary.total_income,
            expense=summary.total_expense,
            net=summary.net,
        ))

    return points