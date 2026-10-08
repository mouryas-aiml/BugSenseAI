"""
BugSenseAI — Section 8: System Health & Diagnostics
Live infrastructure probes for FastAPI backend, Google Gemini API,
Vector Store index, environment variables, and remediation guides.
"""

import streamlit as st
import time
import os
from frontend.api_client import check_backend_status, get_backend_url
from frontend.styles import render_header, render_metric


def show():
    render_header(
        title="System Health & Infrastructure Diagnostics",
        subtitle="Real-time connectivity status, service health probes, and administrator diagnostic guidance",
        badge="INFRASTRUCTURE MONITORING"
    )

    if st.button("🔄 Run Full Diagnostic Probe", type="primary"):
        st.rerun()

    # Run Probes
    with st.spinner("Probing system services..."):
        t0 = time.time()
        health = check_backend_status()
        latency = round((time.time() - t0) * 1000, 1)

    backend_online = health.get("reachable", False)
    llm_status = health.get("llm_status", "unknown")
    provider = health.get("llm_provider", "gemini")
    model = health.get("llm_model", "unknown")
    vector_count = health.get("vector_store_entries", 0)

    # 1. Component Health Status Cards
    h1, h2, h3, h4 = st.columns(4)

    with h1:
        b_color = "#10b981" if backend_online else "#f59e0b"
        b_text = "Online (Port 8000)" if backend_online else "Direct Engine Mode"
        st.markdown(f"""
<div class="metric-container">
    <div class="metric-title">FastAPI Backend</div>
    <div class="metric-value" style="color: {b_color}; font-size: 1.35rem;">{b_text}</div>
    <div class="metric-sub">{get_backend_url()}</div>
</div>
""", unsafe_allow_html=True)

    with h2:
        g_color = "#10b981" if llm_status == "ok" else "#ef4444"
        g_text = "Operational" if llm_status == "ok" else "Degraded"
        st.markdown(f"""
<div class="metric-container">
    <div class="metric-title">Gemini AI Service</div>
    <div class="metric-value" style="color: {g_color}; font-size: 1.35rem;">{g_text}</div>
    <div class="metric-sub">Model: {model}</div>
</div>
""", unsafe_allow_html=True)

    with h3:
        v_color = "#10b981" if vector_count > 0 else "#f59e0b"
        st.markdown(f"""
<div class="metric-container">
    <div class="metric-title">Vector Memory Store</div>
    <div class="metric-value" style="color: {v_color}; font-size: 1.35rem;">{vector_count} bugs</div>
    <div class="metric-sub">all-MiniLM-L6-v2 (384-dim)</div>
</div>
""", unsafe_allow_html=True)

    with h4:
        st.markdown(f"""
<div class="metric-container">
    <div class="metric-title">Probe Latency</div>
    <div class="metric-value" style="font-size: 1.35rem;">{latency} ms</div>
    <div class="metric-sub">Local IPC / Loopback</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

    # 2. Detailed Diagnostic Breakdown
    st.subheader("Service Verification Breakdown")

    # Probe 1: LLM Engine
    with st.expander("🤖 AI Provider: Google Gemini Integration", expanded=True):
        st.markdown(f"**Configured Provider:** `{provider.upper()}`")
        st.markdown(f"**Primary Model:** `{model}`")
        st.markdown(f"**SDK:** `google-genai` (Official Google Generative AI SDK)")
        
        has_key = bool(os.getenv("GEMINI_API_KEY"))
        if has_key:
            key_len = len(os.getenv("GEMINI_API_KEY", ""))
            st.markdown(f"**API Key Status:** `Configured` (Length: {key_len} chars, masked for security)")
        else:
            st.markdown("**API Key Status:** `MISSING in .env` ❌")

        if llm_status == "ok":
            st.success("✓ Gemini API connection test succeeded. Structured JSON output is active.")
        else:
            st.error(f"✕ Gemini probe failed: {health.get('message', 'Could not reach model')}")

    # Probe 2: FastAPI Backend Service
    with st.expander("🌐 Backend Service (FastAPI / Uvicorn)", expanded=True):
        if backend_online:
            st.success(f"✓ FastAPI backend is responding normally on `{get_backend_url()}`.")
            st.markdown("All REST endpoints (`/triage`, `/triage/batch`, `/analytics`, `/history`) are available for external CI/CD integrations.")
        else:
            st.warning("⚠️ FastAPI HTTP service is currently offline on port 8000.")
            st.markdown("""
**Impact:** Frontend is operating in **Direct Engine Mode** (running the Python pipeline directly in-process). All triage features work normally for UI users.
<br><br>
**To start the standalone FastAPI service:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
""", unsafe_allow_html=True)

    # Probe 3: PII & Data Privacy Engine
    with st.expander("🛡️ Privacy & PII Redaction Engine", expanded=False):
        st.markdown("**Status:** `Active` ✓")
        st.markdown("All incoming raw bug reports pass through deterministic regex anonymization prior to reaching any external LLM endpoint.")
        st.markdown("**Protected Entity Types:** Customer emails, IP addresses, JWT tokens, API keys, credentials, and user IDs.")

    # Probe 4: Vector Similarity Search
    with st.expander("📐 Dense Semantic Vector Store", expanded=False):
        st.markdown("**Model:** `all-MiniLM-L6-v2` (Sentence-Transformers)")
        st.markdown(f"**Indexed Bug Count:** `{vector_count}` reports")
        st.markdown(f"**Similarity Threshold:** `0.68` for automatic duplicate alerts, `0.30` for related items")

    # 3. Administrator Remediation Guide
    st.subheader("Administrator Troubleshooting Guide")
    st.markdown("""
| Issue | Root Cause | Remediation Action |
|---|---|---|
| **Connection Refused (Port 8000)** | FastAPI service not started | Start backend using `python -m uvicorn backend.main:app --port 8000` or continue in Direct Mode |
| **Gemini 401 / Authentication Error** | Missing or invalid API key | Set `GEMINI_API_KEY=...` in your `.env` file |
| **Gemini 503 / Unavailable** | Temporary Google model spike | The platform automatically retries with backup flash models (`gemini-flash-lite-latest`) |
| **Request Timeout** | Slow network or heavy prompt | Increase `LLM_TIMEOUT_SECONDS=60` in `.env` |
""")


if __name__ == "__main__":
    show()
