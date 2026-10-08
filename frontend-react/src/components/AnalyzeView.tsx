import React, { useState } from 'react';
import { 
  Sparkles, 
  ShieldAlert, 
  CheckCircle, 
  AlertTriangle, 
  Copy, 
  Download, 
  Share2, 
  Terminal, 
  Cpu, 
  Layers, 
  Eye, 
  RotateCcw,
  Check,
  FileCode,
  Send
} from 'lucide-react';
import { apiService } from '../services/api';
import { TriageOutput } from '../types';

const SAMPLE_PRESETS: Record<string, string> = {
  'Critical Checkout 500 (P1)': `When clicking 'Checkout' on the cart page (Chrome 122, macOS Sonoma), the page hangs with a spinning loader and never completes.
Browser console logs show:
Uncaught TypeError: Cannot read properties of undefined (reading 'paymentMethodId') at checkout.js:142
Network tab shows POST /api/v1/orders/checkout returned HTTP 500 Internal Server Error:
{"error": "NullPointerException: customer default payment method is null"}
Affecting roughly 15% of guest checkout attempts since v2.4.1 deployment yesterday.
Steps: 1. Add item to cart. 2. Proceed as guest. 3. Click Checkout.
Expected: Order confirmation page with order ID.
Actual: Infinite spinner, order not created, charge not processed.
Contact: john.smith@enterprise-corp.com, Server IP: 192.168.1.105`,

  'Enterprise Export Timeout (P2)': `Data export to CSV fails for accounts with more than 50,000 records on the Analytics page.
Error message: '504 Gateway Timeout: upstream request timed out after 30000ms'.
Affects all Tier-1 enterprise customers attempting monthly billing reconciliation.
Workaround: Exporting date ranges shorter than 7 days succeeds.
Browser: Any browser, Environment: Production US-East.`,

  'Vague User Report (Needs Review)': `the website feels very laggy today and something broke on my screen. please fix this asap its urgent!`,

  'UI Dark Mode Contrast Glitch (P4)': `On the user profile settings page in Dark Mode, the 'Save Changes' button text is dark gray (#333333) against a dark navy button background (#1a1a2e), making it unreadable.
Clicking the button still saves changes normally.
Reproducible on Firefox 123, Windows 11.`
};

