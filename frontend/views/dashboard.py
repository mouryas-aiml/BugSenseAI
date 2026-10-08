"""
BugSenseAI — Section 1: Executive Dashboard
Comprehensive platform metrics, severity breakdowns, human review alerts,
and recent triage activity.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from frontend.api_client import fetch_analytics, check_backend_status
from frontend.styles import render_header, render_metric, get_severity_badge, get_confidence_badge


def show():
    render_header(
        title="Executive Bug Intelligence Dashboard",
        subtitle="Operational triage overview, severity distribution, and quality metrics across active software repositories",
        badge="ENTERPRISE MONITORING"
    )

    # 1. Fetch live metrics
    with st.spinner("Fetching system intelligence..."):
        analytics = fetch_analytics()
        health = check_backend_status()

    # System Status Banner
    backend_mode = health.get("mode", "unknown")
    status_color = "#10b981" if health.get("status") == "healthy" else "#f59e0b"
    engine_label = "FastAPI Service (Port 8000)" if health.get("reachable") else "Direct In-Process Engine"
    
    st.markdown(f"""
<div style="background: rgba(16, 22, 35, 0.7); border: 1px solid #1e283d; border-radius: 8px; padding: 10px 16px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="height: 10px; width: 10px; border-radius: 50%; background-color: {status_color}; display: inline-block;"></span>
        <span style="font-size: 0.85rem; color: #9ca3af;">AI Engine: <strong style="color: #f3f4f6;">Google Gemini ({health.get('llm_model', 'gemini-flash-lite-latest')})</strong></span>
        <span style="color: #4b5563;">|</span>
        <span style="font-size: 0.85rem; color: #9ca3af;">Runtime: <strong style="color: #f3f4f6;">{engine_label}</strong></span>
    </div>
    <div>
        <span style="font-size: 0.8rem; background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(59, 130, 246, 0.3);">Vector Index: {health.get('vector_store_entries', 0)} bugs</span>
    </div>
