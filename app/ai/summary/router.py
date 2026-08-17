from datetime import date
from fastapi import APIRouter, Depends

from app.ai.dependencies import get_llm_service
from app.ai.service import LLMService
from app.ai.summary.schemas import SummaryResponseSchema
from app.ai.summary.service import generate_summary
from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.core.enums import CurrencyCode

router = APIRouter(prefix="/api", tags=["AI"])


@router.get("/ai/summary", response_model=SummaryResponseSchema)
async def get_ai_summary(
    currency: CurrencyCode = CurrencyCode.EUR,
    date_from: date | None = None,
    date_to: date | None = None,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service),
) -> SummaryResponseSchema:
    result = await generate_summary(
        session, llm_service, current_user.id, currency.value, date_from, date_to
    )
    return result