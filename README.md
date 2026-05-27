# 📋 AI Syllabus Checker

> **Help faculty create clear, AI-ready, student-friendly syllabi in minutes.**

A Streamlit app that scans any syllabus (PDF, DOCX, or pasted text) for missing
sections, policy gaps, and clarity issues — then generates ready-to-paste
improvements using Claude or GPT-4o.

---

## Features

| Feature | Details |
|---|---|
| **Upload** | PDF, DOCX, DOC, TXT or paste text directly |
| **Rule-Based Detection** | Instantly flags 8 key sections — no API key needed |
| **AI Readiness Score** | 0-100 score with Green / Yellow / Red rating |
| **Deep AI Analysis** | Claude or GPT-4o reviews each section for quality & gaps |
| **AI Policy Generator** | Generate Strict / Moderate / Open policy in one click |
| **Quick-Add Templates** | Paste-ready starter text for every missing section |
| **Provider Toggle** | Switch between Anthropic Claude and OpenAI in the sidebar |

---

## Sections Checked

- ✅ AI / Generative AI Policy  
- ✅ Academic Integrity  
- ✅ Accessibility / Disability Accommodations  
- ✅ Grading Policy  
- ✅ Late Work Policy  
- ✅ Instructor Contact & Office Hours  
- ✅ Student Support Resources  
- ✅ Attendance Policy  

---

## Quick Start

```bash
# 1. Clone / open the project
cd ai-syllabus-checker

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set API keys in .env
cp .env.example .env
# Edit .env with your Anthropic and/or OpenAI keys

# 5. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Configuration

API keys can be set in three ways (highest priority wins):

1. **Sidebar input** — enter key directly in the app UI  
2. **`.env` file** — `ANTHROPIC_API_KEY=...` or `OPENAI_API_KEY=...`  
3. **Environment variable** — export before running

Rule-based analysis (section detection, scoring) runs **locally** — no data
leaves your machine unless you click an AI action button.

---

## Project Structure

```
app.py              ← Streamlit frontend
utils/
  parser.py         ← PDF/DOCX text extraction
  rules.py          ← keyword-based section detection & scoring
  llm.py            ← unified Claude / OpenAI client
requirements.txt
.env.example
```

---

## Roadmap

- **V1** (current) — Upload → detect → score → generate AI policy  
- **V2** — Downloadable PDF report, editable recommendations  
- **V3** — Compare against university or department templates  
- **V4** — Canvas / Google Docs plugin, institutional dashboards  

---

## Tech Stack

- **Frontend** — [Streamlit](https://streamlit.io)  
- **LLMs** — [Anthropic Claude](https://anthropic.com) / [OpenAI GPT-4o](https://openai.com)  
- **PDF parsing** — [pypdf](https://pypdf.readthedocs.io)  
- **DOCX parsing** — [python-docx](https://python-docx.readthedocs.io)  
