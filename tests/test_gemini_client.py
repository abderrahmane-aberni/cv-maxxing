"""Tests gemini_client's retry-on-invalid-JSON logic without making a real
API call — the Gemini client is mocked."""
from unittest.mock import MagicMock, patch

import pytest

from app.gemini_client import GeminiOutputError, analyze

VALID_JSON = (
    '{"ats_match_score": 80, "summary": "Good fit.", "skill_gaps": [], '
    '"bullet_rewrites": [], "missing_keywords": []}'
)
INVALID_JSON = "not json at all"


def _mock_response(text: str):
    response = MagicMock()
    response.text = text
    response.usage_metadata = MagicMock(prompt_token_count=100, candidates_token_count=50)
    return response


@patch("app.gemini_client._get_client")
def test_analyze_returns_result_on_first_valid_response(mock_get_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_response(VALID_JSON)
    mock_get_client.return_value = mock_client

    result, usage = analyze("some cv text here", "some job description here")

    assert result.ats_match_score == 80
    assert usage.input_tokens == 100
    assert usage.output_tokens == 50
    assert mock_client.models.generate_content.call_count == 1


@patch("app.gemini_client._get_client")
def test_analyze_retries_once_then_succeeds(mock_get_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        _mock_response(INVALID_JSON),
        _mock_response(VALID_JSON),
    ]
    mock_get_client.return_value = mock_client

    result, _ = analyze("cv text", "jd text")

    assert result.ats_match_score == 80
    assert mock_client.models.generate_content.call_count == 2


@patch("app.gemini_client._get_client")
def test_analyze_raises_after_two_failed_attempts(mock_get_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_response(INVALID_JSON)
    mock_get_client.return_value = mock_client

    with pytest.raises(GeminiOutputError):
        analyze("cv text", "jd text")
