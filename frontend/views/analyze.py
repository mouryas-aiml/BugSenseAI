"""
BugSenseAI — Sections 2 & 3: Analyze Bug & Complete Structured AI Result
Interactive triage interface with sample presets, PII anonymization feedback,
rigorous fact-vs-inference provenance, and human-in-the-loop actions.
"""

import streamlit as st
import json
import time
from frontend.api_client import triage_single_bug, fetch_duplicate_matches
from frontend.styles import render_header, get_severity_badge, get_confidence_badge

# Presets representing real-world bug reports
SAMPLE_PRESETS = {
    "Critical Checkout 500 (P1)": """When clicking 'Checkout' on the cart page (Chrome 122, macOS Sonoma), the page hangs with a spinning loader and never completes.
Browser console logs show:
Uncaught TypeError: Cannot read properties of undefined (reading 'paymentMethodId') at checkout.js:142
Network tab shows POST /api/v1/orders/checkout returned HTTP 500 Internal Server Error:
{"error": "NullPointerException: customer default payment method is null"}
Affecting roughly 15% of guest checkout attempts since v2.4.1 deployment yesterday.
Steps: 1. Add item to cart. 2. Proceed as guest. 3. Click Checkout.
Expected: Order confirmation page with order ID.
Actual: Infinite spinner, order not created, charge not processed.
Contact: john.smith@enterprise-corp.com, Server IP: 192.168.1.105""",

    "Enterprise Export Timeout (P2)": """Data export to CSV fails for accounts with more than 50,000 records on the Analytics page.
Error message: '504 Gateway Timeout: upstream request timed out after 30000ms'.
Affects all Tier-1 enterprise customers attempting monthly billing reconciliation.
Workaround: Exporting date ranges shorter than 7 days succeeds.
Browser: Any browser, Environment: Production US-East.""",

    "Vague User Report (Needs Review)": """the website feels very laggy today and something broke on my screen. please fix this asap its urgent!""",

    "UI Dark Mode Contrast Glitch (P4)": """On the user profile settings page in Dark Mode, the 'Save Changes' button text is dark gray (#333333) against a dark navy button background (#1a1a2e), making it unreadable.
Clicking the button still saves changes normally.
Reproducible on Firefox 123, Windows 11."""
}


def show():
    render_header(
        title="AI Bug Intelligence & Automated Triage",
        subtitle="Transform raw, unstructured bug reports into verified, structured engineering intelligence",
        badge="REAL-TIME AI ANALYSIS"
    )

    # 1. Input & Controls
    col_input, col_meta = st.columns([2.2, 1])

    with col_meta:
        st.markdown("#### Sample Presets")
        selected_sample = st.selectbox(
            "Load realistic example",
            ["-- Select a sample --"] + list(SAMPLE_PRESETS.keys()),
            help="Pre-loaded realistic bug scenarios showcasing different severity tiers and edge cases"
        )
        if selected_sample != "-- Select a sample --":
            st.session_state["raw_bug_input"] = SAMPLE_PRESETS[selected_sample]

        st.markdown("#### Optional Metadata")
        meta_env = st.selectbox("Environment", ["Not specified", "Production", "Staging", "QA / Test", "Development"])
        meta_ver = st.text_input("Application Version", placeholder="e.g., v2.4.1")
        meta_reporter = st.text_input("Reporter / Team", placeholder="e.g., Support Tier 2")

    with col_input:
        st.markdown("#### Bug Report Input")
        raw_text = st.text_area(
            "Paste raw customer ticket, chat transcript, stack trace, or test failure:",
            value=st.session_state.get("raw_bug_input", ""),
            height=230,
            placeholder="Describe what happened, error codes, steps to reproduce, or paste logs..."
        )

        b_col1, b_col2 = st.columns([1, 2])
        with b_col1:
            analyze_clicked = st.button("🚀 Analyze with Gemini", type="primary", use_container_width=True)
        with b_col2:
            if st.button("Clear Input", use_container_width=False):
                st.session_state["raw_bug_input"] = ""
                st.session_state["triage_result"] = None
                st.rerun()

    # Trigger Analysis
    if analyze_clicked:
        if not raw_text.strip():
            st.error("Please provide bug report text before initiating analysis.")
            return

        metadata = {}
        if meta_env != "Not specified":
            metadata["environment"] = meta_env
        if meta_ver:
            metadata["version"] = meta_ver
        if meta_reporter:
            metadata["reporter"] = meta_reporter

        with st.status("Running AI Intelligence Pipeline...", expanded=True) as status:
            st.write("🔒 1. Scanning and anonymizing PII entities (emails, IPs, tokens)...")
            time.sleep(0.1)
            st.write("🧠 2. Deep semantic extraction via Google Gemini SDK...")
            t0 = time.time()
            
            try:
                result = triage_single_bug(raw_text, metadata=metadata)
                st.write(f"⚡ 3. Gemini reasoning completed in {round(time.time() - t0, 2)}s.")
                st.write("📐 4. Enforcing deterministic triage rules, quality scores & duplicate detection...")
                st.session_state["triage_result"] = result
                status.update(label="Triage Analysis Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Triage Failed", state="error", expanded=True)
                st.error(f"Analysis Error: {str(e)}")
                st.markdown("""
<div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 12px; margin-top: 10px; font-size: 0.85rem; color: #fca5a5;">
    <strong>Troubleshooting Guide:</strong><br>
    • Check that your <code>GEMINI_API_KEY</code> is configured in <code>.env</code>.<br>
    • Verify your internet connectivity to Google Generative AI endpoints.<br>
    • Visit the <strong>System Health</strong> tab for real-time diagnostics.
</div>
""", unsafe_allow_html=True)
                return

    # 2. Render Structured AI Result
    result = st.session_state.get("triage_result")
    if result:
        st.markdown("<hr style='border-color: #242f48; margin: 30px 0;'>", unsafe_allow_html=True)
        render_analysis_result(result)


