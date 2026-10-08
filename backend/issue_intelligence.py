"""Data-driven issue intelligence built on a configurable Hugging Face dataset.

The service intentionally keeps the expensive work out of request handlers:
the dataset is downloaded by ``load_dataset`` once, normalized once, embedded
in batches, and persisted as metadata JSON plus a compressed NumPy matrix.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import re
import threading
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np

from .anonymizer import anonymize

logger = logging.getLogger(__name__)

DATASET_NAME = os.getenv("ISSUE_DATASET_NAME", "helmo/github-issues")
DATASET_SPLIT = os.getenv("ISSUE_DATASET_SPLIT", "train")
INCLUDE_PRS = os.getenv("ISSUE_INCLUDE_PRS", "false").lower() == "true"
CLUSTER_THRESHOLD = float(os.getenv("ISSUE_CLUSTER_THRESHOLD", "0.78"))
RETRIEVAL_THRESHOLD = float(os.getenv("ISSUE_RETRIEVAL_THRESHOLD", "0.42"))
INDEX_DIR = Path(os.getenv("ISSUE_INTELLIGENCE_INDEX_DIR", "outputs"))
METADATA_PATH = INDEX_DIR / "issue_intelligence_index.json"
EMBEDDING_PATH = INDEX_DIR / "issue_intelligence_embeddings.npz"
MODEL_NAME = os.getenv("ISSUE_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_state: dict[str, Any] = {"metadata": None, "embeddings": None}
_lock = threading.RLock()
_build_lock = threading.Lock()


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return "\n".join(_text(item) for item in value if _text(item))
    if isinstance(value, dict):
        return " ".join(_text(v) for v in value.values() if _text(v))
    return str(value).strip()


def _label_names(labels: Any) -> list[str]:
    if not isinstance(labels, list):
        return []
    names = []
    for label in labels:
        name = _text(label.get("name")) if isinstance(label, dict) else _text(label)
        if name:
            names.append(name)
    return names


def _comments(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    return [value] if _text(value) else []


def _repository_name(url: str) -> str:
    parts = [part for part in url.rstrip("/").split("/") if part]
    return "/".join(parts[-2:]) if len(parts) >= 2 else "Unknown repository"


def _category(title: str, body: str, labels: list[str]) -> str:
    label_text = " ".join(labels).lower()
    text = f"{title} {body} {label_text}".lower()
    categories = [
        ("Documentation", ("documentation", "docs", "readme")),
        ("Build and CI", ("ci", "pipeline", "build", "workflow", "test")),
        ("Performance", ("slow", "performance", "memory", "timeout", "latency")),
        ("API and Data", ("api", "dataset", "data", "schema", "serialization")),
        ("User Interface", ("ui", "interface", "display", "render", "notebook")),
        ("Installation", ("install", "dependency", "package", "pip", "conda")),
        ("Security", ("security", "vulnerability", "credential", "token")),
    ]
    for name, signals in categories:
        if any(signal in text for signal in signals):
            return name
    return labels[0] if labels else "General"


def _priority(labels: list[str], body: str) -> str:
    text = " ".join(labels + [body]).lower()
    if any(word in text for word in ("critical", "urgent", "blocker", "security")):
        return "High"
    if any(word in text for word in ("bug", "error", "regression", "crash")):
        return "Medium"
    return "Unspecified"


def _resolution_content(body: str, comments: list[str], state: str) -> tuple[bool, str, list[str]]:
    resolution_terms = ("fixed", "fix", "resolved", "workaround", "solution", "release", "merged", "close")
    candidates = [comment for comment in comments if any(term in comment.lower() for term in resolution_terms)]
    if state.lower() == "closed" and not candidates and comments:
        candidates = comments[-2:]
    snippets = []
    for candidate in candidates[:3]:
        sentences = re.split(r"(?<=[.!?])\s+", candidate)
        snippets.extend(sentence.strip() for sentence in sentences if sentence.strip())
    snippets = snippets[:6]
    summary = " ".join(snippets)[:900]
    return bool(summary), summary, snippets


def normalize_issue(record: dict[str, Any], issue_index: int = 0) -> dict[str, Any]:
    """Map the GitHub issue schema into the stable intelligence schema."""
    title = _text(record.get("title")) or "Untitled issue"
    body = _text(record.get("body"))
    comments = _comments(record.get("comments"))
    labels = _label_names(record.get("labels"))
    state = _text(record.get("state")) or "unknown"
    issue_id = _text(record.get("id")) or _text(record.get("number")) or str(issue_index)
    clean_title, _ = anonymize(title)
    clean_body, _ = anonymize(body)
    clean_comments = [anonymize(comment)[0] for comment in comments]
    resolution_available, resolution_summary, resolution_steps = _resolution_content(clean_body, clean_comments, state)
    repository = _repository_name(_text(record.get("repository_url")))
    summary_source = clean_body or clean_title
    summary = re.split(r"(?<=[.!?])\s+", summary_source)[0][:300]
    return {
        "issue_id": issue_id,
        "number": record.get("number"),
        "title": title,
        "summary": summary,
        "body": body,
        "comments": comments,
        "labels": labels,
        "state": state,
        "category": _category(title, body, labels),
        "component": repository,
        "priority": _priority(labels, body),
        "created_at": _text(record.get("created_at")),
        "updated_at": _text(record.get("updated_at")),
        "closed_at": _text(record.get("closed_at")),
        "source_url": _text(record.get("html_url")) or _text(record.get("url")),
        "is_pull_request": bool(record.get("pull_request")) or _text(record.get("type")).lower() in {"pullrequest", "pull request"},
        "discussion_count": len(comments),
        "resolution_available": resolution_available,
        "resolution_summary": resolution_summary,
        "resolution_steps": resolution_steps,
        "confidence": "High" if len(resolution_steps) >= 2 else ("Medium" if resolution_available else "Low"),
        "cluster_name": "",
        "search_text": "\n".join([clean_title, clean_body, *clean_comments]).strip(),
    }


def _load_source_records() -> list[dict[str, Any]]:
    from datasets import load_dataset

    dataset = load_dataset(DATASET_NAME)
    split = dataset[DATASET_SPLIT] if hasattr(dataset, "keys") and DATASET_SPLIT in dataset else dataset
    records = []
    for index, record in enumerate(split):
        normalized = normalize_issue(dict(record), index)
        if not INCLUDE_PRS and normalized["is_pull_request"]:
            continue
        if normalized["search_text"]:
            records.append(normalized)
    return records


def _embed(texts: list[str]) -> np.ndarray:
    from .vector_store import _get_model

    model = _get_model()
    values = model.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
    return np.asarray(values, dtype=np.float32)


def _cluster_embeddings(embeddings: np.ndarray) -> list[int]:
    """Build connected semantic groups without an O(n^2) matrix allocation."""
    size = len(embeddings)
    parents = list(range(size))

    def find(value: int) -> int:
        while parents[value] != value:
            parents[value] = parents[parents[value]]
            value = parents[value]
        return value

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    block_size = 256
    for start in range(0, size, block_size):
        block = embeddings[start:start + block_size] @ embeddings.T
        for row, scores in enumerate(block):
            scores[row + start] = -1.0
            candidates = np.flatnonzero(scores >= CLUSTER_THRESHOLD)
            if len(candidates) > 8:
                candidates = candidates[np.argsort(scores[candidates])[-8:]]
            for candidate in candidates:
                union(start + row, int(candidate))

    roots = {}
    cluster_ids = []
    for index in range(size):
        root = find(index)
        roots.setdefault(root, len(roots) + 1)
        cluster_ids.append(roots[root])
    return cluster_ids


def build_index(records: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
    """Build and persist the dataset index. Safe to call from a worker thread."""
    with _build_lock:
        if records is None:
            records = _load_source_records()
        embeddings = _embed([record["search_text"] for record in records])
        cluster_ids = _cluster_embeddings(embeddings)
        for record, cluster_id in zip(records, cluster_ids):
            record["cluster_id"] = f"ISSUE-{cluster_id:04d}"
        cluster_names = {}
        for record in records:
            cluster_names.setdefault(record["cluster_id"], record["title"][:100])
        for record in records:
            record["cluster_name"] = cluster_names[record["cluster_id"]]
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "dataset_name": DATASET_NAME,
            "dataset_split": DATASET_SPLIT,
            "model_name": MODEL_NAME,
            "cluster_threshold": CLUSTER_THRESHOLD,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "records": records,
        }
        METADATA_PATH.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
        np.savez_compressed(EMBEDDING_PATH, embeddings=embeddings)
        with _lock:
            _state["metadata"] = payload
            _state["embeddings"] = embeddings
        return status()


def status() -> dict[str, Any]:
    ready = METADATA_PATH.exists() and EMBEDDING_PATH.exists()
    records = _state.get("metadata", {}).get("records", []) if _state.get("metadata") else []
    if ready and not records:
        try:
            _load_index()
            records = _state["metadata"]["records"]
        except Exception as exc:
            return {"ready": False, "building": False, "error": str(exc), "dataset_name": DATASET_NAME}
    return {
        "ready": ready,
        "building": _build_lock.locked(),
        "dataset_name": DATASET_NAME,
        "dataset_split": DATASET_SPLIT,
        "record_count": len(records),
        "index_path": str(METADATA_PATH),
    }


def _load_index() -> tuple[dict[str, Any], np.ndarray]:
    with _lock:
        if _state.get("metadata") is None or _state.get("embeddings") is None:
            if not METADATA_PATH.exists() or not EMBEDDING_PATH.exists():
                raise FileNotFoundError("Issue intelligence index is not ready. Call POST /issue-intelligence/prepare.")
            _state["metadata"] = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
            _state["embeddings"] = np.load(EMBEDDING_PATH, allow_pickle=False)["embeddings"]
        return _state["metadata"], _state["embeddings"]


def _filtered_records(filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    metadata, _ = _load_index()
    records = metadata["records"]
    filters = filters or {}
    query = _text(filters.get("query")).lower()
    category = _text(filters.get("category"))
    state = _text(filters.get("state"))
    priority = _text(filters.get("priority"))
    start_date = _text(filters.get("start_date"))
    end_date = _text(filters.get("end_date"))
    return [
        record for record in records
        if (not query or query in f"{record['title']} {record['body']} {' '.join(record['labels'])}".lower())
        and (not category or record["category"] == category)
        and (not state or record["state"] == state)
        and (not priority or record["priority"] == priority)
        and (not start_date or record["created_at"] >= start_date)
        and (not end_date or record["created_at"] <= end_date)
    ]


def _cluster_summary(records: list[dict[str, Any]], cluster_id: str) -> dict[str, Any]:
    members = [record for record in records if record.get("cluster_id") == cluster_id]
    if not members:
        raise KeyError(cluster_id)
    representative = max(members, key=lambda item: (len(item["body"]), item["discussion_count"]))
    symptoms = Counter(word.lower() for record in members for word in re.findall(r"[A-Za-z]{5,}", record["title"]))
    common_symptoms = [word for word, _ in symptoms.most_common(8)]
    resolutions = [record["resolution_summary"] for record in members if record["resolution_available"]]
    return {
        "cluster_id": cluster_id,
        "cluster_name": representative["title"][:100],
        "report_count": len(members),
        "percentage": round((len(members) / len(records)) * 100, 2) if records else 0,
        "representative_issue_id": representative["issue_id"],
        "representative_title": representative["title"],
        "category": Counter(item["category"] for item in members).most_common(1)[0][0],
        "common_symptoms": common_symptoms,
        "related_issue_ids": [item["issue_id"] for item in members[:10]],
        "resolution_available": bool(resolutions),
        "resolution_summary": resolutions[0] if resolutions else "No grounded resolution discussion found.",
    }


def get_analytics(filters: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    records = _filtered_records(filters)
    clusters = {_record["cluster_id"] for _record in records}
    category_counts = Counter(record["category"] for record in records)
    component_counts = Counter(record["component"] for record in records)
    issue_counts = Counter(record["cluster_id"] for record in records)
    discussion_counts = sorted(records, key=lambda item: item["discussion_count"], reverse=True)
    resolutions = sum(record["resolution_available"] for record in records)
    high_priority = sum(record["priority"] == "High" for record in records)
    duplicate_reports = sum(max(0, count - 1) for count in issue_counts.values())
    cluster_count = len(clusters)
    return {
        "total_reports": len(records),
        "unique_issue_clusters": cluster_count,
        "duplicate_similar_reports": duplicate_reports,
        "top_issue": issue_counts.most_common(1)[0][0] if issue_counts else None,
        "top_issue_percentage": round((issue_counts.most_common(1)[0][1] / len(records)) * 100, 2) if records else 0,
        "potentially_auto_resolvable": resolutions,
        "human_escalations": len(records) - resolutions,
        "ai_resolution_rate": round((resolutions / len(records)) * 100, 2) if records else 0,
        "average_confidence": round(sum({"High": 1.0, "Medium": 0.6, "Low": 0.2}[record["confidence"]] for record in records) / len(records), 2) if records else 0,
        "average_completeness": round(sum(min(100, len(record["body"]) // 10) for record in records) / len(records), 2) if records else 0,
        "open_count": sum(record["state"].lower() == "open" for record in records),
        "closed_count": sum(record["state"].lower() == "closed" for record in records),
        "high_priority_count": high_priority,
        "resolution_count": resolutions,
        "category_distribution": dict(category_counts.most_common(15)),
        "component_distribution": dict(component_counts.most_common(15)),
        "most_discussed": [{"issue_id": item["issue_id"], "title": item["title"], "comments": item["discussion_count"]} for item in discussion_counts[:10]],
        "clusters_with_resolutions": sum(_cluster_summary(records, cluster)["resolution_available"] for cluster in clusters),
        "trend_by_month": dict(sorted(Counter(record["created_at"][:7] for record in records if record["created_at"]).items())),
        "dataset_name": DATASET_NAME,
    }


def list_clusters(offset: int = 0, limit: int = 25, filters: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    records = _filtered_records(filters)
    cluster_ids = sorted({record["cluster_id"] for record in records})
    items = [_cluster_summary(records, cluster_id) for cluster_id in cluster_ids]
    items.sort(key=lambda item: item["report_count"], reverse=True)
    return {"total": len(items), "offset": offset, "limit": limit, "items": items[offset:offset + limit]}


def get_issue(issue_id: str) -> dict[str, Any]:
    metadata, embeddings = _load_index()
    records = metadata["records"]
    index = next((i for i, record in enumerate(records) if record["issue_id"] == issue_id), None)
    if index is None:
        raise KeyError(issue_id)
    similarities = embeddings @ embeddings[index]
    candidates = np.argsort(similarities)[::-1]
    similar = [
        {"issue_id": records[candidate]["issue_id"], "title": records[candidate]["title"], "similarity": round(float(similarities[candidate]) * 100, 1)}
        for candidate in candidates[1:6]
        if similarities[candidate] >= RETRIEVAL_THRESHOLD
    ]
    record = dict(records[index])
    record["similar_reports"] = similar
    record["evidence_sources"] = [item["source_url"] for item in [records[index], *[records[candidate] for candidate in candidates[1:4]]] if item.get("source_url")]
    record["escalation_recommendation"] = "Human agent recommended" if not record["resolution_available"] else "Offer grounded resolution and collect confirmation"
    return record


def resolve_issue(query: str, top_k: int = 5) -> dict[str, Any]:
    metadata, embeddings = _load_index()
    clean_query = anonymize(query)[0]
    query_embedding = _embed([clean_query])[0]
    scores = embeddings @ query_embedding
    candidates = np.argsort(scores)[::-1]
    matches = []
    evidence = []
    for candidate in candidates[:top_k]:
        if scores[candidate] < RETRIEVAL_THRESHOLD:
            continue
        record = metadata["records"][candidate]
        matches.append({"issue_id": record["issue_id"], "title": record["title"], "similarity": round(float(scores[candidate]) * 100, 1), "source_url": record["source_url"]})
        if record["resolution_available"]:
            evidence.append({"issue_id": record["issue_id"], "title": record["title"], "resolution_summary": record["resolution_summary"], "steps": record["resolution_steps"], "source_url": record["source_url"]})
    has_evidence = bool(evidence)
    return {
        "query": query,
        "answer": evidence[0]["resolution_summary"] if has_evidence else "The imported issue dataset does not contain enough resolution evidence for a grounded answer.",
        "steps": evidence[0]["steps"] if has_evidence else [],
        "confidence": "High" if len(evidence) >= 2 else ("Medium" if has_evidence else "Low"),
        "resolution_available": has_evidence,
        "escalation_recommended": not has_evidence,
        "matches": matches,
        "evidence": evidence,
    }


def record_support_feedback(issue_id: str, resolved: bool, comment: str = "") -> dict[str, Any]:
    path = INDEX_DIR / "support_feedback.json"
    entries = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    entries.append({"issue_id": issue_id, "resolved": resolved, "comment": comment.strip(), "timestamp": datetime.now(timezone.utc).isoformat()})
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    return entries[-1]


def export_csv(kind: str, filters: Optional[dict[str, Any]] = None) -> str:
    records = _filtered_records(filters)
    if kind == "clusters":
        rows = list_clusters(0, 100000, filters)["items"]
    elif kind == "kpis":
        analytics = get_analytics(filters)
        rows = [{"metric": key, "value": value if not isinstance(value, (dict, list)) else json.dumps(value)} for key, value in analytics.items()]
    else:
        rows = []
        for record in records:
            row = dict(record)
            row["labels"] = "; ".join(record["labels"])
            row["comments"] = "\n".join(record["comments"])
            row["similar_issue_count"] = sum(item["cluster_id"] == record["cluster_id"] for item in records) - 1
            row["severity_priority"] = record["priority"]
            row.pop("search_text", None)
            rows.append(row)
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()