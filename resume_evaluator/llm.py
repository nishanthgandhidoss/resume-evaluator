"""LLM client and structured completion utilities."""

import json
from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from resume_evaluator.config import get_openai_api_key

T = TypeVar("T", bound=BaseModel)

# Singleton OpenAI client
_client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    """
    Get or create singleton OpenAI client.

    Returns:
        OpenAI client instance.
    """
    global _client
    if _client is None:
        api_key = get_openai_api_key()
        _client = OpenAI(api_key=api_key)
    return _client


def structured_completion(
    schema_model: Type[T],
    system_prompt: str,
    user_content: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> T:
    """
    Get structured completion from OpenAI with Pydantic validation.

    Args:
        schema_model: Pydantic model class to validate response against.
        system_prompt: System prompt for the LLM.
        user_content: User content/message.
        model: OpenAI model to use (default: gpt-4o-mini).
        temperature: Temperature for generation (default: 0.2).

    Returns:
        Validated Pydantic model instance.

    Raises:
        ValueError: If JSON parsing or validation fails.
        Exception: On API errors after retries.
    """
    client = get_openai_client()

    # Get JSON schema from Pydantic model
    json_schema = schema_model.model_json_schema()

    # Enhance system prompt with schema information
    enhanced_system_prompt = f"""{system_prompt}

You must respond with a valid JSON object that matches this exact schema:
{json.dumps(json_schema, indent=2)}

Ensure all required fields are present and all values match the schema types and constraints."""

    @retry(
        retry=retry_if_exception_type((ValueError, json.JSONDecodeError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def _call_api() -> T:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API")

            # Parse JSON
            try:
                json_data = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Failed to parse JSON response: {e}. Response: {content[:500]}"
                ) from e

            # Validate with Pydantic
            try:
                return schema_model.model_validate(json_data)
            except ValidationError as e:
                raise ValueError(
                    f"Pydantic validation failed: {e}. JSON data: {json.dumps(json_data, indent=2)[:1000]}"
                ) from e

        except Exception as e:
            if isinstance(e, (ValueError, json.JSONDecodeError)):
                raise
            # Retry on transient errors
            raise ValueError(f"OpenAI API error: {e}") from e

    return _call_api()
