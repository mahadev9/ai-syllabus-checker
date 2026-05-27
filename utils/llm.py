"""
Unified LLM client.
Supports Anthropic (Claude) and OpenAI, selected at runtime.
"""
from __future__ import annotations

from typing import Literal

Provider = Literal["anthropic", "openai"]

# Default models
ANTHROPIC_MODEL = "claude-sonnet-4-6"
OPENAI_MODEL = "gpt-4o"

# ---------------------------------------------------------------------------
# System prompt shared across all tasks
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an expert instructional designer and higher-education
policy specialist. You help faculty write clear, compliant, and student-friendly
syllabi. You specialize in AI policy, academic integrity, and accessibility best
practices. Be concise, practical, and encouraging in tone."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _anthropic_chat(messages: list[dict], api_key: str, model: str) -> str:
    import anthropic  # lazy import

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def _openai_chat(messages: list[dict], api_key: str, model: str) -> str:
    from openai import OpenAI  # lazy import

    client = OpenAI(api_key=api_key)
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    response = client.chat.completions.create(
        model=model,
        messages=full_messages,
        max_tokens=2048,
    )
    return response.choices[0].message.content


def chat(
    messages: list[dict],
    provider: Provider,
    api_key: str,
    model: str | None = None,
) -> str:
    """Route a chat request to the selected provider."""
    if provider == "anthropic":
        return _anthropic_chat(messages, api_key, model or ANTHROPIC_MODEL)
    else:
        return _openai_chat(messages, api_key, model or OPENAI_MODEL)


# ---------------------------------------------------------------------------
# Task-specific prompts
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT = """Analyze the following syllabus text and provide structured feedback.

For EACH of these sections, evaluate the quality (not just presence):
1. AI / Generative AI Policy
2. Academic Integrity
3. Accessibility / Disability Accommodations
4. Grading Policy
5. Late Work Policy
6. Instructor Contact / Office Hours
7. Student Support Resources
8. Attendance Policy

For each section found, identify:
- What's good
- What's missing or vague
- One specific improvement suggestion

Format your response as clear markdown with section headers (##).
Be specific and practical — faculty should be able to act on your feedback immediately.

SYLLABUS TEXT:
{syllabus_text}"""

GENERATE_POLICY_PROMPT = """Generate a {stance} AI policy section for a college syllabus.

Stance guidelines:
- Strict: AI tools are NOT permitted for any graded work
- Moderate: AI tools may be used for certain tasks (brainstorming, outlining, research assistance)
  with mandatory disclosure and citation
- Open: AI tools are encouraged as professional skills; all use must be disclosed and cited

The policy must cover:
1. What AI tools are / aren't permitted
2. How to disclose and cite AI use (provide a sample citation format)
3. Consequences for policy violations
4. Rationale / learning goals behind the policy

Write in clear, direct language suitable for a college syllabus (2-4 short paragraphs).
Do NOT use bullet lists — write in paragraph form."""

IMPROVE_SECTION_PROMPT = """Rewrite and improve the following syllabus section.
Make it clearer, more student-friendly, and more complete.
Keep roughly the same length (±20%).

SECTION ({section_name}):
{section_text}

Return only the improved section text, no commentary."""


def analyze_syllabus(text: str, provider: Provider, api_key: str, model: str | None = None) -> str:
    prompt = ANALYSIS_PROMPT.format(syllabus_text=text[:8000])  # trim for token safety
    return chat([{"role": "user", "content": prompt}], provider, api_key, model)


def generate_ai_policy(stance: str, provider: Provider, api_key: str, model: str | None = None) -> str:
    prompt = GENERATE_POLICY_PROMPT.format(stance=stance)
    return chat([{"role": "user", "content": prompt}], provider, api_key, model)


def improve_section(
    section_name: str,
    section_text: str,
    provider: Provider,
    api_key: str,
    model: str | None = None,
) -> str:
    prompt = IMPROVE_SECTION_PROMPT.format(
        section_name=section_name,
        section_text=section_text,
    )
    return chat([{"role": "user", "content": prompt}], provider, api_key, model)
