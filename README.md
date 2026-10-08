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

## Real Dataset Issue Intelligence

The React dashboard includes an Issue Intelligence workspace backed by the configurable Hugging Face dataset:

```python
from datasets import load_dataset

ds = load_dataset("helmo/github-issues")
```

The implementation lives in [backend/issue_intelligence.py](backend/issue_intelligence.py). It loads the dataset once, excludes pull requests by default, anonymizes titles, bodies, and comments, batches Sentence Transformer embeddings, and persists the result under `outputs/`:

- `issue_intelligence_index.json` stores normalized issue metadata and cluster assignments.
- `issue_intelligence_embeddings.npz` stores the compressed embedding matrix.
- The Hugging Face cache stores the downloaded source dataset.

The current dataset contains GitHub issue and pull-request records with titles, bodies, labels, states, timestamps, comments, repository metadata, and source URLs. A default build filters pull requests and indexes the remaining issue records. No request downloads or embeds the full dataset again.

### Preparation and configuration

Start the backend, open the **Issue Intelligence** navigation item, and the UI will call the asynchronous preparation endpoint. The first build performs normalization, batch embedding, and semantic graph clustering. Later requests reuse the persistent index.

Configuration is environment-driven so another compatible dataset can be substituted:

```env
ISSUE_DATASET_NAME=helmo/github-issues
ISSUE_DATASET_SPLIT=train
ISSUE_INCLUDE_PRS=false
ISSUE_EMBEDDING_MODEL=all-MiniLM-L6-v2
ISSUE_CLUSTER_THRESHOLD=0.78
ISSUE_RETRIEVAL_THRESHOLD=0.42
ISSUE_INTELLIGENCE_INDEX_DIR=outputs
```

### Intelligence workflow

```text
Real GitHub issues and discussions
       -> normalized, anonymized issue records
       -> persistent embeddings and semantic clusters
       -> analytics, trends, recurring issue detection
       -> retrieved historical resolution evidence
       -> grounded support response or human escalation
       -> support feedback and KPI tracking
```

The resolution engine deliberately returns an escalation recommendation when retrieved discussions do not contain resolution evidence. It does not invent troubleshooting steps. When evidence exists, it returns the source issue, discussion-derived resolution summary, step-by-step evidence snippets, similarity scores, and source URLs.

### Issue Intelligence API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/issue-intelligence/status` | Check whether the persistent index is ready |
| POST | `/issue-intelligence/prepare` | Start one-time background dataset preparation |
| GET | `/issue-intelligence/analytics` | Calculate real dataset KPIs and trends |
| GET | `/issue-intelligence/clusters` | Paginated semantic issue clusters |
| GET | `/issue-intelligence/issues` | Paginated, filterable source records |
| GET | `/issue-intelligence/issues/{issue_id}` | Issue details, similar reports, comments, and evidence |
| POST | `/issue-intelligence/resolve` | Retrieve grounded resolution evidence for a support query |
| POST | `/issue-intelligence/feedback` | Record resolved/unresolved support outcomes |
| GET | `/issue-intelligence/export` | Export filtered issues, clusters, or KPI summaries as CSV |

### Data-derived mass-support KPIs

The Issue Intelligence dashboard calculates, rather than hardcodes:

- Total reports
- Unique semantic issue clusters
- Similar/duplicate reports beyond cluster representatives
- Top issue and its percentage of the filtered dataset
- Potentially auto-resolvable records with resolution evidence
- Human escalations without sufficient resolution evidence
- Grounded AI resolution rate
- Evidence confidence, derived from resolution discussion depth
- Completeness score from available report text
- Open/closed state counts
- High-priority count
- Category/component distributions
- Most-discussed issues
- Monthly issue trends

The dashboard supports issue search, category/state/priority/date filters, cluster and issue detail drawers, evidence links, support resolution feedback, and top-right CSV exports for the filtered issue dataset, clusters, and KPI summary.

## Validation

The project currently has 117 passing Python tests, including tests for dataset normalization, cluster formation, evidence-only resolution behavior, CSV export fields, and a simulated 1,000-identical-report workload collapsing into one cluster. A real Hugging Face smoke test successfully loaded and normalized the dataset; the persistent index is generated on first preparation rather than during every request.
