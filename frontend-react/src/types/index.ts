/**
 * BugSenseAI — TypeScript Domain Models
 * Synchronized with backend Pydantic schemas and TCS problem statement.
 */

export type SeverityLevel = 'P1' | 'P2' | 'P3' | 'P4';
export type ConfidenceLevel = 'High' | 'Medium' | 'Low';

export interface SimilarBugMatch {
  id?: string;
  jira_key?: string;
  jira_url?: string;
  title: string;
  similarity: number;
  component?: string;
  severity?: string;
  summary?: string;
  actual_behavior?: string;
  explanation?: string;
  source?: string;
}

export interface TriageOutput {
  title: string;
  summary: string;
  severity: SeverityLevel;
  confidence: ConfidenceLevel;
  bug_type: string;
  component: string;
  priority_reasoning: string;
  affected_users: string;
  impact: string;
  reproduction_steps: string[];
  expected_behavior: string;
  actual_behavior: string;
  environment: string;
  error_messages: string[];
  root_cause_hypothesis: string;
  missing_information: string[];
  extracted_entities: string[];
  suggested_labels: string[];
  suggested_assignee_team: string;
  related_test_areas: string[];
  completeness_score: number;
  requires_human_review: boolean;
  similar_bugs?: SimilarBugMatch[];
  is_duplicate?: boolean;
  _pii_redacted?: boolean;
  _pii_redaction_types?: string[];
  _processing_time_ms?: number;
  _timestamp?: string;
  _filename?: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'offline';
  backend: string;
  llm_provider: string;
  llm_status: string;
  llm_model: string;
  vector_store_entries: number;
  feedback_entries: number;
  total_triaged: number;
  reachable?: boolean;
  message?: string;
}

export interface AnalyticsData {
  total_reports: number;
  severity_distribution: Record<string, number>;
  component_distribution: Record<string, number>;
  team_distribution: Record<string, number>;
  confidence_distribution: Record<string, number>;
  avg_completeness_score: number;
  requires_human_review_count: number;
  duplicate_count: number;
  recent_reports: Array<{
    timestamp: string;
    title: string;
    severity: string;
    component: string;
    team: string;
    confidence: string;
    completeness_score: number;
  }>;
}

export interface BatchTriageResultItem {
  index: number;
  input_preview: string;
  success: boolean;
  triage?: TriageOutput;
  error?: string;
  processing_time_ms: number;
}

export interface BatchTriageResponse {
  total: number;
  succeeded: number;
  failed: number;
  results: BatchTriageResultItem[];
  source_filename?: string;
}

export interface StoredBugItem {
  jira_key: string;
  title: string;
  text: string;
  jira_url?: string;
}
