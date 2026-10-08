"""
Unit tests for PII and sensitive entity anonymizer.
"""

from backend.anonymizer import anonymize, get_redaction_summary


def test_anonymize_email():
    text = "Reported by alice.tester@enterprise.com regarding auth failure."
    redacted, count = anonymize(text)
    assert "[EMAIL_REDACTED]" in redacted
    assert "alice.tester@enterprise.com" not in redacted
    assert count >= 1


def test_anonymize_ip_address():
    text = "Connection timed out connecting to 192.168.1.105 on port 8080."
    redacted, count = anonymize(text)
    assert "[IP_REDACTED]" in redacted
    assert "192.168.1.105" not in redacted
    assert count >= 1


def test_anonymize_multiple_pii():
    text = "Contact john.doe@corp.net from 10.0.0.1 immediately."
    redacted, count = anonymize(text)
    assert "[EMAIL_REDACTED]" in redacted
    assert "[IP_REDACTED]" in redacted
    assert count >= 2


def test_redaction_summary():
    text = "User bob@test.com on 172.16.0.4 reported crash."
    redacted, _ = anonymize(text)
    summary = get_redaction_summary(text, redacted)
    assert any("email" in s.lower() for s in summary)
    assert any("ip" in s.lower() for s in summary)


def test_no_pii_clean_text():
    text = "NullPointerException in payment gateway when clicking submit."
    redacted, count = anonymize(text)
    assert redacted == text
    assert count == 0
