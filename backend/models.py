from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Any, Dict, List, Optional
from enum import Enum


class Severity(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class BugInput(BaseModel):
    bug: str = Field(..., min_length=1, description="Raw unstructured bug report")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Optional metadata (version, env, reporter)")


class SimilarBug(BaseModel):
    id: str = ""
    title: str = ""
    similarity: float = 0.0
    source: str = ""  # "local" | "jira"


class TriageOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Core identity
    title: str = Field(..., min_length=5)
    summary: str = Field(default="", description="Concise 1–2 sentence executive summary")
    severity: Severity
    confidence: Confidence

    # Classification
    bug_type: str = ""
    component: str = ""
    priority_reasoning: str = ""

    # Impact
    affected_users: str = ""
    impact: str = Field(default="", description="Business/user impact statement")

    # Reproduction
    reproduction_steps: List[str] = Field(default_factory=list)
    expected_behavior: str = ""
    actual_behavior: str = ""
    environment: str = Field(default="", description="OS, browser, version, env extracted from report")
    error_messages: List[str] = Field(default_factory=list, description="Extracted error codes or messages")

    # Intelligence
    root_cause_hypothesis: str = Field(default="", description="[HYPOTHESIS] Possible root cause — not confirmed")
    missing_information: List[str] = Field(default_factory=list, description="What's missing from the report")
    extracted_entities: List[str] = Field(default_factory=list, description="Emails, versions, IDs, components found")

    # Routing
    suggested_labels: List[str] = Field(default_factory=list)
    suggested_assignee_team: str = ""
    related_test_areas: List[str] = Field(default_factory=list)

    # Quality
    completeness_score: int = Field(default=0, ge=0, le=100, description="Report quality 0–100")
    requires_human_review: bool = False

    # Duplicate detection (populated post-LLM)
    similar_bugs: List[SimilarBug] = Field(default_factory=list)
    is_duplicate: bool = False


class CITriageRequest(BaseModel):
    junit_xml: str = Field(..., description="JUnit XML string from CI test run")
    branch: str = ""
    commit_sha: str = ""
    run_url: str = ""
    max_failures: int = Field(default=10, ge=1, le=50, description="Cap on failures to triage per run")
    create_tickets: bool = False


class CITriageResult(BaseModel):
    test_name: str
    classname: str
    failure_type: str
    failure_message: str
    triage: Dict[str, Any]
    jira_ticket: Optional[str] = None


class CITriageResponse(BaseModel):
    total_failures_found: int
    triaged_count: int
    branch: str
    commit_sha: str
    run_url: str
    results: List[CITriageResult]


class BatchBugInput(BaseModel):
    reports: List[str] = Field(..., min_length=1, description="List of raw bug report strings")
    source_filename: str = ""


class BatchTriageResult(BaseModel):
    index: int
    input_preview: str  # first 80 chars of raw input
    success: bool
    triage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: int = 0


class BatchTriageResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: List[BatchTriageResult]
    source_filename: str = ""


class AnalyticsResponse(BaseModel):
    total_reports: int
    severity_distribution: Dict[str, int]
    component_distribution: Dict[str, int]
    team_distribution: Dict[str, int]
    confidence_distribution: Dict[str, int]
    avg_completeness_score: float
    requires_human_review_count: int
    duplicate_count: int
    recent_reports: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    backend: str
    llm_provider: str
    llm_status: str
    llm_model: str
    vector_store_entries: int
    feedback_entries: int
    total_triaged: int
