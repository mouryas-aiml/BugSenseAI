# BugSenseAI — Enterprise AI Bug Intelligence & Triage Platform

An enterprise-grade software maintenance and automated defect triage platform aligned directly with the **TCS AI Problem Statement**. Transforms unstructured bug reports, logs, and stack traces into structured, actionable engineering intelligence with zero hallucination, strict PII privacy masking, semantic duplicate detection, and human-in-the-loop review.

Powered by the **Google Gemini SDK** (`google-genai`), Sentence-Transformers vector similarity, and FastAPI + Streamlit.

---

## 🎯 TCS Problem Alignment

| TCS Requirement | BugSenseAI Capability |
|---|---|
| **AI/GenAI Summarization** | Distills complex customer complaints and multi-page stack traces into concise 1–2 sentence executive summaries for maintenance engineers. |
| **Key Information Extraction** | Extracts component, bug type, affected users, error codes, environment, and technical entities. |
| **Actionable Bug Summaries** | Formats findings into engineer-ready dossiers with suggested assignee teams, Jira labels, and test coverage areas. |
| **Reproduction-Step Extraction** | Extracts verified sequential steps or marks missing sequences with clear provenance tags. |
| **Impact Identification** | Quantifies operational impact and blast radius (e.g., revenue risk, user percentage affected). |
| **Severity Classification** | Standardized P1 (Critical) through P4 (Low) rubric with automated business impact elevation. |
| **Data Privacy & Anonymization** | Pre-LLM client-side redaction of emails, IP addresses, credentials, and personal identifiers. |
| **Strict Fact vs. Inference Separation** | Explicitly distinguishes stated report facts from AI hypotheses (`[HYPOTHESIS]`, `[INFERRED]`) and rule-based decisions. |
| **Missing Information Flagging** | Flags incomplete reports with *"Information Missing — Human Input Required"*. |
| **Duplicate Bug Detection** | Dense 384-dimensional semantic embeddings (`all-MiniLM-L6-v2`) with cosine similarity scoring, rationale explanations, and side-by-side diffing. |
| **Batch Processing** | Ingests CSV, JSON, and TXT bug batches with real-time progress bars, filtering, and export. |
| **Human-in-the-Loop Review** | Automated review triggers on P1 severity, low confidence, or low quality scores; interactive overrides. |
| **Platform Analytics & Health** | Interactive Plotly dashboards tracking severity trends, component clusters, duplicate rates, pipeline latency, and live service probes. |

---

## 🔄 Core Product Flow

```
Bug Report (Text / CSV / Logs)
         │
         ▼
  Privacy / PII Anonymization (Client-side regex masking of emails, IPs, tokens)
         │
         ▼
  Deterministic Quality Scoring (Completeness heuristic 0–100)
         │
         ▼
  AI Understanding (Google Gemini via official google-genai SDK)
         │
         ▼
  Structured Extraction & Validation (Typed Pydantic Schemas)
  ├── Executive Summary & Title
  ├── Severity (P1–P4) & Priority Rationale
  ├── Operational Impact & Affected Users
  ├── Sequential Reproduction Steps
  ├── Expected vs. Actual Behavior
  ├── Environment & Technical Entities
  └── Root-Cause Hypothesis ([HYPOTHESIS])
         │
         ▼
  Information Gap Analysis (Missing Info → "Human Input Required" flag)
         │
         ▼
  Deterministic Rules Engine (Severity elevation, team routing, test areas)
         │
         ▼
  Semantic Vector Duplicate Detection (Cosine similarity comparison)
         │
         ▼
  Human-in-the-Loop Review & Jira Export
         │
         ▼
  Persistent JSON Dossier & Real-Time Analytics
```

---

## 🖥️ Enterprise UI/UX (9 Sections)

BugSenseAI features a dark-themed, high-contrast enterprise interface built with modern Streamlit routing (`st.navigation`):

