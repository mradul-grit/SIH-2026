import React, { useState, useEffect } from 'react';
import { Icon } from '../components/Icons';

export const AnalystReviewTab = () => {
  const [logs, setLogs] = useState([]);
  const [tileId, setTileId] = useState('test_10');
  const [dataset, setDataset] = useState('LEVIR-CD');
  const [action, setAction] = useState('confirm');
  const [analystId, setAnalystId] = useState('ANALYST-DEF-042');
  const [notes, setNotes] = useState('Structural expansion confirmed. Ground truth match.');
  const [lastHash, setLastHash] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchLogs = async () => {
    try {
      const res = await fetch('/api/audit-logs');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setLogs(data.records || []);
    } catch (err) {
      console.warn('Error fetching audit logs:', err);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const submitReview = async () => {
    setIsSubmitting(true);
    try {
      const res = await fetch('/api/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tile_id: tileId,
          dataset_name: dataset,
          action: action,
          analyst_id: analystId,
          model_version: 'v2.4-cbam',
          threshold: 0.40,
          change_percentage: 9.72,
          notes: notes
        })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setLastHash(data.provenance_hash);
      fetchLogs();
    } catch (err) {
      alert('Review submission failed: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="view-body">
      {/* Review Submission Card */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>ANALYST DECISION AUDIT &amp; CRYPTOGRAPHIC PROVENANCE</span>
          <span className="c2-badge badge-emerald">SHA-256 SEALED</span>
        </div>
        <div className="c2-card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', alignItems: 'flex-end' }}>
            <div>
              <label style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '4px' }}>
                TILE IDENTIFIER:
              </label>
              <input type="text" className="c2-input" style={{ width: '100%' }} value={tileId} onChange={(e) => setTileId(e.target.value)} />
            </div>

            <div>
              <label style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '4px' }}>
                DATASET CORPUS:
              </label>
              <select className="c2-select" style={{ width: '100%' }} value={dataset} onChange={(e) => setDataset(e.target.value)}>
                <option value="LEVIR-CD">LEVIR-CD</option>
                <option value="LEVIR-CD+">LEVIR-CD+</option>
                <option value="WHU-CD">WHU-CD</option>
                <option value="S2Looking">S2Looking</option>
                <option value="SYSU-CD">SYSU-CD</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '4px' }}>
                ANALYST DECISION:
              </label>
              <select className="c2-select" style={{ width: '100%' }} value={action} onChange={(e) => setAction(e.target.value)}>
                <option value="confirm">CONFIRM (True Positive Change)</option>
                <option value="reject">REJECT (False Alarm / Invariant)</option>
                <option value="escalate">ESCALATE FOR SATELLITE RETASKING</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '4px' }}>
                ANALYST CALLSIGN:
              </label>
              <input type="text" className="c2-input" style={{ width: '100%' }} value={analystId} onChange={(e) => setAnalystId(e.target.value)} />
            </div>

            <div style={{ gridColumn: 'span 2' }}>
              <label style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '4px' }}>
                INTELLIGENCE REMARKS:
              </label>
              <input type="text" className="c2-input" style={{ width: '100%' }} value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>

            <div>
              <button className="c2-btn c2-btn-primary" style={{ width: '100%', height: '34px' }} disabled={isSubmitting} onClick={submitReview}>
                <Icon name="audit" size={13} />
                <span>{isSubmitting ? 'Signing...' : 'Sign & Record Decision'}</span>
              </button>
            </div>
          </div>

          {lastHash && (
            <div style={{ marginTop: '10px', padding: '8px 12px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 'var(--radius-sm)', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
              <span style={{ color: 'var(--c2-emerald)', fontWeight: 700 }}>PROVENANCE SEAL GENERATED: </span>
              <span style={{ color: '#fff', wordBreak: 'break-all' }}>{lastHash}</span>
            </div>
          )}
        </div>
      </div>

      {/* Audit History Log */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>HISTORICAL DECISION LEDGER (TAMPER-EVIDENT AUDIT TRAIL)</span>
          <button className="c2-btn c2-btn-secondary" style={{ padding: '2px 8px', fontSize: '10px' }} onClick={fetchLogs}>
            Refresh Ledger
          </button>
        </div>
        <div className="c2-card-body">
          <div className="c2-table-wrapper">
            <table className="c2-table">
              <thead>
                <tr>
                  <th>Timestamp (UTC)</th>
                  <th>Tile ID</th>
                  <th>Dataset</th>
                  <th>Decision</th>
                  <th>Analyst</th>
                  <th>Notes</th>
                  <th>SHA-256 Provenance Hash</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                      No audit decisions recorded in this session.
                    </td>
                  </tr>
                ) : (
                  logs.map((row, idx) => (
                    <tr key={idx}>
                      <td className="mono-nums">{row.timestamp ? new Date(row.timestamp * 1000).toISOString().replace('T', ' ').substring(0, 19) : '--'}</td>
                      <td><strong>{row.tile_id}</strong></td>
                      <td>{row.dataset_name}</td>
                      <td>
                        <span className={`c2-badge ${row.action === 'confirm' ? 'badge-emerald' : row.action === 'reject' ? 'badge-crimson' : 'badge-amber'}`}>
                          {row.action}
                        </span>
                      </td>
                      <td className="mono-nums">{row.analyst_id}</td>
                      <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{row.notes}</td>
                      <td className="mono-nums" style={{ fontSize: '10px', color: 'var(--c2-cyan)' }}>
                        {row.record_hash?.substring(0, 16)}...
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
