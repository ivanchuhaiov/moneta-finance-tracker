from abc import ABC, abstractmethod

import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMServiceError,
    LLMTimeoutError,
)
from app.core.config import settings


class LLMService(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        raise NotImplementedError


class AnthropicLLMService(LLMService):
    def __init__(self) -> None:
        self._client = ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            max_tokens=settings.anthropic_max_tokens,
            temperature=settings.anthropic_temperature,
        )

    async def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt is not None:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        try:
            response = await self._client.ainvoke(messages)
        except anthropic.RateLimitError as e:
            raise LLMRateLimitError("Anthropic API rate limit exceeded") from e
        except anthropic.AuthenticationError as e:
            raise LLMAuthenticationError("Invalid Anthropic API key") from e
        except anthropic.APITimeoutError as e:
            raise LLMTimeoutError("Anthropic API request timed out") from e
        except anthropic.APIConnectionError as e:
            raise LLMConnectionError("Could not connect to Anthropic API") from e
        except anthropic.APIError as e:
            raise LLMServiceError(f"Anthropic API error: {e}") from e

        return response.content