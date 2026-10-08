"""
BugSenseAI — Enterprise Design System & Styling
Sleek, high-contrast dark theme with consistent visual hierarchy,
typography, badges, metric cards, and provenance indicators.
"""

import streamlit as st


def apply_theme():
    """Inject modern enterprise CSS styling into Streamlit."""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Reset & Root Variables */
:root {
    --bg-primary: #0a0e17;
    --bg-secondary: #101623;
    --bg-card: #151d2e;
    --bg-card-hover: #1c263c;
    --border-color: #242f48;
    --border-subtle: #1e283d;
    --text-primary: #f3f4f6;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --p1-red: #ef4444;
    --p2-amber: #f59e0b;
    --p3-blue: #3b82f6;
    --p4-green: #10b981;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* App Canvas */
.stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

/* Hide default clutter */
#MainMenu, footer { visibility: hidden !important; }
header { background: transparent !important; }

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    padding-top: 1rem;
}

/* Typography */
h1 {
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: #ffffff !important;
    margin-bottom: 0.25rem !important;
}

h2 {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: #f3f4f6 !important;
    margin-top: 1.25rem !important;
}

h3 {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: #e5e7eb !important;
}

p, span, label {
    color: var(--text-secondary);
}

/* Enterprise Header Card */
.enterprise-header {
    background: linear-gradient(135deg, rgba(30, 41, 67, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
}

.header-badge {
    display: inline-block;
    padding: 3px 10px;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.35);
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #60a5fa;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

/* Metric Cards */
.metric-container {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1.15rem 1.25rem;
    transition: all 0.2s ease;
    height: 100%;
}
.metric-container:hover {
    border-color: #3b82f6;
    background-color: var(--bg-card-hover);
}
.metric-title {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.35rem;
}
.metric-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
}
.metric-sub {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.35rem;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.65rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-p1 {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
}
.badge-p2 {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.35);
}
.badge-p3 {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.35);
}
.badge-p4 {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.35);
}

.badge-conf-high {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.badge-conf-medium {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
.badge-conf-low {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Provenance Tags: Fact vs Inference vs Rule */
.provenance-tag {
    font-size: 0.68rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-right: 6px;
    vertical-align: middle;
}
.tag-fact {
    background: rgba(59, 130, 246, 0.2);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.4);
}
.tag-inference {
    background: rgba(168, 85, 247, 0.2);
    color: #d8b4fe;
    border: 1px solid rgba(168, 85, 247, 0.4);
}
.tag-rule {
    background: rgba(20, 184, 166, 0.2);
    color: #5eead4;
    border: 1px solid rgba(20, 184, 166, 0.4);
}

/* Structured AI Output Box */
.intelligence-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.intelligence-card-header {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 0.5rem;
    margin-bottom: 0.85rem;
}

/* Alert Boxes */
.alert-missing {
    background: rgba(239, 68, 68, 0.08);
    border-left: 4px solid #ef4444;
    padding: 0.85rem 1.15rem;
    border-radius: 4px;
    margin: 0.75rem 0;
    color: #fca5a5;
    font-size: 0.9rem;
}
.alert-pii {
    background: rgba(16, 185, 129, 0.08);
    border-left: 4px solid #10b981;
    padding: 0.85rem 1.15rem;
    border-radius: 4px;
    margin: 0.75rem 0;
    color: #6ee7b7;
    font-size: 0.9rem;
}

/* Code & Monospace */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #1e2638 !important;
    color: #e2e8f0 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.85rem !important;
}

/* Buttons */
.stButton>button {
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

/* Inputs */
.stTextArea textarea, .stTextInput input {
    background-color: #101623 !important;
    border: 1px solid #242f48 !important;
    color: #f3f4f6 !important;
    border-radius: 8px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 1px #3b82f6 !important;
}
</style>
""", unsafe_allow_html=True)


def render_header(title: str, subtitle: str, badge: str = "TCS AI PLATFORM"):
    """Render high-polish enterprise header banner."""
    st.markdown(f"""
<div class="enterprise-header">
    <div class="header-badge">{badge}</div>
    <h1>{title}</h1>
    <p style="margin: 0; color: #9ca3af; font-size: 0.95rem;">{subtitle}</p>
</div>
""", unsafe_allow_html=True)


def get_severity_badge(severity: str) -> str:
    s = (severity or "P3").upper().replace("SEVERITY.", "")
    cls_map = {"P1": "badge-p1", "P2": "badge-p2", "P3": "badge-p3", "P4": "badge-p4"}
    cls = cls_map.get(s, "badge-p3")
    label_map = {"P1": "P1 · Critical", "P2": "P2 · High", "P3": "P3 · Medium", "P4": "P4 · Low"}
    return f'<span class="badge {cls}">{label_map.get(s, s)}</span>'


def get_confidence_badge(confidence: str) -> str:
    c = (confidence or "Medium").capitalize()
    cls_map = {"High": "badge-conf-high", "Medium": "badge-conf-medium", "Low": "badge-conf-low"}
    cls = cls_map.get(c, "badge-conf-medium")
    return f'<span class="badge {cls}">{c} Confidence</span>'


def render_metric(label: str, value: Any, sub: str = ""):
    """Render a clean enterprise metric box."""
    st.markdown(f"""
<div class="metric-container">
    <div class="metric-title">{label}</div>
    <div class="metric-value">{value}</div>
    <div class="metric-sub">{sub}</div>
</div>
""", unsafe_allow_html=True)
