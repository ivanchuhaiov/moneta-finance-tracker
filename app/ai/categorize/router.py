from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.categorize.schemas import CategorizeSuggestionRequest, CategorySuggestionResponse
from app.ai.categorize.service import suggest_category
from app.ai.dependencies import get_llm_service
from app.ai.service import LLMService
from app.auth.dependencies import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/api", tags=["AI"])


@router.post("/ai/categorize/suggest", response_model=CategorySuggestionResponse)
async def categorize_suggest(
    data: CategorizeSuggestionRequest,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service),
) -> CategorySuggestionResponse:
    result = await suggest_category(
        session, llm_service, current_user.id, data.description, data.operation_code
    )
    return result