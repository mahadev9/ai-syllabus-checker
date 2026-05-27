"""
Text extraction from PDF, DOCX, or plain text.
"""
from __future__ import annotations

import io
from typing import Optional


def extract_text(uploaded_file) -> str:
    """
    Accept a Streamlit UploadedFile object (or a raw str/bytes) and
    return the extracted plain text.
    """
    if uploaded_file is None:
        return ""

    name: str = getattr(uploaded_file, "name", "") or ""
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""

    # ── PDF ──────────────────────────────────────────────────────────────
    if ext == "pdf":
        return _extract_pdf(uploaded_file)

    # ── DOCX ─────────────────────────────────────────────────────────────
    if ext in ("docx", "doc"):
        return _extract_docx(uploaded_file)

    # ── Fallback: try to decode as UTF-8 text ────────────────────────────
    raw = uploaded_file.read()
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="replace")
    return str(raw)


def _extract_pdf(file) -> str:
    from pypdf import PdfReader  # lazy import to avoid hard dep at import time

    reader = PdfReader(file)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def _extract_docx(file) -> str:
    from docx import Document  # lazy import

    raw = file.read()
    doc = Document(io.BytesIO(raw))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