</div>
""", unsafe_allow_html=True)

    # 2. Key KPI Metric Cards (User requested: Total, P1-P4, Human review, Duplicates, Avg confidence, Avg completeness)
    total_reports = analytics.get("total_reports", 0)
    sev_dist = analytics.get("severity_distribution", {})
    p1 = sev_dist.get("P1", 0)
    p2 = sev_dist.get("P2", 0)
    p3 = sev_dist.get("P3", 0)
    p4 = sev_dist.get("P4", 0)
    review_req = analytics.get("requires_human_review_count", 0)
    duplicates = analytics.get("duplicate_count", 0)
    avg_comp = analytics.get("avg_completeness_score", 0.0)

    # Calculate average confidence
    conf_dist = analytics.get("confidence_distribution", {})
    high_c = conf_dist.get("High", 0)
    med_c = conf_dist.get("Medium", 0)
    low_c = conf_dist.get("Low", 0)
    top_conf = "High" if high_c >= med_c and high_c >= low_c else ("Medium" if med_c >= low_c else "Low")
    if total_reports == 0:
        top_conf = "N/A"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Total Bugs Analyzed", total_reports, "Processed through AI pipeline")
    with col2:
        render_metric("Critical & High (P1/P2)", f"{p1 + p2}", f"P1: {p1} · P2: {p2}")
    with col3:
        render_metric("Human Review Required", review_req, "Ambiguous or critical bugs")
    with col4:
        render_metric("Duplicate Bugs Detected", duplicates, "Semantic vector matches")

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        render_metric("Medium & Low (P3/P4)", f"{p3 + p4}", f"P3: {p3} · P4: {p4}")
    with col6:
        render_metric("Avg Completeness", f"{avg_comp}%", "Report quality heuristic")
    with col7:
        render_metric("Dominant Confidence", top_conf, f"High: {high_c} · Med: {med_c} · Low: {low_c}")
    with col8:
        render_metric("Active Vector Index", health.get("vector_store_entries", 0), "Stored semantic fingerprints")

    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

    # 3. Charts Section
    st.subheader("Severity & Component Intelligence")
    c_chart1, c_chart2 = st.columns([1, 1])

    with c_chart1:
        # Severity Distribution Chart
        sev_df = pd.DataFrame([
            {"Severity": "P1 · Critical", "Count": p1, "Color": "#ef4444"},
            {"Severity": "P2 · High", "Count": p2, "Color": "#f59e0b"},
            {"Severity": "P3 · Medium", "Count": p3, "Color": "#3b82f6"},
            {"Severity": "P4 · Low", "Count": p4, "Color": "#10b981"},
        ])
        fig_sev = px.bar(
            sev_df,
            x="Severity",
            y="Count",
            color="Severity",
            color_discrete_map={
                "P1 · Critical": "#ef4444",
                "P2 · High": "#f59e0b",
                "P3 · Medium": "#3b82f6",
                "P4 · Low": "#10b981",
            },
            title="Severity Tier Distribution",
        )
        fig_sev.update_layout(
            template="plotly_dark",
            paper_bgcolor="#151d2e",
            plot_bgcolor="#151d2e",
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            height=280,
            xaxis=dict(gridcolor="#1f2937"),
            yaxis=dict(gridcolor="#1f2937"),
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    with c_chart2:
        # Component Breakdown
        comp_dist = analytics.get("component_distribution", {})
        if comp_dist:
            top_comps = list(comp_dist.items())[:6]
            comp_df = pd.DataFrame(top_comps, columns=["Component", "Count"])
            fig_comp = px.pie(
                comp_df,
                names="Component",
                values="Count",
                title="Top Affected Components",
                hole=0.45,
                color_discrete_sequence=["#3b82f6", "#06b6d4", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981"]
            )
            fig_comp.update_layout(
                template="plotly_dark",
                paper_bgcolor="#151d2e",
                plot_bgcolor="#151d2e",
                margin=dict(l=20, r=20, t=40, b=20),
                height=280,
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No component data available yet. Triage bug reports to populate breakdown.")

    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

    # 4. Recent Activity Feed
    st.subheader("Recent Triage Activity")
    recent = analytics.get("recent_reports", [])
    if recent:
        table_rows = []
        for r in recent:
            sev_badge = get_severity_badge(r.get("severity", "P3"))
            conf_badge = get_confidence_badge(r.get("confidence", "Medium"))
            comp_score = r.get("completeness_score", 0)
            score_color = "#10b981" if comp_score >= 70 else ("#f59e0b" if comp_score >= 40 else "#ef4444")
            
            table_rows.append({
                "Timestamp": r.get("timestamp", "-"),
                "Bug Title": r.get("title", "Untitled"),
                "Severity": sev_badge,
                "Component": r.get("component") or "Unassigned",
                "Assignee Team": r.get("team") or "Triage Team",
                "Confidence": conf_badge,
                "Completeness": f"<span style='color:{score_color}; font-weight:600;'>{comp_score}%</span>",
            })
        
        df_html = pd.DataFrame(table_rows).to_html(escape=False, index=False)
        st.markdown(f"""
<div style="background-color: #151d2e; border: 1px solid #242f48; border-radius: 8px; overflow-x: auto;">
    <style>
        table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; color: #e5e7eb; }}
        th {{ background-color: #101623; color: #9ca3af; text-align: left; padding: 12px 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.75rem; border-bottom: 1px solid #242f48; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid #1e283d; }}
        tr:hover td {{ background-color: #1c263c; }}
    </style>
    {df_html}
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background-color: #151d2e; border: 1px dashed #374151; border-radius: 8px; padding: 32px; text-align: center;">
    <p style="color: #9ca3af; margin-bottom: 8px;">No triage history recorded yet.</p>
    <p style="color: #6b7280; font-size: 0.85rem;">Run your first bug analysis using the 'Analyze Bug' tab or upload batch files.</p>
</div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    show()
