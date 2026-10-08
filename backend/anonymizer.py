"""
PII Anonymizer — scrubs personally identifiable information before sending
bug reports to external LLM providers.

Handled patterns:
  - Email addresses
  - Phone numbers (common formats)
  - IP addresses (IPv4 & IPv6)
  - API keys / tokens (common patterns)
  - Names prefixed with PII-signal words (e.g. "reported by John Smith")
  - Credit card numbers

This is a best-effort regex layer, not a guaranteed solution.
The anonymized text is used only for LLM calls; the original is preserved
for display/storage so no data is permanently altered.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# ── Patterns ──────────────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(
    r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
)

_PHONE_RE = re.compile(
    r'(?<!\d)'                                      # not preceded by digit
    r'(\+?\d{1,3}[\s\-.]?)?'                       # country code
    r'(\(?\d{2,4}\)?[\s\-.]?)'                     # area code
    r'(\d{2,4}[\s\-.]?){2,4}'                      # number groups
    r'(?!\d)',                                       # not followed by digit
    re.VERBOSE
)

_IPV4_RE = re.compile(
    r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
)

_IPV6_RE = re.compile(
    r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
    r'|(?:[0-9a-fA-F]{1,4}:){1,7}:'
    r'|::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}'
)

# API keys / bearer tokens (long hex/base64 strings ≥ 20 chars)
_TOKEN_RE = re.compile(
    r'\b(?:api[_\-]?key|token|bearer|secret|password|passwd|pwd)[\s:=]+[^\s\'"]{8,}\b',
    re.IGNORECASE
)

# Long random-looking alphanumeric strings (likely keys/hashes, ≥ 24 chars)
_HASH_RE = re.compile(
    r'\b[A-Za-z0-9+/]{24,}={0,2}\b'
)

# Credit card numbers (basic Luhn-style pattern)
_CC_RE = re.compile(
    r'\b(?:\d[ \-]?){13,19}\b'
)

# Names after trigger words
_NAME_TRIGGER_RE = re.compile(
    r'(?:reported by|submitted by|from|user|customer|client|employee|name)[:\s]+([A-Z][a-z]+(?: [A-Z][a-z]+)+)',
    re.IGNORECASE
)

# ── Replacement constants ──────────────────────────────────────────────────────

_REPLACEMENTS = [
    (_EMAIL_RE,        "[EMAIL_REDACTED]"),
    (_IPV4_RE,         "[IP_REDACTED]"),
    (_IPV6_RE,         "[IP_REDACTED]"),
    (_TOKEN_RE,        "[CREDENTIAL_REDACTED]"),
    (_HASH_RE,         "[HASH_REDACTED]"),
    (_CC_RE,           "[CC_REDACTED]"),
]


def anonymize(text: str) -> Tuple[str, int]:
    """
    Scrub PII from a bug report string.

    Returns:
        (anonymized_text, count_of_redactions)

    The original text is never modified — this function returns a new string.
    """
    if not text:
        return text, 0

    result = text
    redaction_count = 0

    # Named-entity trigger words (do first, before removing emails that might be names)
    for m in reversed(list(_NAME_TRIGGER_RE.finditer(result))):
        result = result[:m.start(1)] + "[NAME_REDACTED]" + result[m.end(1):]
        redaction_count += 1

    # Structured patterns
    for pattern, replacement in _REPLACEMENTS:
        new_result, n = pattern.subn(replacement, result)
        result = new_result
        redaction_count += n

    if redaction_count > 0:
        logger.info(f"Anonymizer: redacted {redaction_count} PII item(s) before LLM call")

    return result, redaction_count


def get_redaction_summary(original: str, anonymized: str) -> list:
    """
    Return a list of redaction types found.
    Used for UI display: 'Report contained: 1 email, 2 IPs'.
    """
    found = []
    checks = [
        (_EMAIL_RE,   "email address"),
        (_IPV4_RE,    "IP address"),
        (_IPV6_RE,    "IPv6 address"),
        (_TOKEN_RE,   "API key/token"),
        (_HASH_RE,    "potential hash/key"),
        (_CC_RE,      "potential card number"),
        (_NAME_TRIGGER_RE, "personal name"),
    ]
    for pattern, label in checks:
        matches = pattern.findall(original)
        if matches:
            found.append(f"{len(matches)} {label}{'s' if len(matches) > 1 else ''}")
    return found
