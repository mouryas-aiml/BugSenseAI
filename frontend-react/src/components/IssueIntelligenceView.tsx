import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  Download,
  ExternalLink,
  LoaderCircle,
  Search,
  ShieldAlert,
  Sparkles,
  Users,
  X,
} from 'lucide-react';
import { apiService } from '../services/api';
import { IntelligenceStatus, IssueAnalytics, IssueCluster, IssueRecord, IssueResolution } from '../types';

const EMPTY_ANALYTICS: IssueAnalytics = {
  total_reports: 0,
  unique_issue_clusters: 0,
  duplicate_similar_reports: 0,
  top_issue: null,
  top_issue_percentage: 0,
  potentially_auto_resolvable: 0,
  human_escalations: 0,
  ai_resolution_rate: 0,
  average_confidence: 0,
  average_completeness: 0,
  open_count: 0,
  closed_count: 0,
  high_priority_count: 0,
  resolution_count: 0,
  category_distribution: {},
  component_distribution: {},
  most_discussed: [],
  clusters_with_resolutions: 0,
  trend_by_month: {},
  dataset_name: '',
};

type Filters = { query: string; category: string; state: string; priority: string; start_date: string; end_date: string };
const EMPTY_FILTERS: Filters = { query: '', category: '', state: '', priority: '', start_date: '', end_date: '' };

