class LLMServiceError(Exception):
    """Base exception for LLM service errors."""


class LLMRateLimitError(LLMServiceError):
    """Raised when the LLM API rate limit is exceeded."""


class LLMTimeoutError(LLMServiceError):
    """Raised when the LLM API request times out."""


class LLMConnectionError(LLMServiceError):
    """Raised when the LLM API is unreachable."""


class LLMAuthenticationError(LLMServiceError):
    """Raised when the LLM API key is invalid or missing."""