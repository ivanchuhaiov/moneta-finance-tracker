from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, create_model
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.categorize.prompts import CATEGORIZE_SYSTEM_PROMPT, build_categorize_prompt
from app.ai.categorize.schemas import CategorySuggestionResponse
from app.ai.service import LLMService
from app.models import CreditType, DebitType
from app.transaction.service import get_credit_types_by_user, get_debit_types_by_user


def build_category_output_schema(categories: list[CreditType] | list[DebitType]) -> type[BaseModel]:
    codes = []
    for category_item in categories:
        codes.append(category_item.code)

    codes_literal = Literal[tuple(codes)]

    dynamic_schema = create_model(
        "CategorySelection",
        category_code=(codes_literal, ...),
    )
    return dynamic_schema


async def suggest_category(
    session: AsyncSession,
    llm_service: LLMService,
    user_id: int,
    description: str,
    operation_code: str,
) -> CategorySuggestionResponse:
    if operation_code == "credit":
        categories = await get_credit_types_by_user(session, user_id)
    else:
        categories = await get_debit_types_by_user(session, user_id)

    if len(categories) == 0:
        raise HTTPException(status_code=400, detail="No categories found for this user")

    output_schema = build_category_output_schema(categories)
    prompt = build_categorize_prompt(description, categories)

    result = await llm_service.generate_structured(
        prompt, output_schema=output_schema, system_prompt=CATEGORIZE_SYSTEM_PROMPT
    )

    selected_code = result.category_code

    category_name = ""
    for category_item in categories:
        if category_item.code == selected_code:
            category_name = category_item.name
            break

    response = CategorySuggestionResponse(category_code=selected_code, category_name=category_name)
    return response