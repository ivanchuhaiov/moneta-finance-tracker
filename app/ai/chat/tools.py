from datetime import date
from decimal import Decimal

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import service as analytics_service


class DateRangeArgs(BaseModel):
    date_from: date | None = Field(
        default=None, description="Start date of the period in YYYY-MM-DD format. Omit for the current month."
    )
    date_to: date | None = Field(
        default=None, description="End date of the period in YYYY-MM-DD format. Omit for the current month."
    )


def build_analytics_tools(session: AsyncSession, user_id: int, currency: str) -> list[StructuredTool]:
    async def get_summary_tool(date_from: date | None = None, date_to: date | None = None) -> dict:
        result = await analytics_service.get_summary(session, user_id, currency, date_from, date_to)
        return result.model_dump(mode="json")

    async def get_expenses_by_category_tool(date_from: date | None = None, date_to: date | None = None) -> dict:
        resolved_date_from = date_from
        resolved_date_to = date_to
        if resolved_date_from is None or resolved_date_to is None:
            today = date.today()
            resolved_date_from = today.replace(day=1)
            resolved_date_to = today

        result = await analytics_service.get_expenses_by_category(
            session, user_id, resolved_date_from, resolved_date_to, currency
        )
        items = []
        for item in result:
            items.append(item.model_dump(mode="json"))
        return {"expenses_by_category": items}

    async def get_income_by_category_tool(date_from: date | None = None, date_to: date | None = None) -> dict:
        resolved_date_from = date_from
        resolved_date_to = date_to
        if resolved_date_from is None or resolved_date_to is None:
            today = date.today()
            resolved_date_from = today.replace(day=1)
            resolved_date_to = today

        result = await analytics_service.get_income_by_category(
            session, user_id, resolved_date_from, resolved_date_to, currency
        )
        items = []
        for item in result:
            items.append(item.model_dump(mode="json"))
        return {"income_by_category": items}

    async def get_savings_rate_tool(date_from: date | None = None, date_to: date | None = None) -> dict:
        result = await analytics_service.get_savings_rate(session, user_id, currency, date_from, date_to)
        return result.model_dump(mode="json")

    tools = [
        StructuredTool.from_function(
            coroutine=get_summary_tool,
            name="get_summary",
            description=(
                "Get total income and expenses for a period, compared to the previous period "
                "of the same length, with percentage change. Use this for questions about "
                "overall income/expense trends."
            ),
            args_schema=DateRangeArgs,
        ),
        StructuredTool.from_function(
            coroutine=get_expenses_by_category_tool,
            name="get_expenses_by_category",
            description=(
                "Get a breakdown of expenses by category for a period, with amount and percentage "
                "share per category. Use this for questions about what money was spent on."
            ),
            args_schema=DateRangeArgs,
        ),
        StructuredTool.from_function(
            coroutine=get_income_by_category_tool,
            name="get_income_by_category",
            description=(
                "Get a breakdown of income by category for a period, with amount and percentage "
                "share per category. Use this for questions about income sources."
            ),
            args_schema=DateRangeArgs,
        ),
        StructuredTool.from_function(
            coroutine=get_savings_rate_tool,
            name="get_savings_rate",
            description=(
                "Get income, expense and savings rate percentage for a period. "
                "Use this for questions about how much the user is saving."
            ),
            args_schema=DateRangeArgs,
        ),
    ]
    return tools