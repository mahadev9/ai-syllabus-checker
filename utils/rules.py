"""
Rule-based detection engine.
Each "section" has a list of keyword signals and a weight for scoring.
No LLM needed — fast and free.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class SectionResult:
    key: str
    label: str
    found: bool
    matched_keywords: List[str] = field(default_factory=list)
    weight: int = 10  # contribution to AI-readiness score


# ---------------------------------------------------------------------------
# Section definitions
# ---------------------------------------------------------------------------

SECTIONS: list[dict] = [
    {
        "key": "ai_policy",
        "label": "AI / Generative AI Policy",
        "weight": 20,
        "keywords": [
            "artificial intelligence",
            "generative ai",
            "chatgpt",
            "gpt",
            "large language model",
            "llm",
            "ai tools",
            "ai-generated",
            "ai assistance",
            "copilot",
            "bard",
            "gemini",
            "claude",
        ],
    },
    {
        "key": "academic_integrity",
        "label": "Academic Integrity",
        "weight": 15,
        "keywords": [
            "academic integrity",
            "academic honesty",
            "plagiarism",
            "cheating",
            "honor code",
            "misconduct",
            "dishonesty",
        ],
    },
    {
        "key": "accessibility",
        "label": "Accessibility / Disability Accommodations",
        "weight": 15,
        "keywords": [
            "accessibility",
            "accommodation",
            "accommodations",
            "disability",
            "disabilities",
            "disability services",
            "ada",
            "section 504",
            "student support services",
            "dss",
        ],
    },
    {
        "key": "grading",
        "label": "Grading Policy",
        "weight": 15,
        "keywords": [
            "grading",
            "grade",
            "rubric",
            "points",
            "percentage",
            "final grade",
            "grading scale",
            "assessment",
            "evaluation",
        ],
    },
    {
        "key": "late_work",
        "label": "Late Work Policy",
        "weight": 10,
        "keywords": [
            "late work",
            "late assignment",
            "late submission",
            "late penalty",
            "extensions",
            "makeup",
            "make-up",
            "missed assignment",
        ],
    },
    {
        "key": "contact_info",
        "label": "Instructor Contact Information",
        "weight": 10,
        "keywords": [
            "office hours",
            "email",
            "contact",
            "reach me",
            "phone",
            "zoom",
            "teams",
            "canvas message",
        ],
    },
    {
        "key": "support_resources",
        "label": "Student Support Resources",
        "weight": 10,
        "keywords": [
            "tutoring",
            "writing center",
            "counseling",
            "mental health",
            "financial aid",
            "food pantry",
            "student services",
            "advising",
            "support",
        ],
    },
    {
        "key": "attendance",
        "label": "Attendance Policy",
        "weight": 5,
        "keywords": [
            "attendance",
            "absences",
            "absent",
            "participation",
            "present",
        ],
    },
]


def analyze(text: str) -> list[SectionResult]:
    """
    Run all rule checks against `text` and return a list of SectionResult.
    """
    lower = text.lower()
    results: list[SectionResult] = []

    for section in SECTIONS:
        matched = [kw for kw in section["keywords"] if kw in lower]
        results.append(
            SectionResult(
                key=section["key"],
                label=section["label"],
                found=bool(matched),
                matched_keywords=matched,
                weight=section["weight"],
            )
        )

    return results


def compute_score(results: list[SectionResult]) -> int:
    """
    Return an integer 0-100 representing overall policy completeness.
    Weight of found sections / total weight * 100.
    """
    total_weight = sum(r.weight for r in results)
    found_weight = sum(r.weight for r in results if r.found)
    if total_weight == 0:
        return 0
    return round(found_weight / total_weight * 100)


def ai_readiness_label(score: int) -> tuple[str, str]:
    """Return (label, emoji) for a given score."""
    if score >= 80:
        return "AI-Ready", "🟢"
    if score >= 55:
        return "Partially AI-Ready", "🟡"
    return "Needs Attention", "🔴"
