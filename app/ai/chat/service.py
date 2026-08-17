import json

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chat import repository
from app.ai.chat.prompts import build_chat_system_prompt
from app.ai.chat.tools import build_analytics_tools
from app.ai.service import LLMService
from app.models import ChatMessage


MAX_TOOL_CALL_ITERATIONS = 5


def convert_to_langchain_messages(messages: list[ChatMessage]) -> list[BaseMessage]:
    langchain_messages = []
    for message_item in messages:
        if message_item.role == "user":
            langchain_messages.append(HumanMessage(content=message_item.content))
        else:
            langchain_messages.append(AIMessage(content=message_item.content))

    return langchain_messages


async def run_tool_calling_loop(
    session: AsyncSession,
    llm_service: LLMService,
    user_id: int,
    currency: str,
    langchain_messages: list[BaseMessage],
) -> str:
    tools = build_analytics_tools(session, user_id, currency)

    tools_by_name = {}
    for tool_item in tools:
        tools_by_name[tool_item.name] = tool_item

    system_prompt = build_chat_system_prompt()

    for iteration in range(MAX_TOOL_CALL_ITERATIONS):
        response = await llm_service.generate_with_tools(langchain_messages, tools, system_prompt=system_prompt)

        if not response.tool_calls:
            return response.content

        langchain_messages.append(response)

        for tool_call in response.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            tool_result = await tool.ainvoke(tool_call["args"])

            tool_message = ToolMessage(
                content=json.dumps(tool_result, default=str),
                tool_call_id=tool_call["id"],
            )
            langchain_messages.append(tool_message)

    return "I could not complete the analysis, please try rephrasing your question."


async def send_chat_message(
    session: AsyncSession,
    llm_service: LLMService,
    user_id: int,
    currency: str,
    conversation_id: int | None,
    message: str,
) -> tuple[int, str]:
    if conversation_id is None:
        conversation = await repository.create_conversation(session, user_id)
        resolved_conversation_id = conversation.id
        history = []
    else:
        conversation = await repository.get_conversation_by_id(session, conversation_id, user_id)
        resolved_conversation_id = conversation.id
        history = await repository.get_messages_by_conversation(session, resolved_conversation_id)

    await repository.save_message(session, resolved_conversation_id, "user", message)

    langchain_messages = convert_to_langchain_messages(history)
    langchain_messages.append(HumanMessage(content=message))

    reply = await run_tool_calling_loop(session, llm_service, user_id, currency, langchain_messages)

    await repository.save_message(session, resolved_conversation_id, "assistant", reply)

    await session.commit()

    return resolved_conversation_id, reply


async def get_conversation_history(
    session: AsyncSession, user_id: int, conversation_id: int
) -> list[ChatMessage]:
    await repository.get_conversation_by_id(session, conversation_id, user_id)
    return await repository.get_messages_by_conversation(session, conversation_id)