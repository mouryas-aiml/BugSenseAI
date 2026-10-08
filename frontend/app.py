"""
BugSenseAI — Enterprise AI Bug Intelligence & Triage Platform
Master Application Shell & Navigation Router
"""

import streamlit as st
import os
from pathlib import Path
from frontend.styles import apply_theme
from frontend.api_client import check_backend_status

# Page Configuration
st.set_page_config(
    page_title="BugSenseAI — Enterprise AI Bug Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global dark enterprise CSS theme
apply_theme()

# Paths to views relative to frontend/ directory
VIEWS_DIR = Path(__file__).parent / "views"

dashboard_page = st.Page(str(VIEWS_DIR / "dashboard.py"), title="Executive Dashboard", icon=":material/dashboard:", default=True)
analyze_page = st.Page(str(VIEWS_DIR / "analyze.py"), title="Analyze Bug", icon=":material/psychology:")
batch_page = st.Page(str(VIEWS_DIR / "batch.py"), title="Batch Analysis", icon=":material/batch_prediction:")
duplicates_page = st.Page(str(VIEWS_DIR / "duplicates.py"), title="Duplicate Detection", icon=":material/difference:")
history_page = st.Page(str(VIEWS_DIR / "history.py"), title="Bug History Dossiers", icon=":material/history:")
analytics_page = st.Page(str(VIEWS_DIR / "analytics.py"), title="Engineering Analytics", icon=":material/analytics:")
health_page = st.Page(str(VIEWS_DIR / "health.py"), title="System Health", icon=":material/health_and_safety:")
settings_page = st.Page(str(VIEWS_DIR / "settings.py"), title="Platform Settings", icon=":material/settings:")

# Grouped enterprise navigation
pg = st.navigation({
    "Core Triage": [dashboard_page, analyze_page, batch_page, duplicates_page],
    "Analytics & Audit": [history_page, analytics_page],
    "Platform Governance": [health_page, settings_page],
})

# Sidebar Brand Header & Real-Time Status Indicators
with st.sidebar:
    st.markdown("""
<div style="padding: 12px 0 16px 0; border-bottom: 1px solid #1f2937; margin-bottom: 12px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 1.6rem;">🛡️</span>
        <div>
            <div style="font-weight: 800; font-size: 1.15rem; color: #ffffff; letter-spacing: -0.02em;">BugSense<span style="color: #3b82f6;">AI</span></div>
            <div style="font-size: 0.72rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em;">AI Bug Intelligence Platform</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Real-time health status widget
    try:
        health = check_backend_status()
        is_healthy = health.get("status") == "healthy"
        status_color = "#10b981" if is_healthy else "#f59e0b"
        status_text = "Operational" if is_healthy else "Degraded Mode"
        llm_model = health.get("llm_model", "gemini-flash-lite-latest")

        st.markdown(f"""
<div style="background: rgba(17, 24, 39, 0.7); border: 1px solid #1f2937; border-radius: 8px; padding: 10px 12px; margin-bottom: 16px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-size: 0.75rem; color: #9ca3af;">STATUS</span>
        <span style="font-size: 0.75rem; font-weight: 600; color: {status_color};">● {status_text}</span>
    </div>
    <div style="font-size: 0.75rem; color: #6b7280;">Model: <span style="color: #cbd5e1;">{llm_model}</span></div>
</div>
""", unsafe_allow_html=True)
    except Exception:
        pass

# Execute the routed page
pg.run()
