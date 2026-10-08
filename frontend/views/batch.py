"""
BugSenseAI — Section 4: Batch Analysis
Process multiple bug reports from CSV, JSON, or TXT file uploads with live progress
tracking, severity filtering, and bulk intelligence export.
"""

import streamlit as st
import pandas as pd
import json
import time
import io
from frontend.api_client import triage_batch_bugs
from frontend.styles import render_header, render_metric, get_severity_badge


def show():
    render_header(
        title="Batch Bug Intelligence Processing",
        subtitle="Ingest and triage bulk datasets from bug trackers, legacy systems, or support exports",
        badge="BULK INGESTION"
    )

    st.markdown("#### Upload Bug Dataset")
    uploaded_file = st.file_uploader(
        "Upload CSV, JSON, or TXT file containing bug reports (max 20 per batch recommended):",
        type=["csv", "json", "txt"],
        help="Upload CSV with a text column, JSON array of report strings, or plain text with reports separated by '---'"
    )

    reports = []
    if uploaded_file is not None:
        filename = uploaded_file.name
        content = uploaded_file.getvalue()

        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(content))
                text_cols = [c for c in df.columns if df[c].dtype == "object"]
                if not text_cols:
                    st.error("No text columns detected in uploaded CSV.")
                    return
                selected_col = st.selectbox("Select column containing bug reports:", text_cols)
                reports = df[selected_col].dropna().astype(str).tolist()

            elif filename.endswith(".json"):
                data = json.loads(content.decode("utf-8"))
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            reports.append(item)
                        elif isinstance(item, dict):
                            # Try common bug field names
                            val = item.get("bug") or item.get("description") or item.get("text") or item.get("title")
                            if val:
                                reports.append(str(val))
                elif isinstance(data, dict):
                    reports = data.get("reports", [])

            elif filename.endswith(".txt"):
                raw_text = content.decode("utf-8")
                # Split by delimiter if present
                if "---" in raw_text:
                    reports = [r.strip() for r in raw_text.split("---") if r.strip()]
                else:
                    reports = [r.strip() for r in raw_text.split("\n\n") if r.strip()]

        except Exception as e:
            st.error(f"Failed to parse uploaded file: {e}")
            return

        st.info(f"Loaded **{len(reports)}** bug reports from `{filename}`.")

        # Limit to 20 per batch for reasonable API latency
        if len(reports) > 20:
            st.warning("Capping batch size to 20 reports to respect rate limits.")
            reports = reports[:20]

        if st.button("⚡ Start Batch Triage", type="primary"):
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            status_text.text("Initiating batch AI triage pipeline...")
            batch_result = triage_batch_bugs(reports, filename=filename)
            progress_bar.progress(1.0)
            status_text.text("Batch processing complete!")
            st.session_state["batch_results"] = batch_result

    # Display Batch Results
    batch_data = st.session_state.get("batch_results")
    if batch_data:
        st.markdown("<hr style='border-color: #242f48; margin: 24px 0;'>", unsafe_allow_html=True)
        
        total = batch_data.get("total", 0)
        succeeded = batch_data.get("succeeded", 0)
        failed = batch_data.get("failed", 0)
        results = batch_data.get("results", [])

        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric("Total Ingested", total, "Batch volume")
        with col2:
            render_metric("Successfully Triaged", succeeded, f"{round((succeeded/total)*100, 1) if total else 0}% success rate")
        with col3:
            render_metric("Failed", failed, "Errors during processing")
        with col4:
            # Count P1s
            p1_count = sum(1 for r in results if r.get("triage") and r["triage"].get("severity", "").endswith("P1"))
            render_metric("Critical P1 Identified", p1_count, "Urgent production triage")

        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

        # Build table records
        table_rows = []
        full_records = []

        for r in results:
            triage = r.get("triage")
            if triage:
                sev = triage.get("severity", "P3").replace("Severity.", "")
                table_rows.append({
                    "Index": r.get("index", 0) + 1,
                    "Title": triage.get("title", "Untitled"),
                    "Severity": sev,
                    "Component": triage.get("component", "General"),
                    "Team": triage.get("suggested_assignee_team", "Triage"),
                    "Confidence": triage.get("confidence", "Medium"),
                    "Latency (ms)": r.get("processing_time_ms", 0),
                })
                full_records.append(triage)
            else:
                table_rows.append({
                    "Index": r.get("index", 0) + 1,
                    "Title": r.get("input_preview", "Failed"),
                    "Severity": "ERROR",
                    "Component": "N/A",
                    "Team": "N/A",
                    "Confidence": "N/A",
                    "Latency (ms)": r.get("processing_time_ms", 0),
                })

        # Filter controls
        st.markdown("#### Results Filter")
        f_col1, f_col2 = st.columns([1, 1])
        with f_col1:
            all_sevs = sorted(list(set(row["Severity"] for row in table_rows)))
            sev_filter = st.multiselect("Filter by Severity:", all_sevs, default=all_sevs)
        with f_col2:
            all_comps = sorted(list(set(row["Component"] for row in table_rows)))
            comp_filter = st.multiselect("Filter by Component:", all_comps, default=all_comps)

        filtered_rows = [
            r for r in table_rows
            if r["Severity"] in sev_filter and r["Component"] in comp_filter
        ]

        if filtered_rows:
            df_display = pd.DataFrame(filtered_rows)
            st.dataframe(df_display, use_container_width=True)

        # Export Controls
        st.markdown("#### Export Batch Intelligence")
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            csv_buf = io.StringIO()
            pd.DataFrame(table_rows).to_csv(csv_buf, index=False)
            st.download_button(
                "📥 Export Summary CSV",
                data=csv_buf.getvalue(),
                file_name=f"batch_triage_summary_{int(time.time())}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with e_col2:
            st.download_button(
                "📥 Export Full Structured JSON",
                data=json.dumps(full_records, indent=2),
                file_name=f"batch_triage_full_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    show()
