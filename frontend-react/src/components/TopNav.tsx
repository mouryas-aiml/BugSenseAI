import React from 'react';
import { Terminal, RefreshCw, Cpu, Database } from 'lucide-react';
import { HealthStatus } from '../types';

interface TopNavProps {
  health: HealthStatus | null;
  onRefresh: () => void;
  isLoading: boolean;
}

export const TopNav: React.FC<TopNavProps> = ({ health, onRefresh, isLoading }) => {
  return (
    <header className="top-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
          <Cpu size={15} style={{ color: '#818cf8' }} />
          <span>LLM Engine: <strong style={{ color: '#f3f4f6' }}>Google Gemini</strong></span>
        </div>
        <span style={{ color: '#334155' }}>|</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
          <Database size={15} style={{ color: '#06b6d4' }} />
          <span>Vector Index: <strong style={{ color: '#f3f4f6' }}>{health?.vector_store_entries || 0} Fingerprints</strong></span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button 
          onClick={onRefresh}
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.78rem' }}
          disabled={isLoading}
        >
          <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
          <span>{isLoading ? 'Syncing...' : 'Sync Engine'}</span>
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#121829', padding: '6px 12px', borderRadius: '6px', border: '1px solid #1c263c', fontSize: '0.75rem', color: '#64748b' }}>
          <Terminal size={14} />
          <span>Port 8000</span>
        </div>
      </div>
    </header>
  );
};
