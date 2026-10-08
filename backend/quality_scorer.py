"""
Bug Report Quality Scorer

Analyses a raw bug report for completeness and assigns a score 0–100.

Checks (weighted):
  1. Has a clear problem description          (20 pts)
  2. Has steps to reproduce                   (20 pts)
  3. Has expected behavior                    (15 pts)
  4. Has actual / observed behavior           (15 pts)
  5. Has environment info (OS, browser, ver)  (10 pts)
  6. Has error message / stack trace          (10 pts)
  7. Has severity/impact signal               (5 pts)
  8. Minimum length (> 50 chars)              (5 pts)

Also returns a list of what's missing for display in the UI.
"""

import re
from typing import Tuple, List


# Keyword signals for each quality dimension
_REPRO_SIGNALS = [
    r'\bstep[s]?\b', r'\bto reproduce\b', r'\brepro\b',
    r'\b\d+\.\s', r'\bfirst\b', r'\bthen\b', r'\bnext\b',
    r'\bclick\b', r'\bnavigate\b', r'\bopen\b', r'\bgo to\b',
    r'\benter\b', r'\bsubmit\b', r'\bselect\b',
]

_EXPECTED_SIGNALS = [
    r'\bexpected\b', r'\bshould\b', r'\bsupposed to\b',
    r'\bintended\b', r'\bnormal(ly)?\b', r'\bcorrect(ly)?\b',
    r'\bworks?\b.*\bbefore\b', r'\bused to\b',
]

_ACTUAL_SIGNALS = [
    r'\bactual(ly)?\b', r'\binstead\b', r'\bbut\b.*\bhappen\b',
    r'\boccur[s]?\b', r'\bsee[s]?\b', r'\bgetting\b', r'\bgets?\b',
    r'\bthrows?\b', r'\bcauses?\b', r'\bresult[s]?\b.*\bin\b',
    r'\bhappen[s]?\b',
]

_ENV_SIGNALS = [
    r'\bbrowser\b', r'\bchrome\b', r'\bfirefox\b', r'\bsafari\b', r'\bedge\b',
    r'\bwindows\b', r'\bmac(os)?\b', r'\blinux\b', r'\bubuntu\b',
    r'\bversion\b', r'\bv\d+\.\d+\b', r'\brelease\b', r'\bbuild\b',
    r'\bstaging\b', r'\bproduction\b', r'\bdev\b', r'\benv\b',
    r'\biphone\b', r'\bandroid\b', r'\bmobile\b', r'\bios\b',
]

_ERROR_SIGNALS = [
    r'\berror\b', r'\bexception\b', r'\bstack trace\b', r'\btraceback\b',
    r'\b500\b', r'\b404\b', r'\b403\b', r'\bnull\b', r'\bundefined\b',
    r'\bcaught\b', r'\bthrown\b', r'\bcrash\b', r'\bfailed\b',
    r'\[error\]', r'\berr:\b',
]

_IMPACT_SIGNALS = [
    r'\ball user[s]?\b', r'\bproduction\b', r'\bcritical\b', r'\burgent\b',
    r'\bblock[s]?\b', r'\bbreaks?\b', r'\bcan\'?t\b', r'\bcannot\b',
    r'\bimpact[s]?\b', r'\baffect[s]?\b', r'\bseverity\b', r'\bpriority\b',
    r'\bblocking\b', r'\bregression\b',
]


def _matches_any(text: str, patterns: List[str]) -> bool:
    """Return True if any pattern matches in the text (case-insensitive)."""
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def score_report(raw_text: str) -> Tuple[int, List[str]]:
    """
    Score a raw bug report for completeness.

    Returns:
        (score: int 0–100, missing_items: List[str])
    """
    if not raw_text or not raw_text.strip():
        return 0, [
            "Problem description", "Reproduction steps",
            "Expected behavior", "Actual behavior",
            "Environment information", "Error messages",
            "Impact/severity signal"
        ]

    text = raw_text.strip()
    score = 0
    missing: List[str] = []

    # 1. Problem description (just needs to be non-trivial)
    if len(text) >= 50:
        score += 20
    elif len(text) >= 20:
        score += 10
        missing.append("More detailed problem description (report is very brief)")
    else:
        missing.append("Clear problem description (too brief)")

    # 2. Steps to reproduce
    if _matches_any(text, _REPRO_SIGNALS):
        score += 20
    else:
        missing.append("Reproduction steps (numbered steps or how to trigger)")

    # 3. Expected behavior
    if _matches_any(text, _EXPECTED_SIGNALS):
        score += 15
    else:
        missing.append("Expected behavior (what should have happened)")

    # 4. Actual behavior
    if _matches_any(text, _ACTUAL_SIGNALS):
        score += 15
    else:
        missing.append("Actual behavior (what actually happened)")

    # 5. Environment information
    if _matches_any(text, _ENV_SIGNALS):
        score += 10
    else:
        missing.append("Environment details (OS, browser, version, or environment)")

    # 6. Error message or stack trace
    if _matches_any(text, _ERROR_SIGNALS):
        score += 10
    else:
        missing.append("Error messages, codes, or stack traces")

    # 7. Severity/impact signal
    if _matches_any(text, _IMPACT_SIGNALS):
        score += 5
    else:
        missing.append("Severity or user impact indication")

    # 8. Minimum length bonus
    if len(text) >= 200:
        score += 5

    return min(score, 100), missing


def get_score_label(score: int) -> str:
    """Return a human-readable quality label for a score."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    elif score >= 30:
        return "Poor"
    else:
        return "Very Poor"


def get_score_color(score: int) -> str:
    """Return a color hint for UI rendering."""
    if score >= 85:
        return "green"
    elif score >= 70:
        return "blue"
    elif score >= 50:
        return "orange"
    else:
        return "red"
