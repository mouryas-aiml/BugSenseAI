import React from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  Copy, 
  Sparkles, 
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import { AnalyticsData, HealthStatus } from '../types';

interface DashboardViewProps {
  analytics: AnalyticsData | null;
  health: HealthStatus | null;
  onNavigateToAnalyze: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ analytics, onNavigateToAnalyze }) => {
  const total = analytics?.total_reports || 0;
  const sevDist = analytics?.severity_distribution || {};
  const p1 = sevDist['P1'] || 0;
  const p2 = sevDist['P2'] || 0;
  const p3 = sevDist['P3'] || 0;
  const p4 = sevDist['P4'] || 0;
  const reviewRequired = analytics?.requires_human_review_count || 0;
  const duplicates = analytics?.duplicate_count || 0;
  const avgCompleteness = analytics?.avg_completeness_score || 0;

  const confDist = analytics?.confidence_distribution || {};
  const highConf = confDist['High'] || 0;
  const medConf = confDist['Medium'] || 0;
  const lowConf = confDist['Low'] || 0;

  return (
    <div className="page-container">
      {/* Hero Banner */}
      <div className="hero-banner">
        <div className="hero-tag">TCS AI Enterprise Platform</div>
        <h1 className="hero-title">Software Defect Intelligence & Automated Triage</h1>
        <p className="hero-desc">
          Automated multi-dimensional incident analysis powered by Google Gemini, vector similarity search, and deterministic quality validation.
        </p>
        <div style={{ marginTop: '20px', display: 'flex', gap: '12px' }}>
          <button onClick={onNavigateToAnalyze} className="btn btn-primary">
            <Sparkles size={16} />
            <span>Triage New Bug Report</span>
            <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-4">
        <div className="card">
          <div className="stat-label">Total Bugs Triaged</div>
          <div className="stat-value">{total}</div>
          <div className="stat-sub">Across all repositories</div>
        </div>

        <div className="card">
          <div className="stat-label">Critical & High (P1 / P2)</div>
          <div className="stat-value" style={{ color: '#f87171' }}>{p1 + p2}</div>
          <div className="stat-sub">P1: {p1} · P2: {p2} incidents</div>
        </div>

        <div className="card">
          <div className="stat-label">Human Review Queue</div>
          <div className="stat-value" style={{ color: '#fbbf24' }}>{reviewRequired}</div>
          <div className="stat-sub">Ambiguous or high-impact bugs</div>
        </div>

        <div className="card">
          <div className="stat-label">Duplicate Filings Caught</div>
          <div className="stat-value" style={{ color: '#06b6d4' }}>{duplicates}</div>
          <div className="stat-sub">Vector semantic matches</div>
        </div>
      </div>

      <div className="grid-4">
        <div className="card">
          <div className="stat-label">Standard & Low (P3 / P4)</div>
          <div className="stat-value" style={{ color: '#60a5fa' }}>{p3 + p4}</div>
          <div className="stat-sub">P3: {p3} · P4: {p4} defects</div>
        </div>

        <div className="card">
          <div className="stat-label">Avg Completeness Score</div>
          <div className="stat-value" style={{ color: avgCompleteness >= 70 ? '#34d399' : '#fbbf24' }}>
            {avgCompleteness}%
          </div>
          <div className="stat-sub">Deterministic quality heuristic</div>
        </div>

        <div className="card">
          <div className="stat-label">Confidence Distribution</div>
          <div className="stat-value" style={{ fontSize: '1.25rem', paddingTop: '6px' }}>
            <span style={{ color: '#34d399' }}>H:{highConf}</span> · <span style={{ color: '#fbbf24' }}>M:{medConf}</span> · <span style={{ color: '#f87171' }}>L:{lowConf}</span>
          </div>
          <div className="stat-sub">Model certainty tiers</div>
        </div>

        <div className="card">
          <div className="stat-label">Automation Efficiency</div>
          <div className="stat-value" style={{ color: '#a78bfa' }}>
            {total ? Math.round(((total - reviewRequired) / total) * 100) : 0}%
          </div>
          <div className="stat-sub">Zero-touch triage rate</div>
        </div>
      </div>

      {/* Visual Analytics Row */}
      <div className="grid-2">
        {/* Severity Distribution */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#f3f4f6' }}>Severity Tier Breakdown</h3>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Deterministic P1-P4 Rubric</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {[
              { label: 'P1 · Critical (System Down / Revenue Impact)', count: p1, color: '#ef4444', pct: total ? Math.round((p1 / total) * 100) : 0 },
              { label: 'P2 · High (Major Functionality Broken)', count: p2, color: '#f59e0b', pct: total ? Math.round((p2 / total) * 100) : 0 },
              { label: 'P3 · Medium (Standard Defect / Workaround Exists)', count: p3, color: '#3b82f6', pct: total ? Math.round((p3 / total) * 100) : 0 },
              { label: 'P4 · Low (Cosmetic / Minor Friction)', count: p4, color: '#10b981', pct: total ? Math.round((p4 / total) * 100) : 0 },
            ].map((tier, idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
                  <span style={{ color: '#cbd5e1' }}>{tier.label}</span>
                  <span style={{ fontWeight: 700, color: tier.color }}>{tier.count} ({tier.pct}%)</span>
                </div>
                <div style={{ height: '8px', background: '#0a0e17', borderRadius: '4px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${tier.pct}%`, 
                      height: '100%', 
                      background: tier.color, 
                      borderRadius: '4px',
                      transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)' 
                    }} 
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Affected Components */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#f3f4f6' }}>Component Defect Concentration</h3>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Top Impacted Subsystems</span>
          </div>

          {analytics?.component_distribution && Object.keys(analytics.component_distribution).length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {Object.entries(analytics.component_distribution).slice(0, 5).map(([comp, count], i) => {
                const pct = total ? Math.round((count / total) * 100) : 0;
                return (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: '#0d121f', borderRadius: '8px', border: '1px solid #1c263c' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ width: '22px', height: '22px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700 }}>
                        {i + 1}
                      </span>
                      <span style={{ fontSize: '0.88rem', fontWeight: 600, color: '#f3f4f6' }}>{comp}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{count} issues</span>
                      <span className="badge badge-p3">{pct}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>
              No component defect records available yet.
            </div>
          )}
        </div>
      </div>

      {/* Recent Triage Activity */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>Recent Incident Triage Feed</h3>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Latest automated extractions processed across engineering repositories</p>
          </div>
          <TrendingUp size={18} style={{ color: '#818cf8' }} />
        </div>

        {analytics?.recent_reports && analytics.recent_reports.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Incident Title</th>
                  <th>Severity</th>
                  <th>Component</th>
                  <th>Assigned Team</th>
                  <th>Confidence</th>
                  <th>Completeness</th>
                </tr>
              </thead>
              <tbody>
                {analytics.recent_reports.map((r, i) => {
                  const s = (r.severity || 'P3').toUpperCase().replace('SEVERITY.', '');
                  return (
                    <tr key={i}>
                      <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{r.timestamp || 'Just now'}</td>
                      <td style={{ fontWeight: 600, color: '#f3f4f6', maxWidth: '340px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {r.title}
                      </td>
                      <td>
                        <span className={`badge badge-${s.toLowerCase()}`}>
                          {s}
                        </span>
                      </td>
                      <td style={{ color: '#cbd5e1' }}>{r.component || 'General'}</td>
                      <td style={{ color: '#94a3b8' }}>{r.team || 'Triage Team'}</td>
                      <td>
                        <span style={{ 
                          color: r.confidence === 'High' ? '#34d399' : (r.confidence === 'Medium' ? '#fbbf24' : '#f87171'),
                          fontWeight: 600,
                          fontSize: '0.8rem'
                        }}>
                          {r.confidence}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontWeight: 700, color: r.completeness_score >= 70 ? '#34d399' : '#fbbf24' }}>
                          {r.completeness_score}%
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
            No triage history recorded yet. Use the 'Analyze Bug Report' tab to triage your first incident.
          </div>
        )}
      </div>
    </div>
  );
};