export const IssueIntelligenceView: React.FC = () => {
  const [status, setStatus] = useState<IntelligenceStatus | null>(null);
  const [analytics, setAnalytics] = useState<IssueAnalytics>(EMPTY_ANALYTICS);
  const [clusters, setClusters] = useState<IssueCluster[]>([]);
  const [issues, setIssues] = useState<IssueRecord[]>([]);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [selectedIssue, setSelectedIssue] = useState<IssueRecord | null>(null);
  const [resolution, setResolution] = useState<IssueResolution | null>(null);
  const [supportQuery, setSupportQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [preparing, setPreparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (nextFilters: Filters = filters) => {
    setLoading(true);
    setError(null);
    try {
      const params = Object.fromEntries(Object.entries(nextFilters).filter(([, value]) => value));
      const [nextAnalytics, nextClusters, nextIssues] = await Promise.all([
        apiService.getIssueAnalytics(params),
        apiService.getIssueClusters(params, 25, 0),
        apiService.getIssues(params, 25, 0),
      ]);
      setAnalytics(nextAnalytics);
      setClusters(nextClusters.items || []);
      setIssues(nextIssues.items || []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to load issue intelligence data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | undefined;
    const initialize = async () => {
      try {
        const current = await apiService.getIntelligenceStatus();
        setStatus(current);
        if (current.ready) {
          await loadData(EMPTY_FILTERS);
          return;
        }
        setPreparing(true);
        await apiService.prepareIntelligence();
        timer = setInterval(async () => {
          const next = await apiService.getIntelligenceStatus();
          setStatus(next);
          if (next.ready) {
            if (timer) clearInterval(timer);
            setPreparing(false);
            await loadData(EMPTY_FILTERS);
          }
        }, 2500);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Unable to initialize the issue index.');
        setLoading(false);
      }
    };
    initialize();
    return () => { if (timer) clearInterval(timer); };
  }, []);

  const selectFilter = (name: keyof Filters, value: string) => {
    const next = { ...filters, [name]: value };
    setFilters(next);
    void loadData(next);
  };

  const openIssue = async (issueId: string) => {
    try {
      setSelectedIssue(await apiService.getIssue(issueId));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to load issue details.');
    }
  };

  const runResolution = async () => {
    if (!supportQuery.trim()) return;
    try {
      setResolution(await apiService.resolveIssue(supportQuery));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to retrieve a grounded resolution.');
    }
  };

  const exportUrl = (kind: 'issues' | 'clusters' | 'kpis') => {
    const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value));
    window.open(apiService.intelligenceExportUrl(kind, params), '_blank', 'noopener,noreferrer');
  };

  if (preparing || (!status?.ready && loading)) {
    return (
      <div className="page-container">
        <div className="hero-banner">
          <div className="hero-tag">Dataset Intelligence Layer</div>
          <h1 className="hero-title">Preparing Real Issue Intelligence</h1>
          <p className="hero-desc">Downloading, anonymizing, embedding, and clustering the configured Hugging Face issue dataset. This happens once and is reused from the persistent index.</p>
        </div>
        <div className="card intelligence-loading">
          <LoaderCircle className="animate-spin" size={26} />
          <div>
            <strong>{status?.dataset_name || 'helmo/github-issues'}</strong>
            <p>{status?.record_count ? `${status.record_count} records indexed` : 'The first preparation may take a few minutes.'}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="hero-banner intelligence-hero">
        <div>
          <div className="hero-tag">RAG Resolution Operations</div>
          <h1 className="hero-title">Issue Intelligence Command Center</h1>
          <p className="hero-desc">Real GitHub issue discussions become searchable resolution evidence, semantic clusters, support responses, and escalation signals.</p>
        </div>
        <div className="export-menu" aria-label="Export issue intelligence">
          <button className="btn btn-primary"><Download size={15} /> Export CSV</button>
          <div className="export-options">
            <button onClick={() => exportUrl('issues')}>Issue dataset</button>
            <button onClick={() => exportUrl('clusters')}>Issue clusters</button>
            <button onClick={() => exportUrl('kpis')}>KPI summary</button>
          </div>
        </div>
      </div>

      {error && <div className="alert-box alert-error"><AlertCircle size={18} /><span>{error}</span><button onClick={() => setError(null)}><X size={15} /></button></div>}

      <div className="intelligence-kpis">
        {[
          ['Total Reports', analytics.total_reports, 'Imported issue records'],
          ['Issue Clusters', analytics.unique_issue_clusters, 'Semantic groups'],
          ['Similar Reports', analytics.duplicate_similar_reports, 'Reports beyond representatives'],
          ['Top Issue Share', `${analytics.top_issue_percentage}%`, analytics.top_issue || 'No dominant issue'],
          ['Auto-Resolvable', analytics.potentially_auto_resolvable, 'Have discussion evidence'],
          ['Human Escalations', analytics.human_escalations, 'Need more evidence'],
          ['AI Resolution Rate', `${analytics.ai_resolution_rate}%`, 'Grounded evidence rate'],
          ['Avg Completeness', `${analytics.average_completeness}%`, 'Description signal score'],
            ['Average Confidence', `${Math.round(analytics.average_confidence * 100)}%`, 'Resolution evidence strength'],
        ].map(([label, value, sub]) => (
          <div className="card intelligence-kpi" key={String(label)}><div className="stat-label">{label}</div><div className="stat-value">{value}</div><div className="stat-sub">{sub}</div></div>
        ))}
      </div>

      <div className="card intelligence-support">
        <div><span className="tag-provenance tag-inference">CUSTOMER SUPPORT</span><h2>Grounded Resolution Assistant</h2><p>Retrieve historical issue discussions and answer only from available resolution evidence.</p></div>
        <div className="support-query"><input value={supportQuery} onChange={(event) => setSupportQuery(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter') void runResolution(); }} placeholder="Describe the customer's issue..." /><button className="btn btn-primary" onClick={() => void runResolution()}><Sparkles size={15} /> Find resolution</button></div>
        {resolution && <div className={`resolution-panel ${resolution.resolution_available ? 'resolution-found' : 'resolution-missing'}`}>
          <div className="resolution-heading"><strong>{resolution.resolution_available ? 'Evidence-backed response' : 'Escalation recommended'}</strong><span>{resolution.confidence} confidence</span></div>
          <p>{resolution.answer}</p>
          {resolution.steps.length > 0 && <ol>{resolution.steps.map((step, index) => <li key={index}>{step}</li>)}</ol>}
          <div className="evidence-list"><strong>Evidence sources</strong>{resolution.evidence.length > 0 ? resolution.evidence.map((item) => <a key={item.issue_id} href={item.source_url} target="_blank" rel="noreferrer">{item.issue_id}: {item.title} <ExternalLink size={12} /></a>) : <span>No supporting resolution discussion was found.</span>}</div>
          {resolution.evidence[0] && <div className="support-actions"><span>Was this resolved?</span><button onClick={() => void apiService.sendSupportFeedback(resolution.evidence[0].issue_id, true)}>Yes</button><button onClick={() => void apiService.sendSupportFeedback(resolution.evidence[0].issue_id, false)}>No, escalate</button></div>}
        </div>}
      </div>

      <div className="card intelligence-filters">
        <div className="filter-search"><Search size={16} /><input value={filters.query} onChange={(event) => setFilters({ ...filters, query: event.target.value })} onKeyDown={(event) => { if (event.key === 'Enter') void loadData(filters); }} placeholder="Search issue title, body, or labels" /></div>
        <select value={filters.category} onChange={(event) => selectFilter('category', event.target.value)}><option value="">All categories</option>{Object.keys(analytics.category_distribution).map((category) => <option key={category}>{category}</option>)}</select>
        <select value={filters.state} onChange={(event) => selectFilter('state', event.target.value)}><option value="">All states</option><option value="open">Open</option><option value="closed">Closed</option></select>
        <select value={filters.priority} onChange={(event) => selectFilter('priority', event.target.value)}><option value="">All priorities</option><option value="High">High</option><option value="Medium">Medium</option><option value="Unspecified">Unspecified</option></select>
        <input type="date" value={filters.start_date} onChange={(event) => selectFilter('start_date', event.target.value)} /><input type="date" value={filters.end_date} onChange={(event) => selectFilter('end_date', event.target.value)} />
      </div>

      <div className="intelligence-chart-row">
        <div className="card mini-chart"><div className="section-heading"><div><span className="tag-provenance tag-rule">CATEGORY MIX</span><h2>Most Common Categories</h2></div></div>{Object.entries(analytics.category_distribution).slice(0, 6).map(([name, count]) => { const maximum = Math.max(...Object.values(analytics.category_distribution), 1); return <div className="bar-line" key={name}><span>{name}</span><div><i style={{ width: `${Math.round((count / maximum) * 100)}%` }} /></div><strong>{count}</strong></div>; })}</div>
        <div className="card mini-chart"><div className="section-heading"><div><span className="tag-provenance tag-fact">TIME SERIES</span><h2>Issue Trend by Month</h2></div></div>{Object.entries(analytics.trend_by_month).slice(-8).map(([month, count]) => { const maximum = Math.max(...Object.values(analytics.trend_by_month), 1); return <div className="bar-line" key={month}><span>{month || 'Unknown'}</span><div><i className="trend-bar" style={{ width: `${Math.round((count / maximum) * 100)}%` }} /></div><strong>{count}</strong></div>; })}</div>
      </div>

      <div className="intelligence-grid">
        <div className="card cluster-card"><div className="section-heading"><div><span className="tag-provenance tag-rule">SEMANTIC GROUPS</span><h2>Issue Clusters</h2></div><BarChart3 size={19} /></div>{loading ? <div className="empty-state"><LoaderCircle className="animate-spin" size={20} /></div> : clusters.length === 0 ? <div className="empty-state">No clusters match the active filters.</div> : <div className="cluster-list">{clusters.map((cluster) => <button className="cluster-row" key={cluster.cluster_id} onClick={() => void openIssue(cluster.representative_issue_id)}><div className="cluster-rank">{cluster.report_count}</div><div className="cluster-copy"><strong>{cluster.cluster_name}</strong><span>{cluster.category} · {cluster.percentage}% of filtered reports</span><small>{cluster.common_symptoms.join(' · ') || 'No repeated symptom terms'}{cluster.resolution_available ? ' · Resolution evidence available' : ''}</small></div><ChevronRight size={17} /></button>)}</div>}</div>
        <div className="card issue-card"><div className="section-heading"><div><span className="tag-provenance tag-fact">SOURCE RECORDS</span><h2>Recent Issues</h2></div><Users size={19} /></div>{issues.length === 0 ? <div className="empty-state">No source records match the active filters.</div> : <div className="issue-list">{issues.map((issue) => <button className="issue-row" key={issue.issue_id} onClick={() => void openIssue(issue.issue_id)}><span className={`state-dot ${issue.state.toLowerCase() === 'open' ? 'degraded' : 'online'}`} /><div><strong>{issue.title}</strong><span>{issue.category} · {issue.state} · {issue.discussion_count} comments</span></div><ChevronRight size={16} /></button>)}</div>}</div>
      </div>

      {selectedIssue && <div className="drawer-backdrop" onClick={() => setSelectedIssue(null)}><aside className="issue-drawer" onClick={(event) => event.stopPropagation()}><div className="drawer-header"><div><span className="tag-provenance tag-fact">{selectedIssue.issue_id}</span><h2>{selectedIssue.title}</h2></div><button onClick={() => setSelectedIssue(null)}><X size={18} /></button></div><div className="drawer-meta"><span>{selectedIssue.category}</span><span>{selectedIssue.state}</span><span>{selectedIssue.priority}</span><span>{selectedIssue.confidence} evidence</span><a href={selectedIssue.source_url} target="_blank" rel="noreferrer">Source <ExternalLink size={12} /></a></div><section><h3>AI Summary</h3><p>{selectedIssue.summary || 'No summary available.'}</p></section><section><h3>Original Report</h3><p>{selectedIssue.body || 'No issue body provided.'}</p></section><section><h3>Resolution</h3>{selectedIssue.resolution_available ? <><p>{selectedIssue.resolution_summary}</p><ol>{selectedIssue.resolution_steps.map((step, index) => <li key={index}>{step}</li>)}</ol></> : <div className="escalation-note"><ShieldAlert size={16} /> No grounded resolution found. Escalate to a human agent.</div>}</section><section><h3>Similar Reports</h3>{selectedIssue.similar_reports?.map((similar) => <button className="evidence-link" key={similar.issue_id} onClick={() => void openIssue(similar.issue_id)}>{similar.issue_id} · {similar.similarity}% · {similar.title}</button>)}</section><section><h3>Discussion</h3>{selectedIssue.comments.length ? selectedIssue.comments.map((comment, index) => <blockquote key={index}>{comment}</blockquote>) : <p>No comments recorded.</p>}</section><div className="drawer-footer"><CheckCircle2 size={16} /> {selectedIssue.escalation_recommendation}</div></aside></div>}
    </div>
  );
};
