"""Loads and formats the system prompt from the versioned files in the
repo's top-level /prompts folder (see prompts/CHANGELOG.md for why each
version changed). Keeping prompt text out of the Python source makes it
easy to diff prompt changes independently of code changes."""
from __future__ import annotations

from pathlib import Path

PROMPT_VERSION = "v1"

_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def _load_system_prompt() -> str:
    path = _PROMPTS_DIR / f"{PROMPT_VERSION}_system_prompt.md"
    return path.read_text(encoding="utf-8")


def build_contents(cv_text: str, job_description: str) -> str:
    """Builds the single user-turn prompt sent to Gemini: the versioned
    system prompt (schema + instructions) plus the specific CV/JD pair."""
    system_prompt = _load_system_prompt()
    return (
        f"{system_prompt}\n\n"
        "--- CANDIDATE CV (extracted text) ---\n"
        f"{cv_text.strip()}\n\n"
        "--- JOB DESCRIPTION ---\n"
        f"{job_description.strip()}\n"
    )
