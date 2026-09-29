import React from 'react';
import { Icon } from './Icons';

export const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: 'dashboard', hotkey: '1', badge: 'STATUS' },
  { id: 'chat', label: 'AI Tactical Chat', icon: 'chat', hotkey: '2', badge: '100% OFFLINE', badgeColor: 'badge-cyan' },
  { id: 'change', label: 'Change Detection', icon: 'change', hotkey: '3', badge: 'NATIVE' },
  { id: 'search', label: 'Semantic Retrieval', icon: 'search', hotkey: '4', badge: 'QDRANT' },
  { id: 'timeline', label: 'Temporal Timeline', icon: 'timeline', hotkey: '5', badge: 'O(log N)' },
  { id: 'cluster', label: 'Discovery Clusters', icon: 'cluster', hotkey: '6', badge: 'UMAP' },
  { id: 'audit', label: 'Analyst Audit Log', icon: 'audit', hotkey: '7', badge: 'SHA-256' },
  { id: 'benchmarks', label: 'Benchmarks & HW', icon: 'benchmark', hotkey: '8', badge: 'RTX 3050' },
  { id: 'datasets', label: 'Dataset Inventory', icon: 'dataset', hotkey: '9', badge: '5 CORPUS' },
];

export const Sidebar = ({ activeTab, onSelectTab }) => {
  return (
    <aside className="app-sidebar">
      <div>
        <div className="nav-rail-group">
          <div className="nav-rail-heading">Operational Subsystems</div>
          {NAV_ITEMS.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                className={`nav-rail-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelectTab(item.id)}
              >
                <div className="nav-item-left">
                  <Icon name={item.icon} size={14} color={isActive ? 'var(--c2-cyan)' : 'var(--text-secondary)'} />
                  <span>{item.label}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {item.badge && (
                    <span className={`c2-badge ${item.badgeColor || 'badge-cyan'}`} style={{ fontSize: '9px', padding: '1px 4px' }}>
                      {item.badge}
                    </span>
                  )}
                  <span className="nav-hotkey">[{item.hotkey}]</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="system-status-indicator">
          <span style={{ color: 'var(--text-muted)' }}>AIR-GAP STATUS:</span>
          <span style={{ color: 'var(--c2-emerald)', fontWeight: 700 }}>SECURED</span>
        </div>
        <div className="system-status-indicator">
          <span style={{ color: 'var(--text-muted)' }}>EXTERNAL APIS:</span>
          <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>0 ACTIVE (BLOCKED)</span>
        </div>
        <div className="system-status-indicator">
          <span style={{ color: 'var(--text-muted)' }}>NETWORK ISOLATION:</span>
          <span style={{ color: 'var(--c2-cyan)' }}>LOCAL ONLY</span>
        </div>
      </div>
    </aside>
  );
};
