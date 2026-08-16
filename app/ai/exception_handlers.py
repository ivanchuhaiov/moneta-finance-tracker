from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.ai.exceptions import (
    LLMRateLimitError,
    LLMServiceError,
    LLMTimeoutError,
)


def register_ai_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LLMRateLimitError)
    async def llm_rate_limit_handler(request: Request, exc: LLMRateLimitError) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests to AI service, please try again later"},
        )

    @app.exception_handler(LLMTimeoutError)
    async def llm_timeout_handler(request: Request, exc: LLMTimeoutError) -> JSONResponse:
        return JSONResponse(
            status_code=504,
            content={"detail": "AI service did not respond in time, please try again"},
        )

    @app.exception_handler(LLMServiceError)
    async def llm_service_error_handler(request: Request, exc: LLMServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": "AI service is temporarily unavailable"},
        )
