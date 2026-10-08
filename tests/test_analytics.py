"""
Unit tests for historical analytics computation.
"""

from backend.analytics import get_analytics, get_history


def test_get_analytics_structure():
    analytics = get_analytics()
    assert "total_reports" in analytics
    assert "severity_distribution" in analytics
    assert "component_distribution" in analytics
    assert "confidence_distribution" in analytics
    assert "avg_completeness_score" in analytics
    assert "requires_human_review_count" in analytics
    assert "duplicate_count" in analytics

    # Validate severity keys
    sev = analytics["severity_distribution"]
    for k in ["P1", "P2", "P3", "P4"]:
        assert k in sev


def test_get_history_pagination():
    history = get_history(limit=5, offset=0)
    assert "total" in history
    assert "items" in history
    assert len(history["items"]) <= 5
