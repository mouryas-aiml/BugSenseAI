import React from 'react';
import { 
  LayoutDashboard, 
  Sparkles, 
  Layers, 
  Copy, 
  History, 
  BarChart3, 
  Activity, 
  Settings, 
  ShieldCheck,
  BrainCircuit
} from 'lucide-react';
import { HealthStatus } from '../types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: HealthStatus | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, health }) => {
  const isOnline = health?.reachable !== false && health?.status === 'healthy';

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-badge">
          <ShieldCheck size={22} />
        </div>
        <div>
          <div className="brand-title">BugSense<span style={{ color: '#6366f1' }}>AI</span></div>
          <div className="brand-sub">TCS AI Triage Platform</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-title">Core Triage</div>
        <div 
          className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <LayoutDashboard size={18} />
          <span>Executive Dashboard</span>
        </div>
        <div 
          className={`nav-item ${activeTab === 'analyze' ? 'active' : ''}`}
          onClick={() => setActiveTab('analyze')}
        >
          <Sparkles size={18} />
          <span>Analyze Bug Report</span>
        </div>
        <div 
          className={`nav-item ${activeTab === 'batch' ? 'active' : ''}`}
          onClick={() => setActiveTab('batch')}
        >
          <Layers size={18} />
          <span>Batch Ingestion</span>
        </div>
        <div 
          className={`nav-item ${activeTab === 'duplicates' ? 'active' : ''}`}
          onClick={() => setActiveTab('duplicates')}
        >
          <Copy size={18} />
          <span>Duplicate Engine</span>
        </div>

        <div className="nav-section-title">Analytics & Audit</div>
        <div 
          className={`nav-item ${activeTab === 'intelligence' ? 'active' : ''}`}
          onClick={() => setActiveTab('intelligence')}
        >
          <BrainCircuit size={18} />
          <span>Issue Intelligence</span>
        </div>
        <div 
          className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <History size={18} />
          <span>Bug History Dossiers</span>
        </div>
        <div 
          className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <BarChart3 size={18} />
          <span>Engineering Analytics</span>
        </div>

        <div className="nav-section-title">Platform Governance</div>
        <div 
          className={`nav-item ${activeTab === 'health' ? 'active' : ''}`}
          onClick={() => setActiveTab('health')}
        >
          <Activity size={18} />
          <span>System Diagnostics</span>
        </div>
        <div 
          className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          <Settings size={18} />
          <span>Platform Settings</span>
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="status-pill">
          <div>
            <span className={`status-dot ${isOnline ? 'online' : 'degraded'}`}></span>
            <span style={{ fontWeight: 600, color: '#f3f4f6' }}>
              {isOnline ? 'System Operational' : 'Degraded Mode'}
            </span>
          </div>
          <span style={{ color: '#94a3b8', fontSize: '0.7rem' }}>
            {health?.llm_model || 'Gemini Flash'}
          </span>
        </div>
      </div>
    </aside>
  );
};
