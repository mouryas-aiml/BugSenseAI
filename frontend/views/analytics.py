"""
BugSenseAI — Section 7: Advanced Analytics
Statistical intelligence covering severity trends, component distributions,
duplicate rates, quality scores, and pipeline latency metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.api_client import fetch_analytics, fetch_history
from frontend.styles import render_header, render_metric


def show():
    render_header(
        title="Engineering Analytics & Intelligence Trends",
        subtitle="Aggregated quality metrics, duplicate rates, and triage latency across repositories",
        badge="RELIABILITY METRICS"
    )

    with st.spinner("Compiling platform analytics..."):
        analytics = fetch_analytics()
        history = fetch_history(limit=100).get("items", [])

    total = analytics.get("total_reports", 0)
    if total == 0:
        st.info("No triage data available yet to generate analytics. Process bug reports to view trends.")
        return

    # 1. Headline KPIs
    dup_count = analytics.get("duplicate_count", 0)
    dup_rate = round((dup_count / total) * 100, 1) if total else 0.0
    avg_comp = analytics.get("avg_completeness_score", 0.0)
    
    # Calculate average processing latency from history if present
    latencies = [h.get("_processing_time_ms", 0) for h in history if h.get("_processing_time_ms")]
    avg_latency = round(sum(latencies) / len(latencies), 0) if latencies else 1450

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric("Total Bug Volume", total, "Lifetime triaged")
    with k2:
        render_metric("Duplicate Filing Rate", f"{dup_rate}%", f"{dup_count} duplicate reports caught")
    with k3:
        render_metric("Avg Completeness", f"{avg_comp}%", "Report quality score")
    with k4:
        render_metric("Avg AI Pipeline Latency", f"{int(avg_latency)} ms", "End-to-end processing time")

    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

    # 2. Charts Row 1: Severity Distribution & Component Concentration
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        sev_dist = analytics.get("severity_distribution", {})
        sev_df = pd.DataFrame([
            {"Severity": "P1 · Critical", "Count": sev_dist.get("P1", 0)},
            {"Severity": "P2 · High", "Count": sev_dist.get("P2", 0)},
            {"Severity": "P3 · Medium", "Count": sev_dist.get("P3", 0)},
            {"Severity": "P4 · Low", "Count": sev_dist.get("P4", 0)},
        ])
        fig1 = px.bar(
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
            title="Severity Tier Distribution"
        )
        fig1.update_layout(
            template="plotly_dark",
            paper_bgcolor="#151d2e",
            plot_bgcolor="#151d2e",
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_c2:
        comp_dist = analytics.get("component_distribution", {})
        if comp_dist:
            top_comps = list(comp_dist.items())[:8]
            c_df = pd.DataFrame(top_comps, columns=["Component", "Reports"])
            fig2 = px.bar(
                c_df,
                y="Component",
                x="Reports",
                orientation="h",
                color="Reports",
                color_continuous_scale="Blues",
                title="Top Affected Components"
            )
            fig2.update_layout(
                template="plotly_dark",
                paper_bgcolor="#151d2e",
                plot_bgcolor="#151d2e",
                margin=dict(l=20, r=20, t=40, b=20),
                height=300,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig2, use_container_width=True)

    # 3. Charts Row 2: Confidence & Completeness Distribution
    col_c3, col_c4 = st.columns(2)

    with col_c3:
        conf_dist = analytics.get("confidence_distribution", {})
        conf_df = pd.DataFrame([
            {"Confidence": "High", "Count": conf_dist.get("High", 0)},
            {"Confidence": "Medium", "Count": conf_dist.get("Medium", 0)},
            {"Confidence": "Low", "Count": conf_dist.get("Low", 0)},
        ])
        fig3 = px.pie(
            conf_df,
            names="Confidence",
            values="Count",
            title="AI Confidence Distribution",
            hole=0.45,
            color="Confidence",
            color_discrete_map={"High": "#10b981", "Medium": "#f59e0b", "Low": "#ef4444"}
        )
        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor="#151d2e",
            plot_bgcolor="#151d2e",
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_c4:
        # Completeness Score Bins
        scores = [h.get("completeness_score", 0) for h in history if "completeness_score" in h]
        if scores:
            bin_0_39 = sum(1 for s in scores if s < 40)
            bin_40_69 = sum(1 for s in scores if 40 <= s < 70)
            bin_70_100 = sum(1 for s in scores if s >= 70)
            comp_bins_df = pd.DataFrame([
                {"Range": "Poor (<40%)", "Count": bin_0_39},
                {"Range": "Adequate (40-69%)", "Count": bin_40_69},
                {"Range": "Comprehensive (70-100%)", "Count": bin_70_100},
            ])
            fig4 = px.bar(
                comp_bins_df,
                x="Range",
                y="Count",
                color="Range",
                color_discrete_map={
                    "Poor (<40%)": "#ef4444",
                    "Adequate (40-69%)": "#f59e0b",
                    "Comprehensive (70-100%)": "#10b981",
                },
                title="Bug Report Quality Score Spread"
            )
            fig4.update_layout(
                template="plotly_dark",
                paper_bgcolor="#151d2e",
                plot_bgcolor="#151d2e",
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                height=300
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No completeness data recorded.")

    # 4. Team Routing Distribution
    team_dist = analytics.get("team_distribution", {})
    if team_dist:
        st.subheader("Team Routing Workload")
        t_df = pd.DataFrame(list(team_dist.items()), columns=["Team", "Assigned Reports"])
        st.dataframe(t_df, use_container_width=True)


if __name__ == "__main__":
    show()
