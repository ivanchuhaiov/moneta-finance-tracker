from datetime import date, datetime, timezone
from decimal import Decimal
import io

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.aggregation import get_categorized_amounts
from app.analytics.conversion import round_money, find_rate_for_date, convert_amount
from app.analytics.service import get_expenses_by_category
from app.analytics import repository as analytics_repository
from app.core.enums import AuditAction, EntityType
from app.core.log_audit_event import log_audit_event
from app.features.reports import repository as reports_repository
from app.analytics.helpers import build_datetime_range, get_transaction_display_info
from app.features.reports.builder import build_report_document
from app.features.reports.schemas import ReportTransactionItemSchema, ReportSummarySchema, ReportCategoryItemSchema, \
    ReportGenerateRequest, ReportData, ReportWalletItemSchema
from app.transaction.service import calculate_balance


async def get_report_by_wallet(
    session: AsyncSession, user_id: int, target_currency: str
) -> list[ReportWalletItemSchema]:
    wallets = await analytics_repository.get_wallets_for_analytics(session, user_id)

    pairs = set()
    for wallet in wallets:
        if wallet.currency.code != target_currency:
            pairs.add((wallet.currency.code, target_currency))

    now = datetime.now(timezone.utc)
    rates_index = await analytics_repository.get_rates_batch(session, pairs, now)

    result = []
    for wallet in wallets:
        balance = await calculate_balance(session, wallet)
        rate = find_rate_for_date(rates_index, wallet.currency.code, target_currency, now)
        converted_balance = convert_amount(balance, wallet.currency.code, target_currency, rate, now)

        result.append(ReportWalletItemSchema(
            wallet_id=wallet.id,
            wallet_name=wallet.name,
            balance=round_money(converted_balance),
            currency=target_currency,
        ))

    return result


async def get_report_transactions(
    session: AsyncSession, user_id: int, date_from: date, date_to: date
) -> list[ReportTransactionItemSchema]:
    range_from, range_to = build_datetime_range(date_from, date_to)
    transactions = await reports_repository.get_transactions_by_period(session, user_id, range_from, range_to)

    result = []
    for tx in transactions:
        amount, currency = get_transaction_display_info(tx)
        result.append(ReportTransactionItemSchema(
            transaction_id=tx.id,
            transaction_date=tx.transaction_date,
            operation_code=tx.operation_code,
            description=tx.description,
            amount=amount,
            currency=currency,
        ))

    return result

async def get_report_summary(
    session: AsyncSession, user_id: int, date_from: date, date_to: date, target_currency: str
) -> ReportSummarySchema:
    range_from, range_to = build_datetime_range(date_from, date_to)
    items = await get_categorized_amounts(session, user_id, range_from, range_to, target_currency)

    total_income = Decimal("0")
    total_expense = Decimal("0")

    for item in items:
        if item.operation_code == "credit":
            total_income += item.amount
        elif item.operation_code == "debit":
            total_expense += item.amount

    total_income = round_money(total_income)
    total_expense = round_money(total_expense)
    net = round_money(total_income - total_expense)

    return ReportSummarySchema(
        date_from=date_from,
        date_to=date_to,
        total_income=total_income,
        total_expense=total_expense,
        net=net,
        currency=target_currency,
    )

async def get_report_by_category(
    session: AsyncSession, user_id: int, date_from: date, date_to: date, target_currency: str
) -> list[ReportCategoryItemSchema]:
    expenses = await get_expenses_by_category(session, user_id, date_from, date_to, target_currency)

    result = []
    for item in expenses:
        result.append(ReportCategoryItemSchema(
            category=item.category,
            total=item.total,
            percentage=item.percentage,
        ))

    return result

async def build_report_data(
    session: AsyncSession, user_id: int, request: ReportGenerateRequest
) -> ReportData:
    summary = None
    if request.include_summary:
        summary = await get_report_summary(
            session, user_id, request.date_from, request.date_to, request.target_currency
        )

    by_category = None
    if request.include_by_category:
        by_category = await get_report_by_category(
            session, user_id, request.date_from, request.date_to, request.target_currency
        )

    by_wallet = None
    if request.include_by_wallet:
        by_wallet = await get_report_by_wallet(session, user_id, request.target_currency)

    transactions = None
    if request.include_transactions:
        transactions = await get_report_transactions(
            session, user_id, request.date_from, request.date_to
        )

    return ReportData(
        date_from=request.date_from,
        date_to=request.date_to,
        target_currency=request.target_currency,
        summary=summary,
        by_category=by_category,
        by_wallet=by_wallet,
        transactions=transactions,
    )

async def generate_report(
    session: AsyncSession, user_id: int, request: ReportGenerateRequest
) -> io.BytesIO:
    report_data = await build_report_data(session, user_id, request)
    buffer = build_report_document(report_data)

    await log_audit_event(
        session=session,
        user_id=user_id,
        action=AuditAction.CREATE,
        entity_type=EntityType.REPORT,
        entity_id=user_id,
        details={
            "date_from": request.date_from.isoformat(),
            "date_to": request.date_to.isoformat(),
            "target_currency": request.target_currency.value,
        },
    )
    await session.commit()

    return buffer