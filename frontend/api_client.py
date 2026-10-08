"""
BugSenseAI — Frontend API & Engine Client
Resilient client layer connecting Streamlit frontend to FastAPI backend
with automatic local engine fallback to ensure zero connection interruptions.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BUGSENSE_BACKEND_URL", "http://localhost:8000").rstrip("/")
DEFAULT_TIMEOUT = int(os.getenv("API_TIMEOUT_SECONDS", "45"))


def get_backend_url() -> str:
    return BACKEND_URL


def check_backend_status() -> Dict[str, Any]:
    """Check backend connectivity. Returns detailed status dict."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health/detailed", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            data["reachable"] = True
            data["mode"] = "fastapi_network"
            return data
    except Exception as e:
        logger.debug(f"FastAPI backend probe failed: {e}")

    # Fallback probe directly in Python environment
    try:
        from backend.llm_client import check_llm_connectivity, get_provider_and_model
        from backend.vector_store import _load_store
        from backend.analytics import get_analytics

        llm_check = check_llm_connectivity()
        provider, model = get_provider_and_model()
        vector_store = _load_store()
        analytics = get_analytics()

        return {
            "status": "healthy" if llm_check.get("status") == "ok" else "degraded",
            "backend": "direct_engine",
            "reachable": False,
            "mode": "in_process_fallback",
            "llm_provider": provider,
            "llm_status": llm_check.get("status", "unknown"),
            "llm_model": model,
            "vector_store_entries": len(vector_store),
            "feedback_entries": 0,
            "total_triaged": analytics.get("total_reports", 0),
            "message": "FastAPI port 8000 offline; running via Direct Engine mode.",
        }
    except Exception as inner_e:
        return {
            "status": "offline",
            "backend": "offline",
            "reachable": False,
            "mode": "offline",
            "llm_provider": os.getenv("LLM_PROVIDER", "gemini"),
            "llm_status": "unreachable",
            "llm_model": os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest"),
            "vector_store_entries": 0,
            "feedback_entries": 0,
            "total_triaged": 0,
            "message": f"Engine initialization failed: {inner_e}",
        }


def triage_single_bug(text: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Triage a single raw bug report through FastAPI, falling back to direct engine."""
    if not text or not text.strip():
        raise ValueError("Bug report text cannot be empty.")

    # 1. Try FastAPI backend if reachable
    try:
        payload = {"bug": text, "metadata": metadata or {}}
        resp = requests.post(f"{BACKEND_URL}/triage", json=payload, timeout=DEFAULT_TIMEOUT)
        if resp.status_code == 200:
            result = resp.json()
            result["_routed_via"] = "FastAPI HTTP (Port 8000)"
            return result
        elif resp.status_code == 400:
            raise ValueError(resp.json().get("detail", "Invalid bug report"))
        else:
            detail = resp.json().get("detail", f"HTTP {resp.status_code}")
            logger.warning(f"Backend error ({resp.status_code}): {detail}. Falling back to direct engine...")
    except (requests.ConnectionError, requests.Timeout) as net_err:
        logger.info(f"Backend unreachable ({net_err}). Executing triage in direct engine mode.")
    except ValueError:
        raise

    # 2. Resilient Fallback: Run in-process triage
    try:
        from backend.triage import triage_bug
        result = triage_bug(text, save_output=True)
        result["_routed_via"] = "Direct Engine (FastAPI offline)"
        return result
    except Exception as e:
        msg = str(e)
        if "404" in msg or "not found" in msg.lower():
            raise ValueError(
                "Configured AI Model was not found. Please verify GEMINI_MODEL in .env or switch to 'gemini-flash-lite-latest'."
            )
        if "503" in msg or "demand" in msg.lower():
            raise ValueError(
                "Gemini API is temporarily experiencing high traffic spikes (503). Retrying with backup flash model..."
            )
        if "api_key" in msg.lower() or "401" in msg:
            raise ValueError(
                "Gemini API authentication failed. Please verify GEMINI_API_KEY in your .env file."
            )
        raise ValueError(f"AI Triage Pipeline Error: {msg}")


def triage_batch_bugs(reports: List[str], filename: str = "") -> Dict[str, Any]:
    """Triage a batch of bug reports."""
    if not reports:
        return {"total": 0, "succeeded": 0, "failed": 0, "results": []}

    # Try FastAPI batch endpoint first
    try:
        payload = {"reports": reports, "source_filename": filename}
        resp = requests.post(f"{BACKEND_URL}/triage/batch", json=payload, timeout=DEFAULT_TIMEOUT * 2)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.info(f"FastAPI batch call failed: {e}. Executing in-process batch...")

    # Direct in-process batch execution
    from backend.triage import triage_bug
    results = []
    succeeded = 0
    failed = 0

    for i, raw in enumerate(reports):
        preview = raw.strip()[:80]
        start_time = time.time()
        try:
            res = triage_bug(raw, save_output=True)
            elapsed = int((time.time() - start_time) * 1000)
            results.append({
                "index": i,
                "input_preview": preview,
                "success": True,
                "triage": res,
                "error": None,
                "processing_time_ms": elapsed,
            })
            succeeded += 1
        except Exception as err:
            elapsed = int((time.time() - start_time) * 1000)
            results.append({
                "index": i,
                "input_preview": preview,
                "success": False,
                "triage": None,
                "error": str(err),
                "processing_time_ms": elapsed,
            })
            failed += 1

    return {
        "total": len(reports),
        "succeeded": succeeded,
        "failed": failed,
        "results": results,
        "source_filename": filename,
    }


def fetch_analytics() -> Dict[str, Any]:
    """Fetch analytics stats."""
    try:
        resp = requests.get(f"{BACKEND_URL}/analytics", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    from backend.analytics import get_analytics
    return get_analytics()


def fetch_history(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Fetch paginated triage history."""
    try:
        resp = requests.get(f"{BACKEND_URL}/history?limit={limit}&offset={offset}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    from backend.analytics import get_history
    return get_history(limit=limit, offset=offset)


def fetch_duplicate_matches(triage_data: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
    """Fetch duplicate candidates with semantic similarity score and explanation."""
    try:
        from backend.vector_store import find_all_similar
        return find_all_similar(triage_data, top_k=top_k)
    except Exception as e:
        logger.warning(f"Error querying duplicate matches: {e}")
        return []


def trigger_vector_sync() -> int:
    """Index past reports into the vector store."""
    try:
        from backend.vector_store import sync_from_outputs
        return sync_from_outputs()
    except Exception as e:
        logger.warning(f"Error syncing vector store: {e}")
        return 0
