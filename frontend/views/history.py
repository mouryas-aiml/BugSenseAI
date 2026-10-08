"""
BugSenseAI — Section 6: Bug History
Searchable, filterable repository of all past triage results with expandable
intelligence dossiers and export.
"""

import streamlit as st
import pandas as pd
import json
import io
from frontend.api_client import fetch_history
from frontend.styles import render_header, get_severity_badge, get_confidence_badge


def show():
    render_header(
        title="Bug Intelligence History",
        subtitle="Search, filter, and audit past triaged bug intelligence dossiers",
        badge="HISTORICAL AUDIT"
    )

    with st.spinner("Loading triage records..."):
        history_res = fetch_history(limit=100)
        items = history_res.get("items", [])

    if not items:
        st.info("No historical bug reports found in outputs/ directory.")
        return

    # 1. Search & Filter Bar
    s_col, f1_col, f2_col, f3_col = st.columns([2, 1, 1, 1])

    with s_col:
        search_query = st.text_input("🔍 Search reports (title, summary, component, errors):", placeholder="e.g. checkout, timeout, NPE")

    with f1_col:
        sev_options = ["All", "P1", "P2", "P3", "P4"]
        selected_sev = st.selectbox("Severity:", sev_options)

    with f2_col:
        conf_options = ["All", "High", "Medium", "Low"]
        selected_conf = st.selectbox("Confidence:", conf_options)

    with f3_col:
        review_options = ["All", "Review Required", "Automated Pass"]
        selected_review = st.selectbox("Review Status:", review_options)

    # 2. Filter logic
    filtered = []
    for item in items:
        # Text search
        if search_query:
            q = search_query.lower()
            text_corpus = (
                item.get("title", "") + " " +
                item.get("summary", "") + " " +
                item.get("component", "") + " " +
                " ".join(item.get("error_messages", []))
            ).lower()
            if q not in text_corpus:
                continue

        # Severity filter
        item_sev = item.get("severity", "P3").replace("Severity.", "")
        if selected_sev != "All" and item_sev != selected_sev:
            continue

        # Confidence filter
        item_conf = item.get("confidence", "Medium")
        if selected_conf != "All" and item_conf != selected_conf:
            continue

        # Review status filter
        needs_review = item.get("requires_human_review", False) or "needs-human-review" in item.get("suggested_labels", [])
        if selected_review == "Review Required" and not needs_review:
            continue
        elif selected_review == "Automated Pass" and needs_review:
            continue

        filtered.append(item)

    st.markdown(f"Showing **{len(filtered)}** of **{len(items)}** recorded bug reports.")

    # 3. Render List with Detailed Expanders
    for i, report in enumerate(filtered):
        sev = report.get("severity", "P3").replace("Severity.", "")
        title = report.get("title", "Untitled")
        timestamp = report.get("_timestamp", "-")
        comp = report.get("component", "General")
        conf = report.get("confidence", "Medium")
        comp_score = report.get("completeness_score", 0)
        needs_review = report.get("requires_human_review", False)

        sev_badge = get_severity_badge(sev)
        conf_badge = get_confidence_badge(conf)
        rev_badge = "⚠️ Needs Review" if needs_review else "✓ Verified"

        expander_title = f"[{sev}] {title} — {comp} ({timestamp})"

        with st.expander(expander_title):
            c_top1, c_top2 = st.columns([2, 1])
            with c_top1:
                st.markdown(f"**Executive Summary:**\n\n{report.get('summary', 'No summary available.')}")
                st.markdown(f"**Impact Statement:** {report.get('impact', 'Not specified')}")
            with c_top2:
                st.markdown(f"**Assigned Team:** `{report.get('suggested_assignee_team', 'Triage')}`")
                st.markdown(f"**Completeness Score:** `{comp_score}%`")
                st.markdown(f"**Review Status:** `{rev_badge}`")

            st.markdown("---")

            # Technical breakdown
            tech_c1, tech_c2 = st.columns(2)
            with tech_c1:
                st.markdown("**Reproduction Steps:**")
                steps = report.get("reproduction_steps", [])
                if steps:
                    for s in steps:
                        st.markdown(f"- {s}")
                else:
                    st.markdown("_[None provided]_")

                st.markdown(f"**Expected:** {report.get('expected_behavior', '-')}")
                st.markdown(f"**Actual:** {report.get('actual_behavior', '-')}")

            with tech_c2:
                st.markdown(f"**Root Cause Hypothesis:**\n\n_{report.get('root_cause_hypothesis', '-')}_")
                st.markdown(f"**Environment:** `{report.get('environment', '-')}`")
                entities = report.get("extracted_entities", [])
                if entities:
                    st.markdown("**Entities:** " + " ".join([f"`{e}`" for e in entities]))

            st.download_button(
                "📥 Download Triage JSON",
                data=json.dumps(report, indent=2),
                file_name=f"{report.get('_filename', 'triage.json')}",
                mime="application/json",
                key=f"dl_{i}"
            )


if __name__ == "__main__":
    show()
