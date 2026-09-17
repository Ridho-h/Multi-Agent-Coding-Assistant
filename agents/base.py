import os
import logging
import warnings
from typing import Any, Type, Optional

from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
from pydantic import BaseModel
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
)

# Suppress the AFC informational warning — we are not using function calling
warnings.filterwarnings(
    "ignore",
    message=".*automatic function calling.*",
    category=UserWarning,
)

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize the Gemini client
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your_gemini_api_key_here":
    raise ValueError(
        "GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key."
    )

client = genai.Client(api_key=api_key)

# Default model: gemini-3.5-flash-lite (lightweight, free-tier friendly).
# Override via GEMINI_MODEL environment variable.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def _is_retryable(exc: BaseException) -> bool:
    """Return True for transient API errors that are safe to retry."""
    if isinstance(exc, ServerError):          # 503 overloaded
        return True
    if isinstance(exc, ClientError) and "429" in str(exc):  # 429 rate-limited
        return True
    return False


@retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=2, min=10, max=90),
    stop=stop_after_attempt(8),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_llm(
    system_prompt: str,
    user_prompt: str,
    response_schema: Optional[Type[BaseModel]] = None,
    temperature: float = 0.2,
) -> Any:
    """
    Call the Gemini LLM with automatic retry on transient errors (503 / 429).

    Args:
        system_prompt: The system instruction for the model.
        user_prompt: The user turn content.
        response_schema: Optional Pydantic model for structured JSON output.
        temperature: Sampling temperature (default 0.2 for deterministic output).

    Returns:
        Parsed Pydantic model instance if response_schema is given, else str.
    """
    config_kwargs: dict = {
        "temperature": temperature,
        "system_instruction": system_prompt,
    }

    if response_schema:
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = response_schema

    config = types.GenerateContentConfig(**config_kwargs)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_prompt,
        config=config,
    )

    if response_schema:
        return response_schema.model_validate_json(response.text)

    return response.text
