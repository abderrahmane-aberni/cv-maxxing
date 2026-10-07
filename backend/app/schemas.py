"""Pydantic schemas. AnalysisResult is the structured-output contract
between the LLM and the API — it's also handed to Gemini directly as
`response_schema`, so the prompt's description of the schema (in
prompts/v1_system_prompt.md) and this class must be kept in sync by hand."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SkillGap(BaseModel):
    skill: str = Field(..., description="A skill or requirement named in the job description.")
    present_in_cv: bool = Field(..., description="Whether the CV provides evidence of this skill.")
    evidence: Optional[str] = Field(
        None, description="Short quote/paraphrase from the CV if present_in_cv is true."
    )
    suggestion: Optional[str] = Field(
        None, description="If missing, a concrete suggestion for closing the gap."
    )


class BulletRewrite(BaseModel):
    original: str = Field(..., description="An existing bullet point from the CV.")
    rewritten: str = Field(..., description="A rewritten version using stronger, JD-aligned language.")
    rationale: str = Field(..., description="One sentence on why the rewrite is stronger.")


class AnalysisResult(BaseModel):
    ats_match_score: int = Field(
        ..., ge=0, le=100, description="0-100 keyword/requirement match score against the JD."
    )
    summary: str = Field(..., description="2-3 sentence overview of fit for this role.")
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    bullet_rewrites: List[BulletRewrite] = Field(default_factory=list)
    missing_keywords: List[str] = Field(
        default_factory=list, description="JD keywords not found anywhere in the CV."
    )


class UsageInfo(BaseModel):
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    model: str


class AnalyzeResponse(BaseModel):
    id: int
    created_at: datetime
    result: AnalysisResult
    usage: UsageInfo


class HistoryItem(BaseModel):
    id: int
    created_at: datetime
    cv_filename: str
    job_title_snippet: str
    ats_match_score: int
    model: str


class HistoryListResponse(BaseModel):
    items: List[HistoryItem]
