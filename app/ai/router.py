from fastapi import APIRouter, Depends

from app.ai.dependencies import get_llm_service
from app.ai.service import LLMService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/test")
async def test_llm(
    prompt: str,
    llm_service: LLMService = Depends(get_llm_service),
) -> dict[str, str]:
    response_text = await llm_service.generate_text(prompt)
    return {"response": response_text}