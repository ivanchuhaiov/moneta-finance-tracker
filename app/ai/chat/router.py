from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chat.schemas import ChatMessageResponse, ChatRequest, ChatResponse
from app.ai.chat.service import get_conversation_history, send_chat_message
from app.ai.dependencies import get_llm_service
from app.ai.service import LLMService
from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.core.enums import CurrencyCode

router = APIRouter(prefix="/api", tags=["AI"])


@router.post("/ai/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    currency: CurrencyCode = CurrencyCode.EUR,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service),
) -> ChatResponse:
    conversation_id, reply = await send_chat_message(
        session, llm_service, current_user.id, currency.value, data.conversation_id, data.message
    )
    return ChatResponse(conversation_id=conversation_id, reply=reply)


@router.get("/ai/chat/{conversation_id}/messages", response_model=list[ChatMessageResponse])
async def get_chat_messages(
    conversation_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ChatMessageResponse]:
    messages = await get_conversation_history(session, current_user.id, conversation_id)
    return messages