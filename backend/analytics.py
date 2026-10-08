"""
Analytics — aggregate statistics from saved triage outputs.

Reads all triaged_*.json files from the outputs/ directory and
computes statistics suitable for the Analytics Dashboard.
No external database required — works off the flat JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

logger = logging.getLogger(__name__)

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


def _load_all_outputs() -> List[Dict[str, Any]]:
    """Load every triaged_*.json from the outputs directory."""
    results = []
    if not OUTPUTS_DIR.exists():
        return results
    for f in sorted(OUTPUTS_DIR.glob("triaged_*.json"), reverse=True):
        try:
            with open(f, "r") as fh:
                data = json.load(fh)
                data["_filename"] = f.name
                # Extract timestamp from filename: triaged_YYYYMMDD_HHMMSS.json
                stem = f.stem  # e.g. "triaged_20260329_191857"
                parts = stem.split("_")
                if len(parts) >= 3:
                    data["_timestamp"] = f"{parts[1][:4]}-{parts[1][4:6]}-{parts[1][6:]} {parts[2][:2]}:{parts[2][2:4]}:{parts[2][4:]}"
                results.append(data)
        except Exception as e:
            logger.warning(f"Could not load {f.name}: {e}")
    return results


def get_analytics() -> Dict[str, Any]:
    """Compute aggregate analytics from all saved triage outputs."""
    outputs = _load_all_outputs()
    total = len(outputs)

    if total == 0:
        return {
            "total_reports": 0,
            "severity_distribution": {"P1": 0, "P2": 0, "P3": 0, "P4": 0},
            "component_distribution": {},
            "team_distribution": {},
            "confidence_distribution": {"High": 0, "Medium": 0, "Low": 0},
            "avg_completeness_score": 0,
            "requires_human_review_count": 0,
            "duplicate_count": 0,
            "recent_reports": [],
        }

    severity_dist: Dict[str, int] = defaultdict(int)
    component_dist: Dict[str, int] = defaultdict(int)
    team_dist: Dict[str, int] = defaultdict(int)
    confidence_dist: Dict[str, int] = defaultdict(int)
    completeness_scores: List[int] = []
    human_review_count = 0
    duplicate_count = 0

    for r in outputs:
        # Severity
        sev = r.get("severity", "P3")
        severity_dist[sev] += 1

        # Component
        comp = r.get("component", "").strip()
        if comp:
            component_dist[comp.title()] += 1

        # Team
        team = r.get("suggested_assignee_team", "").strip()
        if team:
            team_dist[team] += 1

        # Confidence
        conf = r.get("confidence", "Medium")
        confidence_dist[conf] += 1

        # Completeness
        cs = r.get("completeness_score", 0)
        if isinstance(cs, int) and cs > 0:
            completeness_scores.append(cs)

        # Human review
        labels = r.get("suggested_labels", [])
        if "needs-human-review" in labels or r.get("requires_human_review", False):
            human_review_count += 1

        # Duplicates
        if r.get("is_duplicate", False):
            duplicate_count += 1

    avg_completeness = (
        round(sum(completeness_scores) / len(completeness_scores), 1)
        if completeness_scores else 0.0
    )

    # Recent 10 reports for preview table
    recent_reports = []
    for r in outputs[:10]:
        recent_reports.append({
            "timestamp": r.get("_timestamp", ""),
            "title": r.get("title", "Untitled"),
            "severity": r.get("severity", "?"),
            "component": r.get("component", ""),
            "team": r.get("suggested_assignee_team", ""),
            "confidence": r.get("confidence", ""),
            "completeness_score": r.get("completeness_score", 0),
        })

    return {
        "total_reports": total,
        "severity_distribution": {
            "P1": severity_dist.get("P1", 0),
            "P2": severity_dist.get("P2", 0),
            "P3": severity_dist.get("P3", 0),
            "P4": severity_dist.get("P4", 0),
        },
        "component_distribution": dict(
            sorted(component_dist.items(), key=lambda x: x[1], reverse=True)[:15]
        ),
        "team_distribution": dict(
            sorted(team_dist.items(), key=lambda x: x[1], reverse=True)
        ),
        "confidence_distribution": {
            "High": confidence_dist.get("High", 0),
            "Medium": confidence_dist.get("Medium", 0),
            "Low": confidence_dist.get("Low", 0),
        },
        "avg_completeness_score": avg_completeness,
        "requires_human_review_count": human_review_count,
        "duplicate_count": duplicate_count,
        "recent_reports": recent_reports,
    }


def get_history(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Return paginated triage history."""
    outputs = _load_all_outputs()
    total = len(outputs)
    page = outputs[offset: offset + limit]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": page,
    }
