from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import LLMService
from app.ai.summary.prompts import SUMMARY_SYSTEM_PROMPT, build_summary_prompt
from app.ai.summary.schemas import SummaryResponseSchema
from app.analytics import service as analytics_service


def resolve_summary_period(date_from: date | None, date_to: date | None) -> tuple[date, date]:
    if date_from is not None and date_to is not None:
        return date_from, date_to

    today = date.today()
    month_start = today.replace(day=1)
    return month_start, today


async def generate_summary(
    session: AsyncSession,
    llm_service: LLMService,
    user_id: int,
    target_currency: str,
    date_from: date | None = None,
    date_to: date | None = None,
) -> SummaryResponseSchema:
    resolved_date_from, resolved_date_to = resolve_summary_period(date_from, date_to)

    period_comparison = await analytics_service.get_summary(
        session, user_id, target_currency, resolved_date_from, resolved_date_to
    )
    category_breakdown = await analytics_service.get_expenses_by_category(
        session, user_id, resolved_date_from, resolved_date_to, target_currency
    )
    savings_rate = await analytics_service.get_savings_rate(
        session, user_id, target_currency, resolved_date_from, resolved_date_to
    )

    human_prompt = build_summary_prompt(period_comparison, category_breakdown, savings_rate)
    summary_text = await llm_service.generate_text(human_prompt, system_prompt=SUMMARY_SYSTEM_PROMPT)

    response = SummaryResponseSchema(
        summary=summary_text,
        date_from=resolved_date_from,
        date_to=resolved_date_to,
        currency=target_currency,
    )
    return response