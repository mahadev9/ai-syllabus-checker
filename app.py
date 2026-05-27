"""
AI Syllabus Checker
-------------------
Upload a syllabus (PDF / DOCX / text paste) and get instant AI-powered
feedback on policy completeness, clarity, and AI-readiness.
"""
from __future__ import annotations

import os
import textwrap

import streamlit as st
from dotenv import load_dotenv

from utils.parser import extract_text
from utils.rules import SectionResult, analyze, ai_readiness_label, compute_score
from utils import llm

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Syllabus Checker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Hide Streamlit Cloud GitHub & footer chrome ── */
    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stFooter"] { display: none !important; }
    [data-testid="stBottom"] { display: none !important; }
    [data-testid="stBottom"] > * { display: none !important; }
    [data-testid="appCreatorAvatar"] { display: none !important; }
    div:has([data-testid="appCreatorAvatar"]) { display: none !important; }
    [data-testid="stToolbarActions"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }

    /* ── Hide default "Limit 200MB" file uploader text ── */
    [data-testid="stFileUploaderDropzoneInstructions"] small { display: none !important; }
    [data-testid="stFileUploaderDropzone"] small { display: none !important; }

    .score-card {
        border-radius: 12px;
        padding: 20px 28px;
        text-align: center;
        margin-bottom: 16px;
    }
    .score-green  { background: #d4edda; color: #155724; }
    .score-yellow { background: #fff3cd; color: #856404; }
    .score-red    { background: #f8d7da; color: #721c24; }
    .section-found   { border-left: 4px solid #28a745; padding-left: 10px; margin-bottom: 8px; }
    .section-missing { border-left: 4px solid #dc3545; padding-left: 10px; margin-bottom: 8px; }
    .tag-found   { background:#d4edda; color:#155724; border-radius:4px; padding:2px 8px; font-size:0.8em; }
    .tag-missing { background:#f8d7da; color:#721c24; border-radius:4px; padding:2px 8px; font-size:0.8em; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — LLM provider, API keys, model selection
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    st.divider()

    # Provider toggle
    provider_label = st.radio(
        "LLM Provider",
        ["Claude (Anthropic)", "GPT-5.4 (OpenAI)"],
        index=0,
        help="Switch between Anthropic Claude and OpenAI GPT at any time.",
    )
    provider: llm.Provider = "anthropic" if "Claude" in provider_label else "openai"

    st.divider()

    # API keys
    if provider == "anthropic":
        default_key = os.getenv("ANTHROPIC_API_KEY", "")
        api_key = st.text_input(
            "Anthropic API Key",
            value=default_key,
            type="password",
            placeholder="sk-ant-...",
            help="Get a key at console.anthropic.com",
        )
        model_choice = st.selectbox(
            "Model",
            ["claude-sonnet-4-6", "claude-opus-4-7", "claude-haiku-4-5-20251001"],
            index=0,
        )
    else:
        default_key = os.getenv("OPENAI_API_KEY", "")
        api_key = st.text_input(
            "OpenAI API Key",
            value=default_key,
            type="password",
            placeholder="sk-...",
            help="Get a key at platform.openai.com",
        )
        model_choice = st.selectbox(
            "Model",
            ["gpt-5.4-2026-03-05", "gpt-5.4-mini-2026-03-17"],
            index=0,
        )

    st.divider()
    st.caption(
        "API keys are used only for this session and never stored.\n\n"
        "Rule-based analysis (section detection, scoring) runs **locally** — "
        "no data leaves your browser unless you click an AI button."
    )


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.title("📋 AI Syllabus Checker")
st.caption(
    "Upload your syllabus to detect missing sections, get AI-powered improvement "
    "suggestions, and generate a ready-to-paste AI policy in seconds."
)
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# INPUT — Upload or paste
# ─────────────────────────────────────────────────────────────────────────────
input_tab, paste_tab = st.tabs(["📁 Upload File", "✏️ Paste Text"])

syllabus_text: str = ""

MAX_FILE_SIZE_MB = 10
MAX_FILES = 2

with input_tab:
    uploaded_files = st.file_uploader(
        "Upload your syllabus (PDF, DOCX, or TXT) — max 2 files, 10 MB each",
        type=["pdf", "docx", "doc", "txt"],
        accept_multiple_files=True,
        help="Files are processed locally; text is sent to the LLM only when you click an AI action.",
    )

    if uploaded_files:
        # Enforce file count
        if len(uploaded_files) > MAX_FILES:
            st.error(f"Please upload at most {MAX_FILES} files at a time.")
            uploaded_files = []

        all_texts = []
        for uploaded in uploaded_files:
            size_mb = len(uploaded.getvalue()) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                st.error(
                    f"**{uploaded.name}** is {size_mb:.1f} MB — exceeds the {MAX_FILE_SIZE_MB} MB limit. Please upload a smaller file."
                )
                continue
            with st.spinner(f"Extracting text from {uploaded.name}…"):
                text = extract_text(uploaded)
            st.success(f"Extracted {len(text):,} characters from **{uploaded.name}**")
            all_texts.append(text)

        if all_texts:
            syllabus_text = "\n\n---\n\n".join(all_texts)

with paste_tab:
    pasted = st.text_area(
        "Paste your syllabus text here",
        height=280,
        placeholder="Paste the full text of your syllabus…",
    )
    if pasted.strip():
        syllabus_text = pasted.strip()


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS (rule-based — always available)
# ─────────────────────────────────────────────────────────────────────────────
if syllabus_text:

    st.divider()
    st.subheader("📊 Section Analysis")

    results: list[SectionResult] = analyze(syllabus_text)
    score = compute_score(results)
    label, emoji = ai_readiness_label(score)

    # Score card
    colour_class = (
        "score-green" if score >= 80 else "score-yellow" if score >= 55 else "score-red"
    )
    st.markdown(
        f"""
        <div class="score-card {colour_class}">
            <h1 style="margin:0;font-size:3rem;">{emoji} {score}/100</h1>
            <h3 style="margin:4px 0 0 0;">{label}</h3>
            <p style="margin:0;opacity:.8;">Policy Completeness Score</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Section grid
    found_sections = [r for r in results if r.found]
    missing_sections = [r for r in results if not r.found]

    col_found, col_missing = st.columns(2)

    with col_found:
        st.markdown(f"#### ✅ Found ({len(found_sections)})")
        for r in found_sections:
            kw_preview = ", ".join(r.matched_keywords[:3])
            st.markdown(
                f'<div class="section-found">'
                f'<strong>{r.label}</strong>'
                f'<br><span style="font-size:.8em;color:#555;">Matched: <em>{kw_preview}</em></span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_missing:
        st.markdown(f"#### ❌ Missing ({len(missing_sections)})")
        if missing_sections:
            for r in missing_sections:
                st.markdown(
                    f'<div class="section-missing">'
                    f'<strong>{r.label}</strong>'
                    f'<br><span style="font-size:.8em;color:#888;">Not detected in text</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("All standard sections detected!")

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # AI ANALYSIS — requires key
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("🤖 AI-Powered Deep Analysis")

    if not api_key:
        st.info(
            f"Enter your {'Anthropic' if provider == 'anthropic' else 'OpenAI'} "
            "API key in the sidebar to unlock AI analysis and policy generation.",
            icon="🔑",
        )
    else:
        if st.button("🔍 Analyze with AI", type="primary", use_container_width=True):
            with st.spinner(f"Analyzing with {model_choice}…"):
                try:
                    ai_feedback = llm.analyze_syllabus(
                        syllabus_text, provider, api_key, model_choice
                    )
                    st.session_state["ai_feedback"] = ai_feedback
                except Exception as exc:
                    st.error(f"Error calling {provider}: {exc}")

        if "ai_feedback" in st.session_state:
            st.markdown(st.session_state["ai_feedback"])

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # GENERATE AI POLICY — killer feature
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("✨ Generate AI Policy")
    st.caption(
        "Choose a stance and instantly generate ready-to-paste syllabus language "
        "tailored to your course philosophy."
    )

    stance_col, btn_col = st.columns([2, 1])
    with stance_col:
        stance = st.select_slider(
            "AI Usage Stance",
            options=["Strict", "Moderate", "Open"],
            value="Moderate",
            help=(
                "Strict = no AI allowed | "
                "Moderate = permitted with disclosure | "
                "Open = encouraged with citation"
            ),
        )

        stance_descriptions = {
            "Strict": "🚫 AI tools are **not permitted** for any graded work.",
            "Moderate": "⚖️ AI tools are **permitted with mandatory disclosure and citation**.",
            "Open": "✅ AI tools are **encouraged** as a professional skill; all use must be cited.",
        }
        st.caption(stance_descriptions[stance])

    if not api_key:
        st.info("API key required (see sidebar).", icon="🔑")
    else:
        with btn_col:
            st.write("")  # vertical spacer
            st.write("")
            generate_clicked = st.button(
                "Generate Policy →", type="primary", use_container_width=True
            )

        if generate_clicked:
            with st.spinner(f"Generating {stance} policy…"):
                try:
                    policy_text = llm.generate_ai_policy(
                        stance, provider, api_key, model_choice
                    )
                    st.session_state["generated_policy"] = policy_text
                    st.session_state["policy_stance"] = stance
                except Exception as exc:
                    st.error(f"Error: {exc}")

    if "generated_policy" in st.session_state:
        st.divider()
        st.markdown(
            f"#### 📝 Generated {st.session_state['policy_stance']} AI Policy"
        )
        policy_box = st.text_area(
            "Copy this into your syllabus",
            value=st.session_state["generated_policy"],
            height=260,
            label_visibility="collapsed",
        )
        st.download_button(
            "⬇️ Download as .txt",
            data=st.session_state["generated_policy"],
            file_name=f"ai_policy_{st.session_state['policy_stance'].lower()}.txt",
            mime="text/plain",
        )

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # QUICK TIPS for missing sections (no LLM needed)
    # ─────────────────────────────────────────────────────────────────────────
    if missing_sections:
        st.subheader("💡 Quick Additions for Missing Sections")
        st.caption("Paste-ready starter text — edit to fit your course.")

        QUICK_TIPS: dict[str, str] = {
            "ai_policy": (
                "**AI Tools Policy:** [Generated above — use the Generate AI Policy tool above.]"
            ),
            "academic_integrity": (
                "**Academic Integrity:** All students are expected to abide by the university's "
                "Academic Integrity Policy. Plagiarism, cheating, or misrepresenting AI-generated "
                "work as your own will result in a grade of zero for the assignment and may result "
                "in further disciplinary action."
            ),
            "accessibility": (
                "**Accessibility & Accommodations:** Students requiring accommodations due to a "
                "disability should contact the Office of Disability Support Services (DSS) and "
                "provide documentation to the instructor within the first two weeks of class. "
                "I am committed to making this course accessible to all students."
            ),
            "grading": (
                "**Grading Breakdown:** Assignments 30% | Midterm Exam 25% | Final Project 30% | "
                "Participation 15%. Letter grade scale: A 90-100, B 80-89, C 70-79, D 60-69, F <60."
            ),
            "late_work": (
                "**Late Work Policy:** Assignments submitted late will be penalized 10% per day "
                "unless an extension is requested at least 24 hours in advance. Extensions are "
                "granted at my discretion for documented emergencies."
            ),
            "contact_info": (
                "**Contact & Office Hours:** Email: [your email] | Office Hours: [days/times] "
                "in [location] or via Zoom (link on Canvas). I aim to respond to emails within "
                "48 hours on business days."
            ),
            "support_resources": (
                "**Student Resources:** Writing Center, Tutoring Center, Counseling Services, "
                "and the Student Food Pantry are available on campus. Contact Student Affairs "
                "for a full list of support resources."
            ),
            "attendance": (
                "**Attendance Policy:** Regular attendance is expected. More than three unexcused "
                "absences may result in a grade reduction. Please notify me before class if you "
                "will be absent."
            ),
        }

        for r in missing_sections:
            tip = QUICK_TIPS.get(r.key)
            if tip:
                with st.expander(f"➕ {r.label}"):
                    st.markdown(tip)


# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.info(
        "👆 Upload a syllabus file or paste your syllabus text above to get started.",
        icon="📋",
    )

    with st.expander("🎯 What this tool checks", expanded=True):
        checks = [
            ("AI / Generative AI Policy", "Does your syllabus address ChatGPT, Claude, and other AI tools?"),
            ("Academic Integrity", "Is plagiarism / cheating policy clearly stated?"),
            ("Accessibility", "Is there a disability accommodations statement?"),
            ("Grading Policy", "Are weights, rubrics, and the grading scale explicit?"),
            ("Late Work Policy", "Do students know the consequences of submitting late?"),
            ("Instructor Contact", "Are office hours and contact info easy to find?"),
            ("Student Support", "Are campus resources mentioned?"),
            ("Attendance Policy", "Are expectations around attendance spelled out?"),
        ]
        for title, desc in checks:
            st.markdown(f"**{title}** — {desc}")
