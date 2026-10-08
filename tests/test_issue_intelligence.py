import json

import numpy as np

from backend import issue_intelligence as intelligence


def _record(issue_id, title, body, state="closed", comments=None, labels=None, is_pr=False):
    return {
        "id": issue_id,
        "number": issue_id,
        "title": title,
        "body": body,
        "comments": comments or [],
        "labels": [{"name": label} for label in (labels or [])],
        "state": state,
        "repository_url": "https://api.github.com/repos/example/project",
        "html_url": f"https://github.com/example/project/issues/{issue_id}",
        "pull_request": {"url": "x"} if is_pr else None,
    }


def test_normalize_extracts_metadata_and_resolution():
    result = intelligence.normalize_issue(_record(1, "API timeout", "The API times out in production", comments=["Fixed in release 2.0"]), 0)

    assert result["issue_id"] == "1"
    assert result["category"] == "Performance"
    assert result["component"] == "example/project"
    assert result["resolution_available"] is True
    assert "Fixed in release 2.0" in result["resolution_summary"]


def test_prepare_index_persists_clusters_and_supports_csv(tmp_path, monkeypatch):
    records = [
        intelligence.normalize_issue(_record(1, "Video buffering", "Videos keep buffering", comments=["Workaround: clear the cache"])),
        intelligence.normalize_issue(_record(2, "Videos will not play", "Video playback is stuck", comments=["Fixed in release 4.1"])),
        intelligence.normalize_issue(_record(3, "Billing export error", "CSV export returns an error", state="open")),
    ]
    vectors = np.asarray([[1, 0], [0.99, 0.01], [0, 1]], dtype=np.float32)
    monkeypatch.setattr(intelligence, "_embed", lambda texts: vectors)
    monkeypatch.setattr(intelligence, "INDEX_DIR", tmp_path)
    monkeypatch.setattr(intelligence, "METADATA_PATH", tmp_path / "index.json")
    monkeypatch.setattr(intelligence, "EMBEDDING_PATH", tmp_path / "embeddings.npz")
    intelligence._state = {"metadata": None, "embeddings": None}

    result = intelligence.build_index(records)
    assert result["record_count"] == 3
    assert records[0]["cluster_id"] == records[1]["cluster_id"]
    assert records[0]["cluster_id"] != records[2]["cluster_id"]

    analytics = intelligence.get_analytics()
    assert analytics["total_reports"] == 3
    assert analytics["unique_issue_clusters"] == 2
    assert analytics["duplicate_similar_reports"] == 1
    assert analytics["potentially_auto_resolvable"] == 2

    csv_text = intelligence.export_csv("issues")
    assert "issue_id" in csv_text
    assert "cluster_id" in csv_text
    assert "resolution_summary" in csv_text


def test_grounded_resolution_escalates_without_evidence(tmp_path, monkeypatch):
    records = [intelligence.normalize_issue(_record(1, "Unknown error", "Something fails", state="open"))]
    monkeypatch.setattr(intelligence, "_load_index", lambda: ({"records": records}, np.asarray([[1, 0]], dtype=np.float32)))
    monkeypatch.setattr(intelligence, "_embed", lambda texts: np.asarray([[1, 0]], dtype=np.float32))

    result = intelligence.resolve_issue("Something fails")
    assert result["resolution_available"] is False
    assert result["escalation_recommended"] is True
    assert result["steps"] == []
    assert "not contain enough" in result["answer"]


def test_pull_requests_are_identifiable_for_filtering():
    result = intelligence.normalize_issue(_record(5, "PR change", "Change", is_pr=True))
    assert result["is_pull_request"] is True
