import pytest
from pydantic import ValidationError

from app.schemas import AnalysisResult


def test_analysis_result_accepts_minimal_valid_payload():
    payload = {
        "ats_match_score": 72,
        "summary": "Decent overlap on core backend skills, missing cloud experience.",
        "skill_gaps": [
            {"skill": "Python", "present_in_cv": True, "evidence": "3 years Python", "suggestion": None},
            {"skill": "AWS", "present_in_cv": False, "evidence": None, "suggestion": "Add a project using AWS."},
        ],
        "bullet_rewrites": [],
        "missing_keywords": ["AWS", "Terraform"],
    }
    result = AnalysisResult.model_validate(payload)
    assert result.ats_match_score == 72
    assert result.skill_gaps[1].present_in_cv is False


def test_ats_match_score_out_of_range_rejected():
    payload = {
        "ats_match_score": 150,
        "summary": "x",
        "skill_gaps": [],
        "bullet_rewrites": [],
        "missing_keywords": [],
    }
    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(payload)
