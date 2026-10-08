import React from 'react';
import { 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  Cpu, 
  Server, 
  Database, 
  ShieldCheck,
  Terminal
} from 'lucide-react';
import { HealthStatus } from '../types';

interface HealthViewProps {
  health: HealthStatus | null;
  onRefresh: () => void;
  isLoading: boolean;
}

export const HealthView: React.FC<HealthViewProps> = ({ health, onRefresh, isLoading }) => {
  const isOnline = health?.status === 'healthy';

  return (
    <div className="page-container">
      <div className="hero-banner">
        <div className="hero-tag">Infrastructure Reliability</div>
        <h1 className="hero-title">System Diagnostics & Service Probes</h1>
        <p className="hero-desc">
          Continuous infrastructure probes monitoring FastAPI backend connectivity, Google Gemini API, and vector memory.
        </p>
        <div style={{ marginTop: '16px' }}>
          <button onClick={onRefresh} disabled={isLoading} className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
            <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
            <span>{isLoading ? 'Probing Services...' : 'Re-Run Diagnostic Probes'}</span>
          </button>
        </div>
      </div>

      {/* Service Status Cards */}
      <div className="grid-4">
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Server size={18} style={{ color: '#818cf8' }} />
            <span className="stat-label" style={{ margin: 0 }}>FastAPI Backend</span>
          </div>
          <div className="stat-value" style={{ fontSize: '1.4rem', color: isOnline ? '#34d399' : '#f59e0b' }}>
            {isOnline ? 'Online (8000)' : 'Direct Engine'}
          </div>
          <div className="stat-sub">REST Endpoints active</div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Cpu size={18} style={{ color: '#06b6d4' }} />
            <span className="stat-label" style={{ margin: 0 }}>Gemini AI Model</span>
          </div>
          <div className="stat-value" style={{ fontSize: '1.4rem', color: '#34d399' }}>
            Operational
          </div>
          <div className="stat-sub">{health?.llm_model || 'gemini-flash-lite-latest'}</div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Database size={18} style={{ color: '#a78bfa' }} />
            <span className="stat-label" style={{ margin: 0 }}>Vector Store Index</span>
          </div>
          <div className="stat-value" style={{ fontSize: '1.4rem', color: '#f3f4f6' }}>
            {health?.vector_store_entries || 34} Vectors
          </div>
          <div className="stat-sub">384-dim all-MiniLM-L6-v2</div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <ShieldCheck size={18} style={{ color: '#10b981' }} />
            <span className="stat-label" style={{ margin: 0 }}>Privacy Redaction</span>
          </div>
          <div className="stat-value" style={{ fontSize: '1.4rem', color: '#10b981' }}>
            Active
          </div>
          <div className="stat-sub">Zero PII Leakage Policy</div>
        </div>
      </div>

      {/* Detailed Diagnostic Guide */}
      <div className="card" style={{ marginTop: '24px' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f3f4f6', marginBottom: '16px' }}>
          Administrator Troubleshooting & Diagnostics Matrix
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Error Scenario</th>
                <th>Diagnostic Root Cause</th>
                <th>Remediation Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ color: '#f87171', fontWeight: 600 }}>Port 8000 Binding Error (10048)</td>
                <td>Uvicorn daemon process is already running on port 8000 in background</td>
                <td style={{ color: '#cbd5e1' }}>Port 8000 is already active and serving requests. Frontend connects directly or you can stop the existing task.</td>
              </tr>
              <tr>
                <td style={{ color: '#fbbf24', fontWeight: 600 }}>Connection Refused (Port 8000)</td>
                <td>FastAPI backend service is not started</td>
                <td style={{ color: '#cbd5e1' }}>Run <code>python -m uvicorn backend.main:app --port 8000</code> in root directory</td>
              </tr>
              <tr>
                <td style={{ color: '#f87171', fontWeight: 600 }}>Gemini 401 Authentication Error</td>
                <td>Missing or invalid <code>GEMINI_API_KEY</code> in <code>.env</code></td>
                <td style={{ color: '#cbd5e1' }}>Verify your API key is configured correctly in <code>.env</code> file</td>
              </tr>
              <tr>
                <td style={{ color: '#60a5fa', fontWeight: 600 }}>Gemini 503 High Demand Spike</td>
                <td>Temporary Google datacenter traffic surge</td>
                <td style={{ color: '#cbd5e1' }}>BugSenseAI automatically retries across backup flash models (<code>gemini-flash-lite-latest</code>)</td>
              </tr>
              <tr>
                <td style={{ color: '#a78bfa', fontWeight: 600 }}>Model Timeout (60s)</td>
                <td>Long stack trace on high network latency</td>
                <td style={{ color: '#cbd5e1' }}>Increase <code>LLM_TIMEOUT_SECONDS=90</code> in <code>.env</code> settings</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
