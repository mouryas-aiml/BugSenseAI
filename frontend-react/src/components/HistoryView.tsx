import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  Filter, 
  Download, 
  ChevronDown, 
  ChevronUp, 
  FileText,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import { apiService } from '../services/api';
import { TriageOutput } from '../types';

export const HistoryView: React.FC = () => {
  const [items, setItems] = useState<TriageOutput[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const res = await apiService.getHistory(100, 0);
      setItems(res.items || []);
    } catch (err: unknown) {
      console.error('History load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredItems = items.filter(item => {
    if (severityFilter !== 'ALL' && item.severity !== severityFilter) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const corpus = `${item.title} ${item.summary} ${item.component} ${(item.error_messages || []).join(' ')}`.toLowerCase();
      if (!corpus.includes(q)) return false;
    }
    return true;
  });

  return (
    <div className="page-container">
      <div className="hero-banner">
        <div className="hero-tag">Incident Audit Trail</div>
        <h1 className="hero-title">Bug Intelligence History Dossiers</h1>
        <p className="hero-desc">
          Search, audit, and inspect structured engineering triage reports preserved in the platform archive.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1.2fr auto', gap: '16px', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '13px', color: '#64748b' }} />
            <input 
              type="text" 
              className="form-input"
              style={{ paddingLeft: '38px' }}
              placeholder="Search reports by title, component, stack trace keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '6px' }}>
            {(['ALL', 'P1', 'P2', 'P3', 'P4'] as const).map(sev => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`btn ${severityFilter === sev ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '6px 12px', fontSize: '0.78rem' }}
              >
                {sev}
              </button>
            ))}
          </div>

          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
            {filteredItems.length} records found
          </span>
        </div>
      </div>

      {/* Item List */}
      {isLoading ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
          Loading incident archives...
        </div>
      ) : filteredItems.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filteredItems.map((item, idx) => {
            const isExpanded = expandedIndex === idx;
            const s = (item.severity || 'P3').toUpperCase().replace('SEVERITY.', '');

            return (
              <div key={idx} className="card" style={{ padding: '16px 20px' }}>
                <div 
                  onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span className={`badge badge-${s.toLowerCase()}`}>{s}</span>
                    <span style={{ fontWeight: 700, color: '#f3f4f6', fontSize: '0.98rem' }}>
                      {item.title}
                    </span>
                    <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
                      · {item.component || 'General'}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                      Quality: <strong style={{ color: item.completeness_score >= 70 ? '#34d399' : '#fbbf24' }}>{item.completeness_score}%</strong>
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      {item._timestamp || 'Archived'}
                    </span>
                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </div>
                </div>

                {/* Expandable Details */}
                {isExpanded && (
                  <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #1c263c' }}>
                    <div style={{ marginBottom: '14px' }}>
                      <span className="tag-provenance tag-inference">SUMMARY</span>
                      <span style={{ fontSize: '0.9rem', color: '#e2e8f0', lineHeight: '1.5' }}>
                        {item.summary}
                      </span>
                    </div>

                    <div className="grid-2">
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '4px' }}>Impact & Scope</div>
                        <p style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{item.impact || 'Not specified'}</p>
                        
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', marginTop: '10px', marginBottom: '4px' }}>Root Cause Hypothesis</div>
                        <p style={{ fontSize: '0.85rem', color: '#cbd5e1', fontStyle: 'italic' }}>"{item.root_cause_hypothesis || 'None'}"</p>
                      </div>

                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '4px' }}>Reproduction Procedure</div>
                        {item.reproduction_steps && item.reproduction_steps.length > 0 ? (
                          <ol style={{ paddingLeft: '18px', fontSize: '0.82rem', color: '#cbd5e1' }}>
                            {item.reproduction_steps.map((step, i) => (
                              <li key={i}>{step}</li>
                            ))}
                          </ol>
                        ) : (
                          <span style={{ fontSize: '0.82rem', color: '#64748b' }}>None provided</span>
                        )}
                      </div>
                    </div>

                    <div style={{ marginTop: '14px', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                      <button 
                        onClick={() => {
                          const blob = new Blob([JSON.stringify(item, null, 2)], { type: 'application/json' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `triage_dossier_${s}_${Date.now()}.json`;
                          a.click();
                        }}
                        className="btn btn-secondary" 
                        style={{ fontSize: '0.75rem', padding: '6px 10px' }}
                      >
                        <Download size={14} />
                        <span>Download JSON Dossier</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
          No records matched your search filters.
        </div>
      )}
    </div>
  );
};
