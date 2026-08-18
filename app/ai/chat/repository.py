from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import ChatConversation, ChatMessage


async def create_conversation(session: AsyncSession, user_id: int) -> ChatConversation:
    conversation = ChatConversation(user_id=user_id, created_at=datetime.now(timezone.utc))
    session.add(conversation)
    await session.flush()
    return conversation


async def get_conversation_by_id(session: AsyncSession, conversation_id: int, user_id: int) -> ChatConversation:
    result = await session.execute(
        select(ChatConversation).where(ChatConversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    if conversation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your conversation")

    return conversation


async def get_messages_by_conversation(session: AsyncSession, conversation_id: int) -> list[ChatMessage]:
    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return list(result.scalars().all())


async def save_message(session: AsyncSession, conversation_id: int, role: str, content: str) -> ChatMessage:
    message = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=datetime.now(timezone.utc),
    )
    session.add(message)
    await session.flush()
    return message