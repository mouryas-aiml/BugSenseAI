"""
Triage pipeline orchestrator.

Flow:
  1. Validate input
  2. Score report quality (deterministic, no LLM)
  3. Anonymize PII before LLM call
  4. Load prompt + inject feedback
  5. LLM call → structured JSON
  6. Parse + Pydantic validate
  7. Enrich with rules (team routing, severity hints, review labels, test areas)
  8. Add completeness score and review flag
  9. Duplicate detection via vector store
  10. Save output JSON
  11. Return enriched dict

Failure modes documented:
  - Vague reports → low confidence (human review required)
  - Generated repro steps are guesses, clearly prefixed [generated]
  - Root cause hypotheses are guesses, clearly prefixed [HYPOTHESIS]
  - Duplicate detection is semantic but not perfect
  - Severity may need human adjustment on ambiguous reports
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import logging

from dotenv import load_dotenv
from pydantic import ValidationError

from .models import TriageOutput, SimilarBug
from .llm_client import generate_structured_ticket
from .rules import enhance_triage
from .feedback_store import format_feedback_for_prompt
from .anonymizer import anonymize, get_redaction_summary
from .quality_scorer import score_report

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompt.txt"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


def load_prompt() -> str:
    """Load prompt template from file."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt file missing: {PROMPT_PATH}")
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def parse_llm_response(response: str) -> Dict[str, Any]:
    """Parse the LLM JSON response.

    All providers return valid JSON via structured output modes.
    A JSONDecodeError means the provider ignored the format constraint.
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM returned invalid JSON (provider may not support structured outputs): {e}"
        )


def triage_bug(raw_text: str, save_output: bool = False) -> Dict[str, Any]:
    """Main triage function. Returns enriched triage dict.

    Args:
        raw_text:    Raw bug report (any format/length)
        save_output: If True, saves result to outputs/triaged_<timestamp>.json

    Returns:
        Dict matching TriageOutput schema, enriched with rules and scores.

    Raises:
        ValueError: If input is empty, LLM fails, or JSON is invalid.
    """
    if not raw_text.strip():
        raise ValueError("Bug text cannot be empty")

    start_time = time.time()

    # Step 1: Quality scoring (deterministic, before LLM)
    quality_score, missing_items = score_report(raw_text)
    logger.info(f"Quality score: {quality_score}/100, missing: {missing_items}")

    # Step 2: Anonymize PII before sending to external LLM
    anonymized_text, redaction_count = anonymize(raw_text)
    redaction_summary = get_redaction_summary(raw_text, anonymized_text)

    # Step 3: Build prompt
    prompt_template = load_prompt()
    feedback_block = format_feedback_for_prompt(n=5)
    prompt = prompt_template.replace("{{RAW_INPUT}}", anonymized_text)
    if feedback_block:
        prompt = prompt.replace("BUG REPORT:", feedback_block + "BUG REPORT:", 1)

    # Step 4: LLM call
    llm_response = generate_structured_ticket(prompt)
    logger.info("LLM response received")

    # Step 5: Parse + Pydantic validate
    triage_data = parse_llm_response(llm_response)

    # Inject quality-scorer missing items if LLM didn't find them
    if missing_items and not triage_data.get("missing_information"):
        triage_data["missing_information"] = missing_items

    try:
        output = TriageOutput(**triage_data)
    except ValidationError as e:
        logger.error(f"Pydantic validation failed: {e}")
        raise ValueError(f"Invalid triage structure from LLM: {e}")

    # Step 6: Rule enhancements (deterministic post-LLM)
    enhanced = enhance_triage(output.model_dump())

    # Step 7: Inject quality/completeness data
    enhanced["completeness_score"] = quality_score
    enhanced["requires_human_review"] = (
        enhanced.get("confidence") == "Low"
        or enhanced.get("severity") == "P1"
        or quality_score < 40
    )

    # Step 8: Duplicate detection (optional, won't block if it fails)
    try:
        from .vector_store import find_similar
        similar = find_similar(enhanced)
        if similar:
            enhanced["similar_bugs"] = [
                SimilarBug(
                    id=similar.get("jira_key", ""),
                    title=similar.get("title", ""),
                    similarity=similar.get("similarity", 0.0),
                    source="local",
                ).model_dump()
            ]
            enhanced["is_duplicate"] = True
        else:
            enhanced["similar_bugs"] = []
            enhanced["is_duplicate"] = False
    except Exception as e:
        logger.warning(f"Duplicate detection failed (non-fatal): {e}")
        enhanced["similar_bugs"] = []
        enhanced["is_duplicate"] = False

    # Step 9: Metadata
    elapsed_ms = int((time.time() - start_time) * 1000)
    enhanced["_processing_time_ms"] = elapsed_ms
    enhanced["_pii_redacted"] = redaction_count > 0
    enhanced["_pii_redaction_types"] = redaction_summary

    # Step 10: Save
    if save_output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUTS_DIR / f"triaged_{timestamp}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(enhanced, f, indent=2)
        logger.info(f"Saved to {output_path}")

    return enhanced
