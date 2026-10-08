import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopNav } from './components/TopNav';
import { DashboardView } from './components/DashboardView';
import { AnalyzeView } from './components/AnalyzeView';
import { BatchView } from './components/BatchView';
import { DuplicatesView } from './components/DuplicatesView';
import { HistoryView } from './components/HistoryView';
import { AnalyticsView } from './components/AnalyticsView';
import { HealthView } from './components/HealthView';
import { SettingsView } from './components/SettingsView';
import { apiService } from './services/api';
import { HealthStatus, AnalyticsData } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchPlatformData = async () => {
    setIsLoading(true);
    try {
      const [h, a] = await Promise.allSettled([
        apiService.getHealth(),
        apiService.getAnalytics(),
      ]);

      if (h.status === 'fulfilled') {
        setHealth(h.value);
      } else {
        setHealth({
          status: 'degraded',
          backend: 'offline',
          llm_provider: 'gemini',
          llm_status: 'standby',
          llm_model: 'gemini-flash-lite-latest',
          vector_store_entries: 34,
          feedback_entries: 0,
          total_triaged: 34,
          reachable: false,
        });
      }

      if (a.status === 'fulfilled') {
        setAnalytics(a.value);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPlatformData();
  }, []);

  return (
    <div className="app-layout">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        health={health} 
      />

      <div className="main-wrapper">
        <TopNav 
          health={health} 
          onRefresh={fetchPlatformData} 
          isLoading={isLoading} 
        />

        <main>
          {activeTab === 'dashboard' && (
            <DashboardView 
              analytics={analytics} 
              health={health} 
              onNavigateToAnalyze={() => setActiveTab('analyze')} 
            />
          )}

          {activeTab === 'analyze' && <AnalyzeView />}
          {activeTab === 'batch' && <BatchView />}
          {activeTab === 'duplicates' && <DuplicatesView />}
          {activeTab === 'history' && <HistoryView />}
          {activeTab === 'analytics' && <AnalyticsView analytics={analytics} />}
          {activeTab === 'health' && (
            <HealthView 
              health={health} 
              onRefresh={fetchPlatformData} 
              isLoading={isLoading} 
            />
          )}
          {activeTab === 'settings' && <SettingsView />}
        </main>
      </div>
    </div>
  );
};

export default App;
