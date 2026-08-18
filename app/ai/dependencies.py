from functools import lru_cache

from app.ai.service import AnthropicLLMService, LLMService


@lru_cache
def get_llm_service() -> LLMService:
    return AnthropicLLMService()