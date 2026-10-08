"""
BugSenseAI — Section 5: Duplicate & Similar Issues
Semantic vector duplicate detection with cosine similarity scoring,
automated match explanation, and side-by-side comparison.
"""

import streamlit as st
import json
from frontend.api_client import fetch_duplicate_matches, fetch_history, trigger_vector_sync
from frontend.styles import render_header, get_severity_badge


def show():
    render_header(
        title="Duplicate & Semantic Similarity Engine",
        subtitle="Detect redundant bug filings using high-dimensional dense vector embeddings and cosine similarity",
        badge="SEMANTIC SEARCH"
    )

    # Re-sync button
    col_t, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("🔄 Sync Vector Index", help="Index all past triaged reports into vector store"):
            with st.spinner("Syncing embeddings..."):
                synced = trigger_vector_sync()
                st.success(f"Vector index synced! {synced} new entries added.")
                st.rerun()

    # Select Mode: Query active triage or select from history
    history = fetch_history(limit=50).get("items", [])
    
    query_mode = st.radio(
        "Choose Comparison Source:",
        ["Current Active Triage Result", "Select Existing Bug from History", "Enter Custom Query Text"],
        horizontal=True
    )

    candidate_bug = None

    if query_mode == "Current Active Triage Result":
        candidate_bug = st.session_state.get("triage_result")
        if not candidate_bug:
            st.info("No active bug triage found in memory. Please run an analysis in 'Analyze Bug' or select from History below.")
            if history:
                st.markdown("##### Quick Select from Recent History:")
                chosen_idx = st.selectbox(
                    "Select report to test similarity against:",
                    range(len(history)),
                    format_func=lambda i: f"[{history[i].get('severity', 'P3')}] {history[i].get('title', 'Untitled')}"
                )
                candidate_bug = history[chosen_idx]
    elif query_mode == "Select Existing Bug from History":
        if history:
            chosen_idx = st.selectbox(
                "Select historical bug report:",
                range(len(history)),
                format_func=lambda i: f"[{history[i].get('severity', 'P3')}] {history[i].get('title', 'Untitled')}"
            )
            candidate_bug = history[chosen_idx]
        else:
            st.warning("No history found in outputs/ directory.")
    else:
        custom_txt = st.text_area("Enter bug description to search against index:", height=100)
        if custom_txt.strip():
            candidate_bug = {
                "title": custom_txt[:60],
                "actual_behavior": custom_txt,
                "component": "Search Query",
                "severity": "P3"
            }

    if not candidate_bug:
        return

    st.markdown("<hr style='border-color: #242f48; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Run similarity query
    with st.spinner("Calculating cosine distances across vector index..."):
        matches = fetch_duplicate_matches(candidate_bug, top_k=5)

    st.markdown(f"### Query: **{candidate_bug.get('title', 'Target Bug')}**")
    st.markdown(f"**Component:** `{candidate_bug.get('component', 'General')}` · **Severity:** `{candidate_bug.get('severity', 'P3')}`")

    if not matches:
        st.markdown("""
<div style="background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10b981; padding: 14px 18px; border-radius: 4px; margin: 16px 0; color: #a7f3d0;">
    <strong>✓ Unique Issue:</strong> No existing reports exceed the similarity threshold (30%). This appears to be a genuinely novel bug report.
</div>
""", unsafe_allow_html=True)
        return

    st.markdown("#### Ranked Semantic Matches")
    for i, m in enumerate(matches):
        sim = m.get("similarity", 0.0)
        sim_color = "#ef4444" if sim >= 65 else ("#f59e0b" if sim >= 45 else "#3b82f6")
        is_dup_flag = "⚠️ HIGH DUPLICATE PROBABILITY" if sim >= 65 else "ℹ️ RELATED PATTERN"

        with st.expander(f"#{i+1} · {m.get('title')} — {sim}% Match ({is_dup_flag})", expanded=(i == 0)):
            m_col1, m_col2 = st.columns([1, 2])
            with m_col1:
                st.markdown(f"**Similarity Score:** <span style='font-size: 1.3rem; font-weight: 700; color: {sim_color};'>{sim}%</span>", unsafe_allow_html=True)
                st.markdown(f"**Ticket ID:** `{m.get('id', 'HIST')}`")
                st.markdown(f"**Component:** `{m.get('component', 'General')}`")
                st.markdown(f"**Severity:** `{m.get('severity', 'P3')}`")
            with m_col2:
                st.markdown(f"**Duplicate Rationale:**\n\n{m.get('explanation', 'High feature overlap')}")
                st.markdown(f"**Summary:** {m.get('summary', 'No summary available')}")

            # Side-by-Side Comparison
            st.markdown("<h5 style='margin-top: 16px;'>Side-by-Side Comparison</h5>", unsafe_allow_html=True)
            cmp_left, cmp_right = st.columns(2)
            with cmp_left:
                st.markdown("""
<div style="background: #101623; border: 1px solid #1e283d; border-radius: 6px; padding: 12px;">
    <strong style="color: #60a5fa;">CURRENT BUG</strong>
</div>
""", unsafe_allow_html=True)
                st.markdown(f"**Title:** {candidate_bug.get('title', '-')}")
                st.markdown(f"**Component:** {candidate_bug.get('component', '-')}")
                st.markdown(f"**Actual Behavior:**\n\n{candidate_bug.get('actual_behavior', '-')}")
            with cmp_right:
                st.markdown("""
<div style="background: #101623; border: 1px solid #1e283d; border-radius: 6px; padding: 12px;">
    <strong style="color: #34d399;">MATCHED HISTORICAL REPORT</strong>
</div>
""", unsafe_allow_html=True)
                st.markdown(f"**Title:** {m.get('title', '-')}")
                st.markdown(f"**Component:** {m.get('component', '-')}")
                st.markdown(f"**Actual Behavior:**\n\n{m.get('actual_behavior', '-')}")


if __name__ == "__main__":
    show()
