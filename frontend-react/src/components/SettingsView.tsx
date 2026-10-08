import React, { useState } from 'react';
import { 
  Settings, 
  ShieldCheck, 
  Sliders, 
  Cpu, 
  Lock, 
  Save, 
  Check 
} from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [provider, setProvider] = useState('gemini');
  const [model, setModel] = useState('gemini-flash-lite-latest');
  const [timeout, setTimeoutVal] = useState(60);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.68);
  const [completenessThreshold, setCompletenessThreshold] = useState(40);
  const [maskEmails, setMaskEmails] = useState(true);
  const [maskIPs, setMaskIPs] = useState(true);
  const [maskTokens, setMaskTokens] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="page-container">
      <div className="hero-banner">
        <div className="hero-tag">Platform Configuration</div>
        <h1 className="hero-title">Platform Settings & Model Governance</h1>
        <p className="hero-desc">
          Manage AI orchestration parameters, confidence thresholds, and enterprise privacy rules with strict secret protection.
        </p>
      </div>

      <div className="grid-2">
        {/* Model Orchestration */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Cpu size={18} style={{ color: '#818cf8' }} />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f3f4f6', margin: 0 }}>AI Model Orchestration</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>AI Provider</label>
              <select className="form-select" value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="gemini">Google Gemini (Recommended, Official SDK)</option>
                <option value="openai">OpenAI GPT-4o-mini</option>
                <option value="groq">Groq Llama-3.3-70b</option>
                <option value="ollama">Local Ollama</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Gemini Model Selection</label>
              <select className="form-select" value={model} onChange={(e) => setModel(e.target.value)}>
                <option value="gemini-flash-lite-latest">gemini-flash-lite-latest (Fastest, High Availability)</option>
                <option value="gemini-flash-latest">gemini-flash-latest</option>
                <option value="gemini-3.8-flash">gemini-3.8-flash</option>
              </select>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                <span style={{ color: '#94a3b8' }}>Pipeline Timeout:</span>
                <span style={{ color: '#f3f4f6', fontWeight: 600 }}>{timeout}s</span>
              </div>
              <input 
                type="range" 
                min={15} 
                max={120} 
                step={5} 
                value={timeout} 
                onChange={(e) => setTimeoutVal(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>
          </div>
        </div>

        {/* Threshold Governance */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Sliders size={18} style={{ color: '#06b6d4' }} />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f3f4f6', margin: 0 }}>Quality & Duplicate Thresholds</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                <span style={{ color: '#94a3b8' }}>Duplicate Cosine Similarity Threshold:</span>
                <span style={{ color: '#06b6d4', fontWeight: 700 }}>{Math.round(similarityThreshold * 100)}%</span>
              </div>
              <input 
                type="range" 
                min={0.50} 
                max={0.90} 
                step={0.02} 
                value={similarityThreshold} 
                onChange={(e) => setSimilarityThreshold(Number(e.target.value))}
                style={{ width: '100%' }}
              />
              <p style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '4px' }}>
                Matches exceeding this cosine similarity are flagged for deduplication.
              </p>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                <span style={{ color: '#94a3b8' }}>Human Review Completeness Trigger:</span>
                <span style={{ color: '#fbbf24', fontWeight: 700 }}>{completenessThreshold}%</span>
              </div>
              <input 
                type="range" 
                min={20} 
                max={60} 
                step={5} 
                value={completenessThreshold} 
                onChange={(e) => setCompletenessThreshold(Number(e.target.value))}
                style={{ width: '100%' }}
              />
              <p style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '4px' }}>
                Reports scoring below this quality score mandate human verification.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Privacy and Secrets Row */}
      <div className="grid-2" style={{ marginTop: '24px' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <ShieldCheck size={18} style={{ color: '#10b981' }} />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f3f4f6', margin: 0 }}>Data Privacy & Anonymization</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input type="checkbox" checked={maskEmails} onChange={(e) => setMaskEmails(e.target.checked)} />
              <span>Mask Customer Email Addresses ([EMAIL_REDACTED])</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input type="checkbox" checked={maskIPs} onChange={(e) => setMaskIPs(e.target.checked)} />
              <span>Mask IPv4 / IPv6 Addresses ([IP_REDACTED])</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input type="checkbox" checked={maskTokens} onChange={(e) => setMaskTokens(e.target.checked)} />
              <span>Mask Auth Bearer & Secret Tokens ([TOKEN_REDACTED])</span>
            </label>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Lock size={18} style={{ color: '#f59e0b' }} />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f3f4f6', margin: 0 }}>Secret Governance & Protection</h3>
          </div>

          <div className="alert-box alert-success" style={{ marginBottom: '16px' }}>
            <ShieldCheck size={18} />
            <div>
              <strong>Strict Non-Exposure Policy:</strong> Credentials and API tokens are never rendered in plain text or shared in export dossiers.
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>GEMINI_API_KEY (Masked for Security)</label>
            <input 
              type="text" 
              className="form-input" 
              value="•••••••••••••••••••••••••••••••••••••••• (Configured via .env)" 
              disabled 
              style={{ background: '#0a0e17', color: '#64748b' }}
            />
          </div>
        </div>
      </div>

      <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end' }}>
        <button onClick={handleSave} className="btn btn-primary">
          {saved ? <Check size={16} /> : <Save size={16} />}
          <span>{saved ? 'Preferences Saved!' : 'Save Platform Preferences'}</span>
        </button>
      </div>
    </div>
  );
};
