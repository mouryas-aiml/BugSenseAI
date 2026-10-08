"""
Unit tests for bug report quality and completeness scorer.
"""

from backend.quality_scorer import score_report


def test_complete_report_high_score():
    report = """
    Steps to reproduce:
    1. Click on login button in Chrome 122 on macOS Sonoma.
    2. Enter valid credentials and submit.
    Expected: User dashboard loads.
    Actual: Getting 500 Internal Server Error exception thrown.
    Impact: All users are blocked in production.
    """
    score, missing = score_report(report)
    assert score >= 80
    assert len(missing) <= 1


def test_vague_report_low_score():
    report = "it broke"
    score, missing = score_report(report)
    assert score <= 30
    assert len(missing) >= 3


def test_missing_reproduction_detected():
    report = "The payment gateway throws 500 error in production on Chrome v12. Expected success."
    score, missing = score_report(report)
    assert any("repro" in m.lower() for m in missing)



def test_missing_environment_detected():
    report = """
    Steps:
    1. Go to settings.
    2. Click save.
    Expected: Saved.
    Actual: Failed with error 500.
    """
    score, missing = score_report(report)
    assert any("environment" in m.lower() or "browser" in m.lower() for m in missing)
