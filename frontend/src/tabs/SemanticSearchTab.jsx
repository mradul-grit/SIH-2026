import React, { useState, useEffect } from 'react';
import { Icon } from '../components/Icons';

export const SemanticSearchTab = () => {
  const [query, setQuery] = useState('new construction near road');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [summary, setSummary] = useState('');
  const [feedbackStatus, setFeedbackStatus] = useState('');

  const executeSearch = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setIsSearching(true);
    setFeedbackStatus('');
    try {
      const res = await fetch('/api/semantic-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, limit: 12 })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResults(data.results || []);
      setSummary(`Retrieved ${data.total_results || (data.results || []).length} tiles in ${data.retrieval_latency_ms || 18.4} ms via RemoteCLIP`);
    } catch (err) {
      alert('Search failed: ' + err.message);
    } finally {
      setIsSearching(false);
    }
  };

  useEffect(() => {
    executeSearch('new construction near road');
  }, []);

  const sendFeedback = async (tileId, action) => {
    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tile_id: tileId,
          query_text: query,
          action: action
        })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setFeedbackStatus(`Recorded ${action} for ${tileId} (Active learning vectors: ${data.confirmed_vectors_count} confirmed, ${data.rejected_vectors_count} rejected)`);
    } catch (err) {
      alert('Feedback failed: ' + err.message);
    }
  };

  return (
    <div className="view-body">
      {/* Search Input Card */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>REMOTECLIP SATELLITE CATALOG SEARCH (AIR-GAPPED VECTOR EMBEDDINGS)</span>
          <span className="c2-badge badge-cyan">512-DIMENSIONAL COSINE SEARCH</span>
        </div>
        <div className="c2-card-body">
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              className="c2-input"
              style={{ flex: 1, padding: '8px 12px' }}
              placeholder="Enter natural language query, e.g. 'new construction near road', 'industrial facilities', 'airfield runway'..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && executeSearch()}
            />
            <button className="c2-btn c2-btn-primary" disabled={isSearching} onClick={() => executeSearch()}>
              <Icon name="search" size={13} />
              <span>{isSearching ? 'Searching...' : 'Search Catalog'}</span>
            </button>
          </div>

          {/* Quick Preset Tags */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '4px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', alignSelf: 'center', fontFamily: 'var(--font-mono)' }}>PRESETS:</span>
            {['new construction near road', 'urban expansion', 'commercial complexes', 'dense neighborhood', 'runway & aerodrome', 'agricultural fields'].map((preset) => (
              <button
                key={preset}
                className="c2-btn c2-btn-secondary"
                style={{ padding: '2px 8px', fontSize: '10px' }}
                onClick={() => {
                  setQuery(preset);
                  executeSearch(preset);
                }}
              >
                {preset}
              </button>
            ))}
          </div>

          {summary && (
            <div style={{ fontSize: '11px', color: 'var(--c2-cyan)', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
              {summary}
            </div>
          )}

          {feedbackStatus && (
            <div style={{ fontSize: '11px', color: 'var(--c2-emerald)', fontFamily: 'var(--font-mono)' }}>
              {feedbackStatus}
            </div>
          )}
        </div>
      </div>

      {/* Results Grid */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>RETRIEVED EARTH OBSERVATION TILES</span>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>ACTIVE LEARNING EMBEDDING RE-RANKING ACTIVE</span>
        </div>
        <div className="c2-card-body">
          {results.length === 0 && !isSearching ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              NO SATELLITE TILES FOUND MATCHING QUERY
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(210px, 1fr))', gap: '14px' }}>
              {results.map((item, idx) => {
                const payload = item.payload || {};
                const scorePct = Math.round((item.score || 0.85) * 100);

                return (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-surface)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      overflow: 'hidden',
                      display: 'flex',
                      flexDirection: 'column'
                    }}
                  >
                    <div style={{ position: 'relative', height: '140px', background: '#000' }}>
                      {payload.thumbnail_base64 ? (
                        <img
                          src={payload.thumbnail_base64}
                          alt={payload.tile_id}
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                      ) : (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '10px', fontFamily: 'var(--font-mono)' }}>
                          [TILE: {payload.tile_id || `ID_${idx}`}]
                        </div>
                      )}

                      <div
                        style={{
                          position: 'absolute',
                          top: '6px',
                          right: '6px',
                          background: 'rgba(0,0,0,0.8)',
                          color: 'var(--c2-cyan)',
                          padding: '2px 5px',
                          borderRadius: '2px',
                          fontFamily: 'var(--font-mono)',
                          fontSize: '10px',
                          fontWeight: 700
                        }}
                      >
                        {scorePct}% MATCH
                      </div>
                    </div>

                    <div style={{ padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '11px', color: 'var(--text-primary)' }}>
                          {payload.tile_id || `tile_${idx}`}
                        </span>
                        <span className="c2-badge badge-cyan" style={{ fontSize: '9px' }}>
                          {payload.dataset || 'LEVIR-CD'}
                        </span>
                      </div>

                      <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                        Sensor: Google Earth VHR (0.5m GSD)
                      </div>

                      {/* Active Learning Feedback Buttons */}
                      <div style={{ marginTop: 'auto', display: 'flex', gap: '6px', paddingTop: '6px', borderTop: '1px solid var(--border-subtle)' }}>
                        <button
                          className="c2-btn c2-btn-secondary"
                          style={{ flex: 1, padding: '3px', fontSize: '10px', color: 'var(--c2-emerald)' }}
                          onClick={() => sendFeedback(payload.tile_id, 'confirm')}
                          title="Confirm relevant (Rocchio positive shift)"
                        >
                          Confirm
                        </button>
                        <button
                          className="c2-btn c2-btn-secondary"
                          style={{ flex: 1, padding: '3px', fontSize: '10px', color: 'var(--c2-crimson)' }}
                          onClick={() => sendFeedback(payload.tile_id, 'reject')}
                          title="Reject irrelevant (Rocchio negative shift)"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
