"""Thin wrapper around the Gemini API: builds the prompt, requests
schema-constrained JSON output, retries once on invalid output, and
reports token usage for the per-request cost tracker."""
from __future__ import annotations

import logging
from typing import Optional, Tuple

from google import genai
from google.genai import types

from .config import get_settings
from .prompts import build_contents
from .schemas import AnalysisResult, UsageInfo

logger = logging.getLogger(__name__)


class GeminiOutputError(RuntimeError):
    """Raised when Gemini could not produce output matching AnalysisResult,
    even after one retry."""


def _get_client() -> genai.Client:
    settings = get_settings()
    settings.validate()
    return genai.Client(api_key=settings.gemini_api_key)


def analyze(cv_text: str, job_description: str) -> Tuple[AnalysisResult, UsageInfo]:
    settings = get_settings()
    client = _get_client()
    contents = build_contents(cv_text, job_description)

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=AnalysisResult,
        temperature=0.2,
    )

    last_error: Optional[Exception] = None
    for attempt in range(2):  # one retry if the model returns invalid JSON
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=config,
            )
            result = AnalysisResult.model_validate_json(response.text)
            usage = _usage_from_response(response, settings)
            return result, usage
        except Exception as exc:  # noqa: BLE001 - deliberately broad: any
            # failure here (bad JSON, schema mismatch, network hiccup) gets
            # one retry with a stricter instruction before we give up.
            last_error = exc
            logger.warning("Gemini attempt %s failed: %s", attempt + 1, exc)
            contents += (
                "\n\nYour previous response was not valid JSON matching the "
                "required schema. Return ONLY the JSON object, with no "
                "markdown fences or commentary."
            )

    raise GeminiOutputError(
        f"Gemini did not return valid structured output after 2 attempts: {last_error}"
    )


def _usage_from_response(response, settings) -> UsageInfo:
    usage_meta = getattr(response, "usage_metadata", None)
    input_tokens = getattr(usage_meta, "prompt_token_count", 0) or 0
    output_tokens = getattr(usage_meta, "candidates_token_count", 0) or 0
    cost = (
        input_tokens / 1000 * settings.cost_per_1k_input_tokens
        + output_tokens / 1000 * settings.cost_per_1k_output_tokens
    )
    return UsageInfo(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=round(cost, 6),
        model=settings.gemini_model,
    )
