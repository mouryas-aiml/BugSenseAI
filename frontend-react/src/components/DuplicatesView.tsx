import React, { useState } from 'react';
import { 
  Copy, 
  Search, 
  RefreshCw, 
  ArrowRight, 
  CheckCircle, 
  AlertTriangle,
  GitCompare
} from 'lucide-react';
import { apiService } from '../services/api';
import { SimilarBugMatch } from '../types';

export const DuplicatesView: React.FC = () => {
  const [queryText, setQueryText] = useState('Payment checkout fails with 500 null pointer exception');
  const [component, setComponent] = useState('Payment Gateway');
  const [matches, setMatches] = useState<SimilarBugMatch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!queryText.trim()) return;
    setIsLoading(true);

    try {
      const resp = await apiService.queryDuplicates({
        title: queryText,
        actual_behavior: queryText,
        component: component,
      }, 5);
      setMatches(resp.matches || []);
    } catch (err: unknown) {
      console.error('Duplicate search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const res = await apiService.syncVectorStore();
      setSyncMessage(`Vector index successfully synchronized. Total entries: ${res.total}`);
    } catch (err: unknown) {
      setSyncMessage('Failed to sync vector store.');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="page-container">
      <div className="hero-banner">
        <div className="hero-tag">Dense Semantic Vector Search</div>
        <h1 className="hero-title">Duplicate & Similar Incident Detection</h1>
        <p className="hero-desc">
          Identify duplicate defect submissions across legacy repositories using sentence-transformers (all-MiniLM-L6-v2) cosine similarity.
        </p>
      </div>

      {/* Query Bar */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f3f4f6' }}>Search Defect Semantic Space</h3>
          <button 
            onClick={handleSync}
            disabled={syncing}
            className="btn btn-secondary"
            style={{ fontSize: '0.78rem', padding: '6px 12px' }}
          >
            <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
            <span>{syncing ? 'Syncing Index...' : 'Re-index Historical Vectors'}</span>
          </button>
        </div>

        {syncMessage && (
          <div className="alert-box alert-success" style={{ marginBottom: '16px' }}>
            <CheckCircle size={18} />
            <div>{syncMessage}</div>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr auto', gap: '12px', alignItems: 'flex-end' }}>
          <div>
            <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>
              Bug Description or Error Log
            </label>
            <input 
              type="text" 
              className="form-input"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder="e.g. infinite spinner on cart checkout"
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>
              Suspected Component
            </label>
            <input 
              type="text" 
              className="form-input"
              value={component}
              onChange={(e) => setComponent(e.target.value)}
              placeholder="e.g. Payment Gateway"
            />
          </div>

          <button onClick={handleSearch} disabled={isLoading} className="btn btn-primary" style={{ height: '42px' }}>
            <Search size={16} />
            <span>{isLoading ? 'Computing Distances...' : 'Search Duplicates'}</span>
          </button>
        </div>
      </div>

      {/* Results */}
      {matches.length > 0 ? (
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f3f4f6', marginBottom: '16px' }}>
            Ranked Semantic Matches ({matches.length})
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {matches.map((m, idx) => {
              const isHigh = m.similarity >= 65;
              const simColor = isHigh ? '#ef4444' : (m.similarity >= 45 ? '#f59e0b' : '#3b82f6');

              return (
                <div key={idx} className="card" style={{ borderLeft: `4px solid ${simColor}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#818cf8', background: 'rgba(99, 102, 241, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                          #{idx + 1} MATCH
                        </span>
                        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                          ID: {m.id || m.jira_key || 'HIST-BUG'}
                        </span>
                        {isHigh && (
                          <span className="badge badge-p1">
                            HIGH DUPLICATE PROBABILITY
                          </span>
                        )}
                      </div>
                      <h4 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', marginBottom: '6px' }}>
                        {m.title}
                      </h4>
                      <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                        {m.explanation || 'Significant semantic overlap in defect symptoms and component.'}
                      </p>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: simColor }}>
                        {m.similarity}%
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase' }}>
                        Cosine Overlap
                      </div>
                    </div>
                  </div>

                  {/* Side-by-Side Comparison Box */}
                  <div style={{ marginTop: '16px', background: '#0a0e17', borderRadius: '8px', padding: '14px', border: '1px solid #1c263c' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', color: '#818cf8', fontWeight: 700, marginBottom: '8px' }}>
                      <GitCompare size={14} />
                      <span>COMPARATIVE SYMPTOM DIFF</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div>
                        <div style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '4px' }}>Target Query</div>
                        <div style={{ fontSize: '0.85rem', color: '#f3f4f6' }}>{queryText}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '4px' }}>Historical Defect Signature</div>
                        <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{m.actual_behavior || m.summary || m.title}</div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
          Enter a bug description above to compute cosine distances against the historical defect vector space.
        </div>
      )}
    </div>
  );
};