def render_analysis_result(res: dict):
    """Render the full structured AI result complying with all TCS problem requirements."""
    
    # ── Top Summary Header Card ──
    title = res.get("title", "Untitled Bug Report")
    severity = res.get("severity", "P3")
    priority_reasoning = res.get("priority_reasoning", "")
    confidence = res.get("confidence", "Medium")
    comp_score = res.get("completeness_score", 0)
    requires_review = res.get("requires_human_review", False)
    component = res.get("component") or "Unassigned"
    team = res.get("suggested_assignee_team") or "Triage Team"
    routed_via = res.get("_routed_via", "AI Pipeline")

    sev_badge_html = get_severity_badge(severity)
    conf_badge_html = get_confidence_badge(confidence)
    review_badge_html = (
        '<span style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">⚠ HUMAN REVIEW REQUIRED</span>'
        if requires_review else
        '<span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">✓ AUTOMATED PASS</span>'
    )

    st.markdown(f"""
<div style="background-color: #151d2e; border: 1px solid #242f48; border-radius: 12px; padding: 20px 24px; margin-bottom: 24px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
        <div>
            <span style="font-size: 0.75rem; color: #60a5fa; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">AI TRIAGE INTELLIGENCE</span>
            <h2 style="margin: 4px 0 10px 0; font-size: 1.4rem; color: #ffffff;">{title}</h2>
        </div>
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            {sev_badge_html}
            {conf_badge_html}
            {review_badge_html}
        </div>
    </div>
    <div style="display: flex; gap: 20px; font-size: 0.85rem; color: #9ca3af; border-top: 1px solid #1e283d; padding-top: 12px; flex-wrap: wrap;">
        <div><strong>Component:</strong> <span style="color: #f3f4f6;">{component}</span></div>
        <div><strong>Assigned Team:</strong> <span style="color: #f3f4f6;">{team}</span></div>
        <div><strong>Report Completeness:</strong> <span style="color: {'#10b981' if comp_score>=70 else '#f59e0b'}; font-weight: 600;">{comp_score}%</span></div>
        <div><strong>Pipeline Engine:</strong> <span style="color: #cbd5e1;">{routed_via}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Privacy / PII Anonymization Feedback ──
    if res.get("_pii_redacted"):
        redaction_types = res.get("_pii_redaction_types", [])
        types_str = ", ".join(redaction_types) if redaction_types else "Sensitive Identifiers"
        st.markdown(f"""
<div class="alert-pii">
    <strong>🛡️ Privacy Protection Active:</strong> Automatically masked <strong>{types_str}</strong> prior to LLM processing. No sensitive customer PII was exposed externally.
</div>
""", unsafe_allow_html=True)

    # ── Missing Information / Human Review Required Warning ──
    missing_info = res.get("missing_information", [])
    if missing_info:
        items_html = "".join([f"<li>{item}</li>" for item in missing_info])
        st.markdown(f"""
<div class="alert-missing">
    <strong>⚠️ Information Missing — Human Input Required:</strong><br>
    The bug report lacks critical data for deterministic resolution. Maintenance engineers should verify:
    <ul style="margin: 6px 0 0 18px; padding: 0;">{items_html}</ul>
</div>
""", unsafe_allow_html=True)

    # ── Duplicate Alert ──
    if res.get("is_duplicate"):
        sim_bugs = res.get("similar_bugs", [])
        match_title = sim_bugs[0].get("title", "Related Issue") if sim_bugs else "Existing Ticket"
        match_score = sim_bugs[0].get("similarity", 0) if sim_bugs else 0
        st.markdown(f"""
<div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; color: #fde68a; font-size: 0.9rem;">
    <strong>👯 Potential Duplicate Detected:</strong> Matches <em>"{match_title}"</em> with <strong>{match_score}%</strong> semantic similarity. Review duplicate tab to avoid redundant work.
</div>
""", unsafe_allow_html=True)

    # ── Main 2-Column Intelligence Layout ──
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        # Executive Summary
        st.markdown("""
<div class="intelligence-card">
    <div class="intelligence-card-header"><span class="provenance-tag tag-inference">AI SYNTHESIS</span> Executive Summary</div>
""", unsafe_allow_html=True)
        st.markdown(f"**{res.get('summary', 'No summary generated.')}**")
        st.markdown("</div>", unsafe_allow_html=True)

        # Impact Analysis
        st.markdown("""
<div class="intelligence-card">
    <div class="intelligence-card-header"><span class="provenance-tag tag-inference">AI ANALYSIS</span> Impact & Blast Radius</div>
""", unsafe_allow_html=True)
        st.markdown(f"**Affected Users / Scope:** {res.get('affected_users', 'Unknown scope')}")
        st.markdown(f"**Operational Impact:** {res.get('impact', 'No impact description available')}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Expected vs Actual Behavior
        st.markdown("""
<div class="intelligence-card">
    <div class="intelligence-card-header"><span class="provenance-tag tag-fact">FACTS FROM REPORT</span> Expected vs Actual Behavior</div>
""", unsafe_allow_html=True)
        c_exp, c_act = st.columns(2)
        with c_exp:
            st.markdown(f"**Expected:**\n\n{res.get('expected_behavior', 'Not specified')}")
        with c_act:
            st.markdown(f"**Actual:**\n\n{res.get('actual_behavior', 'Not specified')}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Reproduction Steps
        st.markdown("""
<div class="intelligence-card">
    <div class="intelligence-card-header"><span class="provenance-tag tag-fact">REPRODUCTION</span> Step-by-Step Procedure</div>
""", unsafe_allow_html=True)
        steps = res.get("reproduction_steps", [])
        if steps:
            for s in steps:
                st.markdown(f"- {s}")
        else:
            st.markdown("_[Information Missing — Human Input Required: No reproduction steps provided in report]_")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # Technical Root Cause Hypothesis
        st.markdown("""
<div class="intelligence-card">
    <div class="intelligence-card-header"><span class="provenance-tag tag-inference">AI HYPOTHESIS</span> Root Cause Hypothesis</div>
""", unsafe_allow_html=True)
        st.markdown(f"_{res.get('root_cause_hypothesis', 'Insufficient data to formulate root-cause hypothesis.')}_")
        st.markdown("<p style='font-size: 0.75rem; color: #9ca3af; margin-top: 8px;'>Note: Root-cause hypotheses are preliminary AI inferences based on available error signatures and require engineering verification.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Environment & Error Codes
        st.markdown("""
<div class="intelligence-card">
    <div class="intelligence-card-header"><span class="provenance-tag tag-fact">TECHNICAL EVIDENCE</span> Environment & Signatures</div>
""", unsafe_allow_html=True)
        st.markdown(f"**Environment:** `{res.get('environment') or 'Not provided'}`")
        err_msgs = res.get("error_messages", [])
        if err_msgs:
            st.markdown("**Error Messages / Codes:**")
            for err in err_msgs:
                st.code(err, language="text")
        else:
            st.markdown("**Error Messages:** _None explicitly provided in report_")
        st.markdown("</div>", unsafe_allow_html=True)

        # Extracted Entities & Suggested Labels
        st.markdown("""
<div class="intelligence-card">
    <div class="intelligence-card-header"><span class="provenance-tag tag-rule">CLASSIFICATION & ROUTING</span> Entities & Labels</div>
""", unsafe_allow_html=True)
        entities = res.get("extracted_entities", [])
        if entities:
            st.markdown("**Extracted Entities:** " + " ".join([f"`{e}`" for e in entities]))
        labels = res.get("suggested_labels", [])
        if labels:
            st.markdown("**Suggested Labels:** " + " ".join([f"`{l}`" for l in labels]))
        st.markdown(f"**Priority Rationale:** {res.get('priority_reasoning', '-')}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Action Bar: Human-in-the-Loop & Export ──
    st.markdown("<h3 style='margin-top: 24px;'>Recommended Actions & Human Review</h3>", unsafe_allow_html=True)
    act_col1, act_col2, act_col3 = st.columns([1, 1, 1])

    with act_col1:
        if st.button("✓ Mark as Reviewed", use_container_width=True):
            st.success("Report verified by human maintainer. Triage status updated.")

    with act_col2:
        new_sev = st.selectbox(
            "Override Severity",
            ["P1", "P2", "P3", "P4"],
            index=["P1", "P2", "P3", "P4"].index(res.get("severity", "P3").replace("Severity.", ""))
            if res.get("severity", "P3").replace("Severity.", "") in ["P1", "P2", "P3", "P4"] else 2,
            key="override_sev_select"
        )
        if st.button("Apply Severity Override", use_container_width=True):
            res["severity"] = new_sev
            st.session_state["triage_result"] = res
            st.success(f"Severity adjusted to {new_sev}.")
            st.rerun()

    with act_col3:
        st.download_button(
            "📥 Export Triage JSON",
            data=json.dumps(res, indent=2),
            file_name=f"triage_{res.get('severity', 'P3')}_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )

    # Technical JSON Inspector toggle
    with st.expander("🔍 Inspect Full Structured Schema JSON"):
        st.json(res)


if __name__ == "__main__":
    show()
