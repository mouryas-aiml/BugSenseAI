"""
Vector similarity store for semantic duplicate detection.
Embeds bug reports using sentence-transformers and compares via cosine similarity.
Much more accurate than keyword matching — catches duplicates even with different wording.
"""

import json
import os
import numpy as np
from pathlib import Path
from typing import Optional
from sentence_transformers import SentenceTransformer

STORE_PATH = Path(__file__).parent.parent / "outputs" / "vector_store.json"
MODEL_NAME = "all-MiniLM-L6-v2"  # ~80MB, fast, accurate for semantic similarity
SIMILARITY_THRESHOLD = 0.68  # 0.0 - 1.0, higher = stricter matching

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _load_store() -> list:
    if not STORE_PATH.exists():
        return []
    with open(STORE_PATH, "r") as f:
        return json.load(f)


def _save_store(store: list) -> None:
    STORE_PATH.parent.mkdir(exist_ok=True)
    with open(STORE_PATH, "w") as f:
        json.dump(store, f, indent=2)


def _bug_to_text(triage: dict) -> str:
    """Combine the most meaningful fields into one string for embedding."""
    parts = [
        triage.get("title", ""),
        triage.get("component", ""),
        triage.get("actual_behavior", ""),
        triage.get("bug_type", ""),
    ]
    return " ".join(p for p in parts if p).strip()


def cosine_similarity(a: list, b: list) -> float:
    va = np.array(a)
    vb = np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def embed_text(text: str) -> list:
    """Encode a string into an embedding vector using the shared model."""
    return _get_model().encode(text).tolist()


def find_similar(triage: dict) -> Optional[dict]:
    """
    Compare triage against stored embeddings.
    Returns {"jira_key": ..., "title": ..., "similarity": ...} if duplicate found, else None.
    """
    store = _load_store()
    if not store:
        return None

    text = _bug_to_text(triage)
    if not text:
        return None

    embedding = embed_text(text)

    best_match = None
    best_score = 0.0

    for entry in store:
        score = cosine_similarity(embedding, entry["embedding"])
        if score > best_score:
            best_score = score
            best_match = entry

    if best_score >= SIMILARITY_THRESHOLD and best_match:
        return {
            "jira_key": best_match["jira_key"],
            "jira_url": best_match["jira_url"],
            "title": best_match["title"],
            "similarity": round(best_score * 100, 1),
        }

    return None


def find_all_similar(triage: dict, top_k: int = 5, threshold: float = 0.30) -> list:
    """Find top similar reports above threshold with match rationale.
    
    Returns list of dicts with id, title, similarity (0-100), component, severity, and rationale.
    """
    store = _load_store()
    if not store:
        return []

    text = _bug_to_text(triage)
    if not text:
        return []

    embedding = embed_text(text)
    matches = []

    for entry in store:
        score = cosine_similarity(embedding, entry.get("embedding", []))
        if score >= threshold:
            pct = round(score * 100, 1)
            # Generate similarity explanation
            comp_a = triage.get("component", "General")
            comp_b = entry.get("component", "General")
            same_comp = comp_a.lower() == comp_b.lower() if comp_a and comp_b else False
            
            explanation = (
                f"High semantic overlap ({pct}%). "
                f"{'Same component: ' + comp_a if same_comp else 'Cross-component similarity'}. "
                f"Shared failure patterns in behavior and error description."
            )
            
            matches.append({
                "id": entry.get("jira_key") or entry.get("id", "BUG-HIST"),
                "title": entry.get("title", "Untitled"),
                "similarity": pct,
                "component": entry.get("component", "General"),
                "severity": entry.get("severity", "P3"),
                "summary": entry.get("summary", ""),
                "actual_behavior": entry.get("actual_behavior", ""),
                "explanation": explanation,
                "jira_url": entry.get("jira_url", ""),
            })

    # Sort descending by similarity
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return matches[:top_k]


def store_embedding(triage: dict, jira_key: str, jira_url: str = "") -> None:
    """Save a new bug embedding after its Jira ticket is created or triaged."""
    text = _bug_to_text(triage)
    if not text:
        return

    embedding = embed_text(text)
    store = _load_store()

    # Avoid duplicate IDs
    for item in store:
        if item.get("jira_key") == jira_key:
            return

    store.append({
        "jira_key": jira_key,
        "id": jira_key,
        "jira_url": jira_url,
        "title": triage.get("title", ""),
        "component": triage.get("component", ""),
        "severity": triage.get("severity", "P3"),
        "summary": triage.get("summary", ""),
        "actual_behavior": triage.get("actual_behavior", ""),
        "text": text,
        "embedding": embedding,
    })

    _save_store(store)


def sync_from_outputs() -> int:
    """Index all historical triaged_*.json from outputs/ into the vector store."""
    outputs_dir = STORE_PATH.parent
    if not outputs_dir.exists():
        return 0

    store = _load_store()
    existing_keys = {item.get("jira_key") or item.get("id") for item in store}
    
    count = 0
    for f in outputs_dir.glob("triaged_*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            file_id = f.stem.replace("triaged_", "BUG-")
            if file_id in existing_keys:
                continue

            text = _bug_to_text(data)
            if not text:
                continue

            emb = embed_text(text)
            store.append({
                "jira_key": file_id,
                "id": file_id,
                "jira_url": "",
                "title": data.get("title", ""),
                "component": data.get("component", ""),
                "severity": data.get("severity", "P3"),
                "summary": data.get("summary", ""),
                "actual_behavior": data.get("actual_behavior", ""),
                "text": text,
                "embedding": emb,
            })
            existing_keys.add(file_id)
            count += 1
        except Exception:
            continue

    if count > 0:
        _save_store(store)
    return count

