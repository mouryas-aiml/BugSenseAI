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

export interface IssueRecord {
  issue_id: string;
  title: string;
  summary: string;
  body: string;
  comments: string[];
  labels: string[];
  state: string;
  category: string;
  component: string;
  priority: string;
  created_at: string;
  updated_at: string;
  closed_at: string;
  source_url: string;
  discussion_count: number;
  cluster_id: string;
  cluster_name: string;
  resolution_available: boolean;
  resolution_summary: string;
  resolution_steps: string[];
  confidence: 'High' | 'Medium' | 'Low';
  similar_reports?: Array<{ issue_id: string; title: string; similarity: number }>;
  evidence_sources?: string[];
  escalation_recommendation?: string;
}

export interface IssueCluster {
  cluster_id: string;
  cluster_name: string;
  report_count: number;
  percentage: number;
  representative_issue_id: string;
  representative_title: string;
  category: string;
  common_symptoms: string[];
  related_issue_ids: string[];
  resolution_available: boolean;
  resolution_summary: string;
}

export interface IssueAnalytics {
  total_reports: number;
  unique_issue_clusters: number;
  duplicate_similar_reports: number;
  top_issue: string | null;
  top_issue_percentage: number;
  potentially_auto_resolvable: number;
  human_escalations: number;
  ai_resolution_rate: number;
  average_confidence: number;
  average_completeness: number;
  open_count: number;
  closed_count: number;
  high_priority_count: number;
  resolution_count: number;
  category_distribution: Record<string, number>;
  component_distribution: Record<string, number>;
  most_discussed: Array<{ issue_id: string; title: string; comments: number }>;
  clusters_with_resolutions: number;
  trend_by_month: Record<string, number>;
  dataset_name: string;
}

export interface IssueResolution {
  query: string;
  answer: string;
  steps: string[];
  confidence: 'High' | 'Medium' | 'Low';
  resolution_available: boolean;
  escalation_recommended: boolean;
  matches: Array<{ issue_id: string; title: string; similarity: number; source_url: string }>;
  evidence: Array<{ issue_id: string; title: string; resolution_summary: string; steps: string[]; source_url: string }>;
}

export interface IntelligenceStatus {
  ready: boolean;
  building: boolean;
  dataset_name: string;
  dataset_split?: string;
  record_count: number;
  error?: string;
}
