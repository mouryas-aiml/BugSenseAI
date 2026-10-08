import React, { useState } from 'react';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Download, 
  Filter, 
  Layers, 
  RefreshCw 
} from 'lucide-react';
import { apiService } from '../services/api';
import { BatchTriageResponse, BatchTriageResultItem } from '../types';

export const BatchView: React.FC = () => {
  const [reports, setReports] = useState<string[]>([]);
  const [fileName, setFileName] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [batchResponse, setBatchResponse] = useState<BatchTriageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setError(null);
    const reader = new FileReader();

    reader.onload = (event) => {
      const content = event.target?.result as string;
      try {
        if (file.name.endsWith('.json')) {
          const parsed = JSON.parse(content);
          if (Array.isArray(parsed)) {
            const extracted = parsed.map(item => 
              typeof item === 'string' ? item : (item.bug || item.description || item.title || JSON.stringify(item))
            );
            setReports(extracted);
          } else if (parsed.reports && Array.isArray(parsed.reports)) {
            setReports(parsed.reports);
          }
        } else if (file.name.endsWith('.csv')) {
          const lines = content.split('\n').filter(l => l.trim().length > 0);
          if (lines.length > 1) {
            // Treat each non-header line as a report
            setReports(lines.slice(1, 21)); // cap at 20
          }
        } else {
          // .txt
          const delimiter = content.includes('---') ? '---' : '\n\n';
          const items = content.split(delimiter).map(s => s.trim()).filter(s => s.length > 0);
          setReports(items.slice(0, 20));
        }
      } catch (err: unknown) {
        setError('Failed to parse uploaded file. Please ensure valid CSV, JSON or TXT format.');
      }
    };

    reader.readAsText(file);
  };

  const handleRunBatch = async () => {
    if (reports.length === 0) return;
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.triageBatch(reports, fileName);
      setBatchResponse(response);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Batch processing failed.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!batchResponse) return;
    const headers = ['Index', 'Title', 'Severity', 'Component', 'Team', 'Confidence', 'Latency(ms)'];
    const rows = batchResponse.results.map(r => [
      r.index + 1,
      `"${r.triage?.title?.replace(/"/g, '""') || r.input_preview}"`,
      r.triage?.severity || 'ERROR',
      `"${r.triage?.component || 'N/A'}"`,
      `"${r.triage?.suggested_assignee_team || 'N/A'}"`,
      r.triage?.confidence || 'N/A',
      r.processing_time_ms
    ]);
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `batch_triage_${Date.now()}.csv`;
    a.click();
  };

  const filteredResults = batchResponse?.results.filter(r => {
    if (severityFilter === 'ALL') return true;
    return r.triage?.severity === severityFilter;
  }) || [];

  return (
    <div className="page-container">
      <div className="hero-banner">
        <div className="hero-tag">High-Throughput Ingestion</div>
        <h1 className="hero-title">Batch Bug Intelligence Processing</h1>
        <p className="hero-desc">
          Upload CSV defect exports, JSON ticket arrays, or plain text dumps to execute automated triage at scale.
        </p>
      </div>

      {/* Upload Box */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f3f4f6' }}>Upload Dataset</h3>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Supports .csv, .json, .txt (Max 20 per batch)</span>
        </div>

        <div style={{ border: '2px dashed #1c263c', borderRadius: '10px', padding: '36px', textAlign: 'center', background: '#0a0e17' }}>
          <Upload size={32} style={{ color: '#818cf8', marginBottom: '12px' }} />
          <p style={{ fontSize: '0.92rem', color: '#f3f4f6', fontWeight: 600, marginBottom: '6px' }}>
            Drag and drop defect dataset or click to browse
          </p>
          <p style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: '16px' }}>
            Automatic format detection for Jira CSV exports, Bugzilla JSON, and support tickets
          </p>
          <input 
            type="file" 
            accept=".csv,.json,.txt"
            onChange={handleFileUpload}
            style={{ display: 'inline-block', fontSize: '0.82rem', color: '#94a3b8' }}
          />
        </div>

        {reports.length > 0 && (
          <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.88rem', color: '#34d399', fontWeight: 600 }}>
              ✓ Loaded {reports.length} bug report candidates from {fileName}
            </span>
            <button 
              onClick={handleRunBatch}
              disabled={isLoading}
              className="btn btn-primary"
            >
              <Layers size={16} />
              <span>{isLoading ? 'Processing Batch...' : `Execute Batch Triage (${reports.length})`}</span>
            </button>
          </div>
        )}

        {error && (
          <div className="alert-box alert-error" style={{ marginTop: '16px' }}>
            <AlertCircle size={18} />
            <div>{error}</div>
          </div>
        )}
      </div>

      {/* Results Section */}
      {batchResponse && (
        <div style={{ marginTop: '30px' }}>
          {/* Summary KPIs */}
          <div className="grid-4">
            <div className="card">
              <div className="stat-label">Batch Volume</div>
              <div className="stat-value">{batchResponse.total}</div>
            </div>
            <div className="card">
              <div className="stat-label">Successfully Triaged</div>
              <div className="stat-value" style={{ color: '#34d399' }}>{batchResponse.succeeded}</div>
            </div>
            <div className="card">
              <div className="stat-label">Failed Reports</div>
              <div className="stat-value" style={{ color: '#f87171' }}>{batchResponse.failed}</div>
            </div>
            <div className="card">
              <div className="stat-label">Success Rate</div>
              <div className="stat-value" style={{ color: '#60a5fa' }}>
                {batchResponse.total ? Math.round((batchResponse.succeeded / batchResponse.total) * 100) : 0}%
              </div>
            </div>
          </div>

          {/* Table Container */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Filter size={16} style={{ color: '#818cf8' }} />
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f3f4f6' }}>Filter Severity:</span>
                {(['ALL', 'P1', 'P2', 'P3', 'P4'] as const).map(sev => (
                  <button
                    key={sev}
                    onClick={() => setSeverityFilter(sev)}
                    className={`btn ${severityFilter === sev ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                  >
                    {sev}
                  </button>
                ))}
              </div>

              <button onClick={downloadCSV} className="btn btn-secondary" style={{ fontSize: '0.8rem' }}>
                <Download size={14} />
                <span>Export Results CSV</span>
              </button>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Extracted Title</th>
                    <th>Severity</th>
                    <th>Component</th>
                    <th>Assigned Team</th>
                    <th>Confidence</th>
                    <th>Latency</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredResults.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ color: '#64748b', fontSize: '0.8rem' }}>{item.index + 1}</td>
                      <td style={{ fontWeight: 600, color: '#f3f4f6', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {item.triage?.title || item.input_preview}
                      </td>
                      <td>
                        {item.triage?.severity ? (
                          <span className={`badge badge-${item.triage.severity.toLowerCase()}`}>
                            {item.triage.severity}
                          </span>
                        ) : (
                          <span className="badge badge-p1">FAILED</span>
                        )}
                      </td>
                      <td style={{ color: '#cbd5e1' }}>{item.triage?.component || 'N/A'}</td>
                      <td style={{ color: '#94a3b8' }}>{item.triage?.suggested_assignee_team || 'N/A'}</td>
                      <td>
                        <span style={{ 
                          fontWeight: 600, 
                          color: item.triage?.confidence === 'High' ? '#34d399' : (item.triage?.confidence === 'Medium' ? '#fbbf24' : '#f87171') 
                        }}>
                          {item.triage?.confidence || 'N/A'}
                        </span>
                      </td>
                      <td style={{ color: '#64748b', fontSize: '0.8rem' }}>{item.processing_time_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