1. **Executive Dashboard**: High-level KPIs (Total bugs, P1–P4, Human-review queue, Duplicates, Avg completeness, Avg confidence), severity and component charts, and live activity tables.
2. **Analyze Bug**: Multi-line bug input with preset sample scenarios (P1 Checkout crash, P2 Timeout, Vague report, P4 UI glitch), optional metadata, and live processing status.
3. **AI Analysis Result**: Comprehensive structured intelligence dossier separating report facts from AI hypotheses, PII masking summary, missing info banners, severity override controls, and 1-click JSON export.
4. **Batch Analysis**: Bulk file ingestion (CSV, JSON, TXT), real-time progress tracking, sortable/filterable results table, and combined CSV/JSON export.
5. **Duplicate & Similar Issues**: Vector similarity engine displaying ranked matches with percentage scores, duplicate rationales, and side-by-side comparative views.
6. **Bug History Dossiers**: Full-text search and multi-facet filtering (Severity, Component, Confidence, Review Status) across all saved triage reports.
7. **Engineering Analytics**: Statistical dashboards covering severity distribution, component concentration, duplicate filing rates, quality score spread, and AI pipeline latency.
8. **System Health & Diagnostics**: Live health probes for FastAPI backend, Google Gemini API connectivity, sentence-transformer model cache, and administrator troubleshooting guides.
9. **Platform Settings & Governance**: Model variant selection, timeout/temperature sliders, duplicate thresholds, privacy toggles, and strict zero-exposure secret masking.

---

## 🚀 Getting Started

### 1. Prerequisites & Virtual Environment

Python 3.10+ is required.

```bash
git clone https://github.com/mouryas-aiml/BugSenseAI.git
cd BugSenseAI

# Activate virtual environment
.\venv\Scripts\activate       # Windows
source venv/bin/activate      # Linux / macOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set your Google Gemini API key:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-flash-lite-latest
LLM_TIMEOUT_SECONDS=60
```
> **Note:** The platform automatically falls back across reliable Gemini flash models (`gemini-flash-lite-latest`, `gemini-flash-latest`) to protect against temporary Google traffic spikes (503s).

### 3. Launching the Application

Start the FastAPI backend service and the modern React + TypeScript dashboard:

```bash
# Terminal 1 — FastAPI Backend (Port 8000)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Modern React + TypeScript Dashboard (Port 5173) [RECOMMENDED]
cd frontend-react
npm install
npm run dev
```

Open your browser at **`http://localhost:5173`**.

*(Optional Python Streamlit Dashboard available via `streamlit run frontend/app.py` on port 8501).*


---

## 🧪 Automated Test Suite

BugSenseAI includes 113 comprehensive unit tests covering all core modules:

```bash
pytest tests/ -v
```

**Test Coverage Breakdown:**
- `tests/test_triage.py`: JSON schema compliance, enum boundaries, Pydantic validation.
- `tests/test_rules.py`: Deterministic routing rules, severity elevation, test area mapping.
- `tests/test_dedup.py`: Vector cosine similarity, duplicate detection thresholds.
- `tests/test_anonymizer.py`: PII regex redaction for emails, IPs, names, and tokens.
- `tests/test_quality_scorer.py`: Report completeness scoring and missing item detection.
- `tests/test_analytics.py`: Aggregate statistics, pagination, and history parsing.
- `tests/test_ci_parser.py`: JUnit XML failure parsing and CI bug description synthesis.
- `tests/test_feedback.py`: Human correction recording and dynamic prompt injection.

---

## 🛡️ Security & Privacy Guarantees

- **Zero Secret Exposure**: Production API keys are read strictly through environment variables. Keys are never printed in console logs, UI pages, or exported JSON dossiers.
- **Client-Side Redaction**: Customer emails, IPv4/IPv6 addresses, authorization tokens, and personal names are scrubbed before payload transmission to AI providers.
- **Strict Provenance**: Hypotheses are explicitly marked `[HYPOTHESIS]` to prevent false confidence during critical incident triage.
