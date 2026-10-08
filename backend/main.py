"""
BugSenseAI — FastAPI Backend

Endpoints:
  GET  /health              → Simple liveness probe
  GET  /health/detailed     → LLM + config status check
  POST /triage              → Triage a single raw bug report
  POST /triage/batch        → Triage multiple bug reports
  POST /triage/ci           → Triage JUnit XML test failures from CI
  GET  /history             → Paginated triage history
  GET  /analytics           → Aggregate statistics
  GET  /duplicates          → Current vector store contents

All endpoints return structured JSON. Errors return {detail: "..."}.
"""

import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    BugInput, TriageOutput,
    CITriageRequest, CITriageResponse, CITriageResult,
    BatchBugInput, BatchTriageResponse, BatchTriageResult,
    HealthResponse,
)
from .triage import triage_bug
from .ci_parser import parse_junit_xml, build_bug_description
from .analytics import get_analytics, get_history
from .llm_client import check_llm_connectivity, get_provider_and_model
from .vector_store import _load_store
from .feedback_store import _load as _load_feedback

logger = logging.getLogger(__name__)

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"

app = FastAPI(
    title="BugSenseAI",
    description="AI-powered automated bug report summarization and intelligent triage platform",
    version="2.0.0",
)

# Allow Streamlit dev server + any localhost variant
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:8501", "http://localhost:8502", "http://127.0.0.1:8501",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Simple liveness probe."""
    return {"status": "healthy"}


@app.get("/health/detailed", response_model=HealthResponse)
async def health_detailed():
    """Detailed health check including LLM reachability."""
    llm_check = check_llm_connectivity()
    provider, model = get_provider_and_model()

    vector_store = _load_store()
    feedback = _load_feedback()
    total_triaged = len(list(OUTPUTS_DIR.glob("triaged_*.json"))) if OUTPUTS_DIR.exists() else 0

    return HealthResponse(
        status="healthy" if llm_check["status"] == "ok" else "degraded",
        backend="online",
        llm_provider=provider,
        llm_status=llm_check["status"],
        llm_model=model,
        vector_store_entries=len(vector_store),
        feedback_entries=len(feedback),
        total_triaged=total_triaged,
    )


# ── Single Triage ──────────────────────────────────────────────────────────────

@app.post("/triage", response_model=TriageOutput)
async def triage_endpoint(input: BugInput):
    """Triage a single raw bug report through the full AI pipeline."""
    try:
        result = triage_bug(input.bug, save_output=True)
        return TriageOutput(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Triage failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Triage failed: {str(e)}")


# ── Batch Triage ───────────────────────────────────────────────────────────────

@app.post("/triage/batch", response_model=BatchTriageResponse)
async def triage_batch(input: BatchBugInput):
    """Triage multiple bug reports in a single request.

    Processes each report sequentially through the full AI pipeline.
    Failed reports are included in results with success=False.
    Maximum 20 reports per batch.
    """
    if len(input.reports) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 reports per batch request")

    results = []
    succeeded = 0
    failed = 0

    for i, raw in enumerate(input.reports):
        preview = raw.strip()[:80]
        start = time.time()
        try:
            triage = triage_bug(raw, save_output=True)
            elapsed = int((time.time() - start) * 1000)
            results.append(BatchTriageResult(
                index=i,
                input_preview=preview,
                success=True,
                triage=triage,
                processing_time_ms=elapsed,
            ))
            succeeded += 1
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            logger.warning(f"Batch triage failed for report #{i}: {e}")
            results.append(BatchTriageResult(
                index=i,
                input_preview=preview,
                success=False,
                error=str(e),
                processing_time_ms=elapsed,
            ))
            failed += 1

    return BatchTriageResponse(
        total=len(input.reports),
        succeeded=succeeded,
        failed=failed,
        results=results,
        source_filename=input.source_filename,
    )


# ── CI / JUnit Triage ──────────────────────────────────────────────────────────

@app.post("/triage/ci", response_model=CITriageResponse)
async def triage_ci(request: CITriageRequest):
    """Ingest a JUnit XML report from CI and triage each test failure.

    Accepts the standard JUnit XML format produced by pytest (--junit-xml),
    JUnit, TestNG, Mocha, and most other test frameworks.

    Example curl from GitHub Actions:
        curl -X POST http://localhost:8000/triage/ci \\
          -H "Content-Type: application/json" \\
          -d '{"junit_xml": "<testsuites>...</testsuites>",
               "branch": "main",
               "commit_sha": "${{ github.sha }}"}'
    """
    try:
        failures = parse_junit_xml(request.junit_xml)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    total_found = len(failures)
    to_triage = failures[: request.max_failures]

    results = []
    for failure in to_triage:
        bug_text = build_bug_description(
            failure,
            branch=request.branch,
            commit_sha=request.commit_sha,
            run_url=request.run_url,
        )
        try:
            triage = triage_bug(bug_text, save_output=True)
        except Exception as e:
            logger.warning(f"Triage failed for {failure['classname']}::{failure['test_name']}: {e}")
            continue

        jira_ticket = None
        if request.create_tickets:
            try:
                from .jira_client import create_jira_ticket, find_similar_in_jira
                from .vector_store import find_similar, store_embedding
                if not find_similar(triage) and not find_similar_in_jira(triage):
                    ticket = create_jira_ticket(triage)
                    store_embedding(triage, ticket["key"], ticket["url"])
                    jira_ticket = ticket["key"]
            except Exception as e:
                logger.warning(f"Jira ticket creation failed (non-fatal): {e}")

        results.append(CITriageResult(
            test_name=failure["test_name"],
            classname=failure["classname"],
            failure_type=failure["failure_type"],
            failure_message=failure["failure_message"],
            triage=triage,
            jira_ticket=jira_ticket,
        ))

    return CITriageResponse(
        total_failures_found=total_found,
        triaged_count=len(results),
        branch=request.branch,
        commit_sha=request.commit_sha,
        run_url=request.run_url,
        results=results,
    )


# ── History & Analytics ────────────────────────────────────────────────────────

@app.get("/history")
async def history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Return paginated triage history from saved outputs."""
    return get_history(limit=limit, offset=offset)


@app.get("/analytics")
async def analytics():
    """Return aggregate statistics from all triage history."""
    return get_analytics()


@app.get("/duplicates")
async def duplicates():
    """Return all entries in the local vector store (for duplicate detection preview)."""
    store = _load_store()
    # Return without the raw embedding vectors (too large for API response)
    return [
        {
            "jira_key": e.get("jira_key", ""),
            "title": e.get("title", ""),
            "text": e.get("text", ""),
            "jira_url": e.get("jira_url", ""),
        }
        for e in store
    ]


@app.post("/duplicates/sync")
async def duplicates_sync():
    """Index historical triaged outputs into the vector store."""
    from .vector_store import sync_from_outputs, _load_store
    added = sync_from_outputs()
    return {"added": added, "total": len(_load_store())}


@app.post("/duplicates/query")
async def duplicates_query(payload: dict):
    """Find semantic duplicates for a given triage payload."""
    from .vector_store import find_all_similar
    top_k = payload.pop("top_k", 5) if isinstance(payload, dict) else 5
    matches = find_all_similar(payload, top_k=top_k)
    return {"matches": matches}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
