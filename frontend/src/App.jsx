import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, NAV_ITEMS } from './components/Sidebar';
import { DashboardTab } from './tabs/DashboardTab';
import { ChatTab } from './tabs/ChatTab';
import { ChangeDetectTab } from './tabs/ChangeDetectTab';
import { SemanticSearchTab } from './tabs/SemanticSearchTab';
import { TemporalTab } from './tabs/TemporalTab';
import { ClusteringTab } from './tabs/ClusteringTab';
import { AnalystReviewTab } from './tabs/AnalystReviewTab';
import { BenchmarksTab } from './tabs/BenchmarksTab';
import { DatasetsTab } from './tabs/DatasetsTab';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  // Keyboard shortcut listener for tactical command rail ([1] to [9])
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't intercept when user is typing in an input or textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
        return;
      }
      const num = parseInt(e.key);
      if (num >= 1 && num <= NAV_ITEMS.length) {
        setActiveTab(NAV_ITEMS[num - 1].id);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardTab onNavigate={setActiveTab} />;
      case 'chat':
        return <ChatTab />;
      case 'change':
        return <ChangeDetectTab />;
      case 'search':
        return <SemanticSearchTab />;
      case 'timeline':
        return <TemporalTab />;
      case 'cluster':
        return <ClusteringTab />;
      case 'audit':
        return <AnalystReviewTab />;
      case 'benchmarks':
        return <BenchmarksTab />;
      case 'datasets':
        return <DatasetsTab />;
      default:
        return <DashboardTab onNavigate={setActiveTab} />;
    }
  };

  const currentNav = NAV_ITEMS.find((n) => n.id === activeTab);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <Header />
      <div className="app-workspace">
        <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />
        <main className="app-main-viewport">
          <div className="view-header">
            <div className="view-title-wrap">
              <span className="view-title">{currentNav?.label || 'SUBSYSTEM'}</span>
              <span className="view-badge">{currentNav?.badge || 'AIR-GAP'}</span>
            </div>
            <div className="view-actions">
              <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                HOTKEY: [{currentNav?.hotkey}] &bull; NODE DEV/PROD
              </span>
            </div>
          </div>
          {renderActiveTab()}
        </main>
      </div>
    </div>
  );
}

export default App;
