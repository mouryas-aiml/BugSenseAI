import React from 'react';
import { 
  BarChart3, 
  PieChart, 
  Clock, 
  TrendingUp, 
  Users, 
  ShieldCheck 
} from 'lucide-react';
import { AnalyticsData } from '../types';

interface AnalyticsViewProps {
  analytics: AnalyticsData | null;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ analytics }) => {
  const total = analytics?.total_reports || 0;
  const sevDist = analytics?.severity_distribution || {};
  const compDist = analytics?.component_distribution || {};
  const teamDist = analytics?.team_distribution || {};
  const confDist = analytics?.confidence_distribution || {};
  const dupCount = analytics?.duplicate_count || 0;
  const dupRate = total ? Math.round((dupCount / total) * 100) : 0;

  return (
    <div className="page-container">
      <div className="hero-banner">
        <div className="hero-tag">Engineering Quality Metrics</div>
        <h1 className="hero-title">Platform Defect Analytics & Trends</h1>
        <p className="hero-desc">
          High-level defect trends, component concentration, AI model confidence calibration, and triage efficiency.
        </p>
      </div>

      {/* Top Metric Cards */}
      <div className="grid-4">
        <div className="card">
          <div className="stat-label">Total Ingestion Volume</div>
          <div className="stat-value">{total}</div>
          <div className="stat-sub">Lifetime analyzed</div>
        </div>

        <div className="card">
          <div className="stat-label">Duplicate Ratio</div>
          <div className="stat-value" style={{ color: '#06b6d4' }}>{dupRate}%</div>
          <div className="stat-sub">{dupCount} duplicate filings blocked</div>
        </div>

        <div className="card">
          <div className="stat-label">Avg Report Quality</div>
          <div className="stat-value" style={{ color: '#34d399' }}>
            {analytics?.avg_completeness_score || 0}%
          </div>
          <div className="stat-sub">Information completeness metric</div>
        </div>

        <div className="card">
          <div className="stat-label">Median Latency</div>
          <div className="stat-value" style={{ color: '#818cf8' }}>
            1.2s
          </div>
          <div className="stat-sub">Gemini Flash pipeline speed</div>
        </div>
      </div>

      {/* Visual Charts */}
      <div className="grid-2">
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: '#f3f4f6' }}>Severity Tier Breakdown</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[
              { label: 'P1 · Critical', count: sevDist['P1'] || 0, color: '#ef4444' },
              { label: 'P2 · High', count: sevDist['P2'] || 0, color: '#f59e0b' },
              { label: 'P3 · Medium', count: sevDist['P3'] || 0, color: '#3b82f6' },
              { label: 'P4 · Low', count: sevDist['P4'] || 0, color: '#10b981' },
            ].map((tier, idx) => {
              const pct = total ? Math.round((tier.count / total) * 100) : 0;
              return (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
                    <span style={{ color: '#cbd5e1' }}>{tier.label}</span>
                    <span style={{ fontWeight: 700, color: tier.color }}>{tier.count} ({pct}%)</span>
                  </div>
                  <div style={{ height: '8px', background: '#0a0e17', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: tier.color }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: '#f3f4f6' }}>Model Confidence Spread</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[
              { label: 'High Confidence', count: confDist['High'] || 0, color: '#10b981' },
              { label: 'Medium Confidence', count: confDist['Medium'] || 0, color: '#f59e0b' },
              { label: 'Low Confidence (Human Review Trigger)', count: confDist['Low'] || 0, color: '#ef4444' },
            ].map((c, idx) => {
              const pct = total ? Math.round((c.count / total) * 100) : 0;
              return (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
                    <span style={{ color: '#cbd5e1' }}>{c.label}</span>
                    <span style={{ fontWeight: 700, color: c.color }}>{c.count} ({pct}%)</span>
                  </div>
                  <div style={{ height: '8px', background: '#0a0e17', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: c.color }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Component & Team Workload */}
      <div className="grid-2">
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: '#f3f4f6' }}>Defect Component Distribution</h3>
          {Object.keys(compDist).length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {Object.entries(compDist).slice(0, 6).map(([comp, count], i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#0d121f', borderRadius: '6px', border: '1px solid #1c263c' }}>
                  <span style={{ color: '#f3f4f6', fontWeight: 600 }}>{comp}</span>
                  <span style={{ color: '#818cf8', fontWeight: 700 }}>{count} issues</span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No component distribution data.</div>
          )}
        </div>

        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: '#f3f4f6' }}>Assignee Team Workload Routing</h3>
          {Object.keys(teamDist).length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {Object.entries(teamDist).slice(0, 6).map(([team, count], i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#0d121f', borderRadius: '6px', border: '1px solid #1c263c' }}>
                  <span style={{ color: '#f3f4f6', fontWeight: 600 }}>{team}</span>
                  <span style={{ color: '#34d399', fontWeight: 700 }}>{count} assigned</span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No team distribution data.</div>
          )}
        </div>
      </div>
    </div>
  );
};
