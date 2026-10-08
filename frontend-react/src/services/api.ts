/**
 * BugSenseAI — React API Service Layer
 * Connects frontend React components to FastAPI backend with robust fallback
 * and comprehensive error normalization.
 */

import { HealthStatus, TriageOutput, BatchTriageResponse, AnalyticsData, SimilarBugMatch } from '../types';

const API_BASE = 'http://localhost:8000';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });

    if (!response.ok) {
      let errorDetail = `HTTP Error ${response.status}: ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson && errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        // Use status text if body not json
      }
      throw new Error(errorDetail);
    }

    return await response.json() as T;
  } catch (err: unknown) {
    if (err instanceof Error) {
      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        throw new Error(`Cannot connect to FastAPI backend at ${API_BASE}. Ensure backend is running with: python -m uvicorn backend.main:app --port 8000`);
      }
      throw err;
    }
    throw new Error('Unknown network error occurred');
  }
}

export const apiService = {
  // Health & Diagnostics
  async getHealth(): Promise<HealthStatus> {
    return request<HealthStatus>('/health/detailed');
  },

  // Single Bug Triage
  async triageBug(bugText: string, metadata?: Record<string, string>): Promise<TriageOutput> {
    return request<TriageOutput>('/triage', {
      method: 'POST',
      body: JSON.stringify({
        bug: bugText,
        metadata: metadata || null,
      }),
    });
  },

  // Batch Triage
  async triageBatch(reports: string[], filename: string = ''): Promise<BatchTriageResponse> {
    return request<BatchTriageResponse>('/triage/batch', {
      method: 'POST',
      body: JSON.stringify({
        reports,
        source_filename: filename,
      }),
    });
  },

  // CI / JUnit XML Triage
  async triageCI(junitXml: string, createTickets: boolean = false): Promise<any> {
    return request<any>('/triage/ci', {
      method: 'POST',
      body: JSON.stringify({
        junit_xml: junitXml,
        branch: 'main',
        commit_sha: 'local',
        run_url: '',
        max_failures: 10,
        create_tickets: createTickets,
      }),
    });
  },

  // History
  async getHistory(limit: number = 50, offset: number = 0): Promise<{ total: number; offset: number; limit: number; items: TriageOutput[] }> {
    return request<{ total: number; offset: number; limit: number; items: TriageOutput[] }>(`/history?limit=${limit}&offset=${offset}`);
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsData> {
    return request<AnalyticsData>('/analytics');
  },

  // Duplicates Query
  async queryDuplicates(triagePayload: Partial<TriageOutput>, topK: number = 5): Promise<{ matches: SimilarBugMatch[] }> {
    return request<{ matches: SimilarBugMatch[] }>('/duplicates/query', {
      method: 'POST',
      body: JSON.stringify({
        ...triagePayload,
        top_k: topK,
      }),
    });
  },

  // Sync Vector Store
  async syncVectorStore(): Promise<{ added: number; total: number }> {
    return request<{ added: number; total: number }>('/duplicates/sync', {
      method: 'POST',
    });
  },
};
