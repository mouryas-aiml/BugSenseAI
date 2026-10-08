"""
LLM client — provider-agnostic wrapper with structured JSON output.

Supported providers (set LLM_PROVIDER in .env):
  gemini  → Google Gemini (recommended, free tier available)
  openai  → OpenAI GPT-4o-mini (strict schema mode)
  groq    → Groq llama-3.3-70b (json_object mode)
  ollama  → Local Ollama (json_object mode)

All providers enforce JSON output at the API level.
Timeouts: 60s default (configurable via LLM_TIMEOUT_SECONDS).
"""

import os
import logging
from dotenv import load_dotenv
from typing import Any, Tuple
import openai
import httpx

load_dotenv()
logger = logging.getLogger(__name__)

PROVIDERS = ["gemini", "openai", "groq", "ollama"]
_DEFAULT_TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))

# JSON schema enforced at the API level for OpenAI (strict mode).
# Gemini / Groq / Ollama use json_object / mime type which guarantees valid JSON.
TRIAGE_JSON_SCHEMA = {
    "name": "triage_output",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "title":                    {"type": "string"},
            "summary":                  {"type": "string"},
            "severity":                 {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
            "component":                {"type": "string"},
            "bug_type":                 {"type": "string"},
            "affected_users":           {"type": "string"},
            "impact":                   {"type": "string"},
            "reproduction_steps":       {"type": "array", "items": {"type": "string"}},
            "expected_behavior":        {"type": "string"},
            "actual_behavior":          {"type": "string"},
            "environment":              {"type": "string"},
            "error_messages":           {"type": "array", "items": {"type": "string"}},
            "root_cause_hypothesis":    {"type": "string"},
            "missing_information":      {"type": "array", "items": {"type": "string"}},
            "extracted_entities":       {"type": "array", "items": {"type": "string"}},
            "suggested_labels":         {"type": "array", "items": {"type": "string"}},
            "priority_reasoning":       {"type": "string"},
            "suggested_assignee_team":  {"type": "string"},
            "confidence":               {"type": "string", "enum": ["High", "Medium", "Low"]},
        },
        "required": [
            "title", "summary", "severity", "component", "bug_type",
            "affected_users", "impact", "reproduction_steps",
            "expected_behavior", "actual_behavior", "environment",
            "error_messages", "root_cause_hypothesis", "missing_information",
            "extracted_entities", "suggested_labels", "priority_reasoning",
            "suggested_assignee_team", "confidence",
        ],
        "additionalProperties": False,
    },
}


def get_provider_and_model() -> Tuple[str, str]:
    """Return (provider, model_name) from environment."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported LLM_PROVIDER '{provider}'. Choose from: {PROVIDERS}")

    model_map = {
        "gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "groq":   os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "ollama": os.getenv("OLLAMA_MODEL", "llama3.2"),
    }
    return provider, model_map[provider]


def generate_structured_ticket(prompt: str) -> str:
    """Call the configured LLM and return a JSON string.

    All providers enforce JSON output at the API level.
    Raises ValueError with a clear message on failure.
    Enforces a timeout to avoid hanging on slow LLM providers.
    """
    provider, model_name = get_provider_and_model()
    logger.info(f"LLM call: provider={provider}, model={model_name}")

    try:
        if provider == "gemini":
            return _call_gemini(prompt, model_name)
        elif provider == "openai":
            return _call_openai(prompt, model_name)
        elif provider == "groq":
            return _call_groq(prompt, model_name)
        elif provider == "ollama":
            return _call_ollama(prompt, model_name)
    except ValueError:
        raise
    except Exception as e:
        err_type = type(e).__name__
        msg = str(e)
        # Translate common errors to human-readable messages
        if "connect" in msg.lower() or "connection" in msg.lower() or "refused" in msg.lower():
            raise ValueError(
                f"Cannot connect to {provider.upper()} LLM service. "
                f"Check that the service is running and your API key is valid. "
                f"(Detail: {msg})"
            )
        if "timeout" in msg.lower():
            raise ValueError(f"LLM request timed out after {_DEFAULT_TIMEOUT}s. Try again or increase LLM_TIMEOUT_SECONDS.")
        if "401" in msg or "authentication" in msg.lower() or "api_key" in msg.lower():
            raise ValueError(f"LLM authentication failed. Check your {provider.upper()}_API_KEY in .env.")
        if "429" in msg or "rate" in msg.lower():
            raise ValueError("LLM rate limit reached. Wait a moment and try again.")
        raise ValueError(f"LLM error ({err_type}): {msg}")

    raise ValueError("Unhandled LLM provider")


def _call_gemini(prompt: str, model_name: str) -> str:
    """Call Google Gemini using the google-genai SDK with automated model fallback."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ValueError("google-genai package not installed. Run: pip install google-genai")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env. Get a free key at https://aistudio.google.com/")

    client = genai.Client(api_key=api_key)

    # Try requested model, followed by reliable fallbacks
    models_to_try = [model_name]
    for fallback in ["gemini-flash-lite-latest", "gemini-flash-latest"]:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error = None
    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=3000,
                    response_mime_type="application/json",
                ),
            )
            raw = (response.text or "").strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            return raw.strip()
        except Exception as e:
            last_error = e
            logger.warning(f"Gemini call with model '{m}' failed: {e}. Trying fallback...")
            continue

    raise last_error or ValueError("Gemini call failed for all candidate models")