export const AnalyzeView: React.FC = () => {
  const [bugText, setBugText] = useState('');
  const [environment, setEnvironment] = useState('Production');
  const [version, setVersion] = useState('');
  const [reporter, setReporter] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pipelineStage, setPipelineStage] = useState<string>('');
  const [result, setResult] = useState<TriageOutput | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [showJiraModal, setShowJiraModal] = useState(false);
  const [copiedJira, setCopiedJira] = useState(false);
  const [isApproved, setIsApproved] = useState(false);

  const handleSelectPreset = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    if (val && SAMPLE_PRESETS[val]) {
      setBugText(SAMPLE_PRESETS[val]);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!bugText.trim()) {
      setError('Please provide bug report text before initiating analysis.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setIsApproved(false);

    try {
      setPipelineStage('🔒 1. Scanning and scrubbing sensitive PII entities...');
      await new Promise(r => setTimeout(r, 200));

      setPipelineStage('🧠 2. Extracting structured intelligence via Google Gemini...');
      const metadata: Record<string, string> = {};
      if (environment) metadata.environment = environment;
      if (version) metadata.version = version;
      if (reporter) metadata.reporter = reporter;

      const triageResult = await apiService.triageBug(bugText, metadata);
      setPipelineStage('📐 3. Enforcing deterministic rules & semantic vector duplicate scan...');
      await new Promise(r => setTimeout(r, 150));

      setResult(triageResult);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred during triage analysis.');
      }
    } finally {
      setIsLoading(false);
      setPipelineStage('');
    }
  };

  const handleSeverityOverride = (newSev: 'P1' | 'P2' | 'P3' | 'P4') => {
    if (result) {
      setResult({ ...result, severity: newSev });
    }
  };

  const generateJiraMarkdown = () => {
    if (!result) return '';
    return `h1. ${result.title}

*Severity:* ${result.severity} | *Priority:* High | *Confidence:* ${result.confidence}
*Component:* ${result.component} | *Team:* ${result.suggested_assignee_team}

h2. Executive Summary
${result.summary}

h2. Operational Impact
${result.impact}
*Affected Scope:* ${result.affected_users}

h2. Steps to Reproduce
${result.reproduction_steps.map((s, i) => `# ${s}`).join('\n')}

h2. Expected vs Actual
*Expected:* ${result.expected_behavior}
*Actual:* ${result.actual_behavior}

h2. Technical Evidence
*Environment:* ${result.environment}
*Root Cause Hypothesis:* ${result.root_cause_hypothesis}
*Error Codes:* ${result.error_messages.join(', ') || 'None provided'}
`;
  };

  return (
    <div className="page-container">
      {/* Header Banner */}
      <div className="hero-banner">
        <div className="hero-tag">Real-Time Deep Analysis</div>
        <h1 className="hero-title">AI Bug Intelligence & Automated Triage</h1>
        <p className="hero-desc">
          Transform raw customer tickets, stack traces, and chat transcripts into verified, structured engineering intelligence.
        </p>
      </div>

      {/* Input Grid */}
      <div className="grid-3" style={{ gridTemplateColumns: '2.4fr 1fr' }}>
        {/* Left: Input Text Area */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f3f4f6', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Bug Report Payload
            </label>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Markdown, JSON, or Plain Text</span>
          </div>

          <textarea
            className="form-textarea"
            rows={10}
            placeholder="Paste raw customer defect, console error log, stack trace, or incident summary..."
            value={bugText}
            onChange={(e) => setBugText(e.target.value)}
            style={{ fontSize: '0.88rem', lineHeight: '1.5' }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={handleAnalyze} 
                className="btn btn-primary"
                disabled={isLoading}
              >
                <Sparkles size={16} />
                <span>{isLoading ? 'Reasoning with Gemini...' : 'Analyze with Gemini'}</span>
              </button>

              <button 
                onClick={() => { setBugText(''); setResult(null); setError(null); }} 
                className="btn btn-secondary"
                disabled={isLoading}
              >
                <RotateCcw size={15} />
                <span>Reset</span>
              </button>
            </div>

            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
              {bugText.length} characters
            </span>
          </div>

          {isLoading && (
            <div style={{ marginTop: '16px', padding: '12px 16px', background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: '8px', fontSize: '0.85rem', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Cpu size={18} className="animate-spin" />
              <span>{pipelineStage}</span>
            </div>
          )}

          {error && (
            <div className="alert-box alert-error" style={{ marginTop: '16px' }}>
              <AlertTriangle size={18} />
              <div>
                <strong>Triage Pipeline Error:</strong> {error}
              </div>
            </div>
          )}
        </div>

        {/* Right: Presets & Metadata */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="card">
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '12px', color: '#f3f4f6' }}>Realistic Test Presets</h3>
            <select className="form-select" onChange={handleSelectPreset} defaultValue="">
              <option value="" disabled>-- Select realistic scenario --</option>
              {Object.keys(SAMPLE_PRESETS).map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
            <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '8px' }}>
              Preloaded incident templates validating different severity tiers, PII scrubbing, and missing info flags.
            </p>
          </div>

          <div className="card">
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '12px', color: '#f3f4f6' }}>Optional Metadata</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Environment</label>
                <select className="form-select" value={environment} onChange={(e) => setEnvironment(e.target.value)}>
                  <option value="Production">Production</option>
                  <option value="Staging">Staging</option>
                  <option value="QA / Test">QA / Test</option>
                  <option value="Development">Development</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Software Release / Version</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. v2.4.1" 
                  value={version} 
                  onChange={(e) => setVersion(e.target.value)} 
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Reporting Source</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. Support Tier-2" 
                  value={reporter} 
                  onChange={(e) => setReporter(e.target.value)} 
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Structured AI Analysis Result Dossier */}
      {result && (
        <div style={{ marginTop: '36px' }}>
          {/* Header Card */}
          <div className="card" style={{ borderLeft: `5px solid ${result.severity === 'P1' ? '#ef4444' : (result.severity === 'P2' ? '#f59e0b' : '#3b82f6')}`, marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <span className={`badge badge-${result.severity.toLowerCase()}`}>
                    {result.severity} · {result.severity === 'P1' ? 'CRITICAL' : (result.severity === 'P2' ? 'HIGH' : (result.severity === 'P3' ? 'MEDIUM' : 'LOW'))}
                  </span>
                  <span style={{ 
                    fontSize: '0.75rem', 
                    fontWeight: 700, 
                    color: result.confidence === 'High' ? '#34d399' : (result.confidence === 'Medium' ? '#fbbf24' : '#f87171'),
                    background: 'rgba(18, 24, 41, 0.8)',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    border: '1px solid #1c263c'
                  }}>
                    {result.confidence} Confidence
                  </span>
                  {result.requires_human_review && (
                    <span style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: '1px solid rgba(239, 68, 68, 0.4)', padding: '3px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                      ⚠ Human Review Required
                    </span>
                  )}
                  {isApproved && (
                    <span style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)', padding: '3px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                      ✓ Verified by QA Maintainer
                    </span>
                  )}
                </div>
                <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#ffffff', marginBottom: '8px' }}>
                  {result.title}
                </h2>
                <div style={{ display: 'flex', gap: '18px', fontSize: '0.82rem', color: '#94a3b8', flexWrap: 'wrap' }}>
                  <span>Component: <strong style={{ color: '#f3f4f6' }}>{result.component || 'General'}</strong></span>
                  <span>Assignee: <strong style={{ color: '#f3f4f6' }}>{result.suggested_assignee_team || 'Triage Team'}</strong></span>
                  <span>Quality Score: <strong style={{ color: result.completeness_score >= 70 ? '#34d399' : '#fbbf24' }}>{result.completeness_score}%</strong></span>
                  <span>Bug Type: <strong style={{ color: '#f3f4f6' }}>{result.bug_type || 'Defect'}</strong></span>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <button 
                  onClick={() => setIsApproved(true)} 
                  className={`btn ${isApproved ? 'btn-success' : 'btn-secondary'}`}
                  style={{ fontSize: '0.8rem', padding: '8px 14px' }}
                >
                  <Check size={14} />
                  <span>{isApproved ? 'Approved' : 'Verify & Approve'}</span>
                </button>

                <button 
                  onClick={() => setShowJiraModal(true)} 
                  className="btn btn-secondary"
                  style={{ fontSize: '0.8rem', padding: '8px 14px' }}
                >
                  <Share2 size={14} />
                  <span>Jira Ticket</span>
                </button>

                <button 
                  onClick={() => setShowJsonModal(true)} 
                  className="btn btn-secondary"
                  style={{ fontSize: '0.8rem', padding: '8px 14px' }}
                >
                  <FileCode size={14} />
                  <span>Inspect JSON</span>
                </button>
              </div>
            </div>
          </div>

          {/* Privacy Anonymization Banner */}
          {result._pii_redacted && (
            <div className="alert-box alert-success">
              <ShieldAlert size={20} />
              <div>
                <strong>Client-Side Privacy Protection Active:</strong> Automatically masked{' '}
                <strong>{result._pii_redaction_types?.join(', ') || 'sensitive customer entities'}</strong> prior to sending data to the AI model. Zero confidential data was exposed.
              </div>
            </div>
          )}

          {/* Missing Information Banner */}
          {result.missing_information && result.missing_information.length > 0 && (
            <div className="alert-box alert-warning">
              <AlertTriangle size={20} />
              <div>
                <strong>Information Missing — Human Input Required:</strong>
                <p style={{ marginTop: '4px', fontSize: '0.85rem' }}>
                  The bug report lacks critical fields for deterministic resolution. Engineering maintainers should request:
                </p>
                <ul style={{ marginLeft: '20px', marginTop: '6px', fontSize: '0.85rem' }}>
                  {result.missing_information.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Duplicate Match Alert */}
          {result.is_duplicate && result.similar_bugs && result.similar_bugs.length > 0 && (
            <div className="alert-box alert-error">
              <Copy size={20} />
              <div>
                <strong>Potential Duplicate Incident Detected:</strong> Matches existing record{' '}
                <strong>"{result.similar_bugs[0].title}"</strong> with{' '}
                <strong>{result.similar_bugs[0].similarity}%</strong> semantic overlap. Review duplicate detection tab before dispatching new tickets.
              </div>
            </div>
          )}

          {/* Main 2-Column Dossier */}
          <div className="grid-2">
            {/* Left Column: Summary, Impact, Repro */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div className="card">
                <div style={{ marginBottom: '10px' }}>
                  <span className="tag-provenance tag-inference">AI SYNTHESIS</span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f3f4f6' }}>Executive Summary</span>
                </div>
                <p style={{ fontSize: '0.95rem', lineHeight: '1.6', color: '#e2e8f0', fontWeight: 500 }}>
                  {result.summary}
                </p>
              </div>

              <div className="card">
                <div style={{ marginBottom: '10px' }}>
                  <span className="tag-provenance tag-inference">BLAST RADIUS</span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f3f4f6' }}>Impact & Scope Analysis</span>
                </div>
                <div style={{ marginBottom: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Affected Users:</span>
                  <div style={{ fontSize: '0.9rem', color: '#f3f4f6', fontWeight: 600 }}>{result.affected_users || 'Unspecified'}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Operational Risk:</span>
                  <div style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>{result.impact || 'None provided'}</div>
                </div>
              </div>

              <div className="card">
                <div style={{ marginBottom: '10px' }}>
                  <span className="tag-provenance tag-fact">FACTS FROM REPORT</span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f3f4f6' }}>Expected vs Actual Behavior</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ background: '#0a0e17', padding: '12px 14px', borderRadius: '8px', border: '1px solid #1c263c' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#34d399', marginBottom: '6px' }}>EXPECTED BEHAVIOR</div>
                    <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{result.expected_behavior || 'Not stated'}</div>
                  </div>
                  <div style={{ background: '#0a0e17', padding: '12px 14px', borderRadius: '8px', border: '1px solid #1c263c' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f87171', marginBottom: '6px' }}>ACTUAL OBSERVED BEHAVIOR</div>
                    <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{result.actual_behavior || 'Not stated'}</div>
                  </div>
                </div>
              </div>

              <div className="card">
                <div style={{ marginBottom: '10px' }}>
                  <span className="tag-provenance tag-fact">REPRODUCTION</span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f3f4f6' }}>Step-by-Step Procedure</span>
                </div>
                {result.reproduction_steps && result.reproduction_steps.length > 0 ? (
                  <ol style={{ paddingLeft: '20px', fontSize: '0.88rem', color: '#e2e8f0', lineHeight: '1.7' }}>
                    {result.reproduction_steps.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ol>
                ) : (
                  <p style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.85rem' }}>
                    [Information Missing — Human Input Required: No reproduction steps provided in report]
                  </p>
                )}
              </div>
            </div>

            {/* Right Column: Hypothesis, Entities, Priority */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div className="card">
                <div style={{ marginBottom: '10px' }}>
                  <span className="tag-provenance tag-inference">AI HYPOTHESIS</span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f3f4f6' }}>Root Cause Hypothesis</span>
                </div>
                <div style={{ fontStyle: 'italic', fontSize: '0.9rem', color: '#cbd5e1', lineHeight: '1.5', background: '#0d121f', padding: '14px', borderRadius: '8px', border: '1px solid #1c263c' }}>
                  "{result.root_cause_hypothesis || 'Insufficient technical evidence to formulate a hypothesis.'}"
                </div>
                <p style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '8px' }}>
                  Disclaimer: Root cause hypotheses are AI inferences based on error signatures and require engineering verification before code changes.
                </p>
              </div>

              <div className="card">
                <div style={{ marginBottom: '10px' }}>
                  <span className="tag-provenance tag-fact">TECHNICAL EVIDENCE</span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f3f4f6' }}>Environment & Error Signatures</span>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Target Environment:</span>
                  <div style={{ fontSize: '0.88rem', color: '#f3f4f6', fontFamily: 'monospace' }}>{result.environment || 'Not provided'}</div>
                </div>

                {result.error_messages && result.error_messages.length > 0 && (
                  <div>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Captured Stack Trace / Error Codes:</span>
                    <div className="code-box">
                      {result.error_messages.map((err, i) => (
                        <div key={i}>{err}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="card">
                <div style={{ marginBottom: '10px' }}>
                  <span className="tag-provenance tag-rule">CLASSIFICATION</span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f3f4f6' }}>Entities, Labels & Test Areas</span>
                </div>

                {result.extracted_entities && result.extracted_entities.length > 0 && (
                  <div style={{ marginBottom: '12px' }}>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Extracted Entities:</span>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {result.extracted_entities.map((ent, i) => (
                        <span key={i} style={{ background: '#0a0e17', padding: '3px 8px', borderRadius: '4px', border: '1px solid #1c263c', fontSize: '0.75rem', fontFamily: 'monospace', color: '#93c5fd' }}>
                          {ent}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result.suggested_labels && result.suggested_labels.length > 0 && (
                  <div style={{ marginBottom: '12px' }}>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Suggested Jira Labels:</span>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {result.suggested_labels.map((lbl, i) => (
                        <span key={i} className="badge badge-p3">
                          {lbl}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result.related_test_areas && result.related_test_areas.length > 0 && (
                  <div>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Suggested Test Suites to Rerun:</span>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {result.related_test_areas.map((test, i) => (
                        <span key={i} style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '3px 8px', borderRadius: '4px', fontSize: '0.75rem' }}>
                          ✓ {test}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="card">
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f3f4f6', marginBottom: '12px' }}>Maintainer Severity Override</h4>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {(['P1', 'P2', 'P3', 'P4'] as const).map((sev) => (
                    <button
                      key={sev}
                      onClick={() => handleSeverityOverride(sev)}
                      className={`btn ${result.severity === sev ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ flex: 1, padding: '8px 0', fontSize: '0.8rem' }}
                    >
                      {sev}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Jira Ticket Modal */}
      {showJiraModal && result && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ maxWidth: '650px', width: '90%', maxHeight: '80vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff' }}>Formatted Jira Ticket</h3>
              <button onClick={() => setShowJiraModal(false)} className="btn btn-secondary" style={{ padding: '4px 8px' }}>✕</button>
            </div>
            <textarea
              className="form-textarea"
              style={{ flex: 1, fontFamily: 'monospace', fontSize: '0.8rem', minHeight: '300px' }}
              value={generateJiraMarkdown()}
              readOnly
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(generateJiraMarkdown());
                  setCopiedJira(true);
                  setTimeout(() => setCopiedJira(false), 2000);
                }} 
                className="btn btn-primary"
              >
                {copiedJira ? <Check size={16} /> : <Copy size={16} />}
                <span>{copiedJira ? 'Copied to Clipboard!' : 'Copy Jira Markdown'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Raw JSON Modal */}
      {showJsonModal && result && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ maxWidth: '700px', width: '90%', maxHeight: '80vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff' }}>Structured Output JSON Schema</h3>
              <button onClick={() => setShowJsonModal(false)} className="btn btn-secondary" style={{ padding: '4px 8px' }}>✕</button>
            </div>
            <textarea
              className="form-textarea"
              style={{ flex: 1, fontFamily: 'monospace', fontSize: '0.78rem', minHeight: '340px' }}
              value={JSON.stringify(result, null, 2)}
              readOnly
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
              <button 
                onClick={() => {
                  const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `triage_${result.severity}_${Date.now()}.json`;
                  a.click();
                }} 
                className="btn btn-primary"
              >
                <Download size={16} />
                <span>Download .JSON</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
