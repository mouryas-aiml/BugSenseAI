"""
BugSenseAI — Section 9: Settings & Configuration
AI model parameters, triage thresholds, privacy/anonymization rules,
and system configuration with strict secret protection.
"""

import streamlit as st
import os
import re
from frontend.styles import render_header


def show():
    render_header(
        title="Platform Settings & Model Governance",
        subtitle="Manage LLM orchestration parameters, privacy thresholds, and triage governance rules",
        badge="GOVERNANCE & CONFIG"
    )

    # 1. AI Model Configuration
    st.subheader("1. AI Model Orchestration")
    col_m1, col_m2 = st.columns(2)

    with col_m1:
        current_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        provider = st.selectbox(
            "Active LLM Provider",
            ["gemini", "openai", "groq", "ollama"],
            index=["gemini", "openai", "groq", "ollama"].index(current_provider) if current_provider in ["gemini", "openai", "groq", "ollama"] else 0,
            help="Google Gemini is recommended with official SDK and zero-cost tier."
        )

        current_model = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
        gemini_model = st.selectbox(
            "Gemini Model Variant",
            ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-3.8-flash"],
            index=["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-3.8-flash"].index(current_model) if current_model in ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-3.8-flash"] else 0,
            help="gemini-flash-lite-latest offers <1s response times and highest availability."
        )

    with col_m2:
        timeout = st.slider("API Request Timeout (seconds)", min_value=15, max_value=120, value=int(os.getenv("LLM_TIMEOUT_SECONDS", "60")), step=5)
        st.markdown("""
<div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; padding: 10px 14px; border-radius: 4px; font-size: 0.85rem; color: #93c5fd; margin-top: 10px;">
    <strong>Auto-Fallback Strategy Active:</strong> If the primary model encounters temporary traffic spikes (503) or rate limits, the platform automatically retries with verified backup flash models.
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    # 2. Thresholds & Triage Rules
    st.subheader("2. Quality & Duplicate Thresholds")
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        sim_threshold = st.slider("Duplicate Cosine Similarity Threshold", min_value=0.50, max_value=0.90, value=0.68, step=0.02, help="Reports with vector similarity above this value are flagged as duplicates.")
        quality_threshold = st.slider("Completeness Human-Review Threshold", min_value=20, max_value=60, value=40, step=5, help="Reports scoring below this quality score require manual human review.")

    with col_t2:
        st.markdown("**Mandatory Human-in-the-Loop Triggers:**")
        st.checkbox("Flag all P1 (Critical) reports for human review", value=True, disabled=True)
        st.checkbox("Flag all Low Confidence reports for human review", value=True, disabled=True)
        st.checkbox("Flag reports with missing reproduction steps", value=True, disabled=True)

    st.markdown("---")

    # 3. Privacy & Anonymization Settings
    st.subheader("3. Data Privacy & PII Redaction")
    st.markdown("Control automated client-side data anonymization before external model dispatch:")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.checkbox("Mask Customer Email Addresses", value=True, help="Replaces emails with [EMAIL_REDACTED]")
        st.checkbox("Mask IP Addresses & Subnets", value=True, help="Replaces IPv4/IPv6 with [IP_REDACTED]")
    with col_p2:
        st.checkbox("Mask Auth Tokens & Private Keys", value=True, help="Replaces JWT, Bearer tokens with [TOKEN_REDACTED]")
        st.checkbox("Mask Identified Personal Names", value=True, help="Masks reporter and employee names")

    st.markdown("---")

    # 4. Secret Governance (Strict Non-Exposure)
    st.subheader("4. Secrets & Environment Governance")
    st.markdown("""
<div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; padding: 12px 16px; margin-bottom: 16px; font-size: 0.85rem; color: #a7f3d0;">
    <strong>🔒 Zero Secret Exposure Guarantee:</strong> API keys and production credentials are never printed, displayed, logged, or exported.
</div>
""", unsafe_allow_html=True)

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    key_status = "••••••••••••••••••••••••••••• (Configured)" if gemini_key else "Not Configured"
    st.text_input("GEMINI_API_KEY", value=key_status, disabled=True)

    # Save button
    if st.button("💾 Save Settings to .env", type="primary"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                env_content = f.read()

            env_content = re.sub(r"LLM_PROVIDER=.*", f"LLM_PROVIDER={provider}", env_content)
            env_content = re.sub(r"GEMINI_MODEL=.*", f"GEMINI_MODEL={gemini_model}", env_content)
            env_content = re.sub(r"LLM_TIMEOUT_SECONDS=.*", f"LLM_TIMEOUT_SECONDS={timeout}", env_content)

            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)

            st.success("Configuration updated successfully!")
        except Exception as e:
            st.error(f"Failed to save settings: {e}")


if __name__ == "__main__":
    show()