def _call_openai(prompt: str, model_name: str) -> str:
    """Call OpenAI with strict JSON schema enforcement."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in .env.")

    client = openai.OpenAI(
        api_key=api_key,
        timeout=_DEFAULT_TIMEOUT,
    )
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_completion_tokens=2500,
        response_format={"type": "json_schema", "json_schema": TRIAGE_JSON_SCHEMA},
    )
    return response.choices[0].message.content.strip()


def _call_groq(prompt: str, model_name: str) -> str:
    """Call Groq with json_object mode."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env. Get a free key at https://console.groq.com/")

    http_client = httpx.Client(
        transport=httpx.HTTPTransport(retries=1),
        timeout=_DEFAULT_TIMEOUT,
    )
    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        http_client=http_client,
    )
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_completion_tokens=2500,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()


def _call_ollama(prompt: str, model_name: str) -> str:
    """Call local Ollama with json_object mode."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    http_client = httpx.Client(
        base_url=base_url,
        timeout=_DEFAULT_TIMEOUT,
    )
    client = openai.OpenAI(
        base_url=base_url,
        api_key="ollama",
        http_client=http_client,
    )
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_completion_tokens=2500,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()


def check_llm_connectivity() -> dict:
    """Probe the configured LLM provider. Returns {status, provider, model, message}."""
    provider, model_name = get_provider_and_model()
    try:
        if provider == "gemini":
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return {
                    "status": "error",
                    "provider": provider,
                    "model": model_name,
                    "message": "GEMINI_API_KEY is not configured in .env",
                }
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model=model_name,
                contents="Respond with: OK",
            )
            return {
                "status": "ok",
                "provider": provider,
                "model": model_name,
                "message": "Gemini API reachable and active",
            }
        else:
            result = generate_structured_ticket(
                "Respond with exactly this JSON and nothing else: "
                '{"title":"health check","summary":"ok","severity":"P4","component":"system",'
                '"bug_type":"test","affected_users":"none","impact":"none","reproduction_steps":[],'
                '"expected_behavior":"ok","actual_behavior":"ok","environment":"","error_messages":[],'
                '"root_cause_hypothesis":"","missing_information":[],"extracted_entities":[],'
                '"suggested_labels":[],"priority_reasoning":"health check","suggested_assignee_team":"system",'
                '"confidence":"High"}'
            )
            return {"status": "ok", "provider": provider, "model": model_name, "message": "LLM reachable"}
    except Exception as e:
        return {"status": "error", "provider": provider, "model": model_name, "message": str(e)}

