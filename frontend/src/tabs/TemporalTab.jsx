import React, { useState } from 'react';
import { Icon } from '../components/Icons';

export const TemporalTab = () => {
  const [seqLength, setSeqLength] = useState(24);
  const [onsetIdx, setOnsetIdx] = useState(14);
  const [threshold, setThreshold] = useState(5.0);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState(null);

  const runBisection = async () => {
    setIsRunning(true);
    try {
      const res = await fetch('/api/temporal-bisect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sequence_length: seqLength,
          change_onset_index: onsetIdx,
          change_threshold: threshold
        })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert('Bisection failed: ' + err.message);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="view-body">
      {/* Simulation Controls */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>O(LOG N) TEMPORAL BISECTION SEARCH SIMULATION</span>
          <span className="c2-badge badge-cyan">LOGARITHMIC TIMELINE REDUCTION</span>
        </div>
        <div className="c2-card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', alignItems: 'flex-end' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>SEQUENCE LENGTH (OBSERVATIONS):</span>
                <span className="mono-nums" style={{ color: 'var(--c2-cyan)', fontWeight: 700 }}>{seqLength}</span>
              </div>
              <input
                type="range"
                min="8"
                max="60"
                step="4"
                value={seqLength}
                onChange={(e) => {
                  const val = parseInt(e.target.value);
                  setSeqLength(val);
                  if (onsetIdx >= val) setOnsetIdx(val - 2);
                }}
                style={{ width: '100%', accentColor: 'var(--c2-cyan)' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>GROUND TRUTH ONSET (INDEX):</span>
                <span className="mono-nums" style={{ color: 'var(--c2-amber)', fontWeight: 700 }}>{onsetIdx}</span>
              </div>
              <input
                type="range"
                min="1"
                max={seqLength - 1}
                step="1"
                value={onsetIdx}
                onChange={(e) => setOnsetIdx(parseInt(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--c2-amber)' }}
              />
            </div>

            <div>
              <button
                className="c2-btn c2-btn-primary"
                style={{ width: '100%', height: '36px' }}
                disabled={isRunning}
                onClick={runBisection}
              >
                <Icon name="timeline" size={13} />
                <span>{isRunning ? 'Computing Bisection...' : 'Run O(log N) Bisection'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results HUD */}
      {result && (
        <div className="c2-card" style={{ borderLeft: '3px solid var(--c2-emerald)' }}>
          <div className="c2-card-body">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>DETECTED ONSET TIMESTAMP: </span>
                <strong style={{ color: 'var(--c2-cyan)', fontSize: '14px', fontFamily: 'var(--font-mono)' }}>
                  {result.onset_timestamp || `Observation #${result.onset_index}`}
                </strong>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>DETECTION ACCURACY: </span>
                <strong style={{ color: result.onset_index === onsetIdx ? '#10b981' : '#f59e0b' }}>
                  {result.onset_index === onsetIdx ? '100% EXACT MATCH (ZERO ERROR)' : `Offset by ${Math.abs(result.onset_index - onsetIdx)} obs`}
                </strong>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>INFERENCE EVALS: </span>
                <strong className="mono-nums" style={{ color: '#38bdf8' }}>
                  {result.total_evaluations} evaluations vs {seqLength} linear
                </strong>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>COMPUTE EFFICIENCY: </span>
                <strong className="mono-nums" style={{ color: '#10b981' }}>
                  {Math.round((1 - result.total_evaluations / seqLength) * 100)}% COMPUTE SAVINGS
                </strong>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Visual Timeline Diagram */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>SEQUENCE TIMELINE VISUALIZATION</span>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>GREEN = INVARIANT, RED = STRUCTURAL ONSET</span>
        </div>
        <div className="c2-card-body">
          <div style={{ display: 'flex', gap: '3px', alignItems: 'center', overflowX: 'auto', padding: '12px 0' }}>
            {Array.from({ length: seqLength }).map((_, i) => {
              const isOnset = result ? i === result.onset_index : i === onsetIdx;
              const isPastOnset = i >= onsetIdx;
              return (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    minWidth: '22px',
                    height: '56px',
                    background: isPastOnset ? 'rgba(239, 68, 68, 0.25)' : 'rgba(16, 185, 129, 0.2)',
                    border: isOnset ? '2px solid var(--c2-cyan)' : '1px solid var(--border-subtle)',
                    borderRadius: '2px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '4px 2px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '9px',
                    position: 'relative'
                  }}
                  title={`Index ${i}: ${isPastOnset ? 'Changed' : 'Pre-change'}`}
                >
                  <span style={{ color: isOnset ? 'var(--c2-cyan)' : 'var(--text-muted)' }}>{i}</span>
                  {isOnset && (
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--c2-cyan)' }}></div>
                  )}
                  <span style={{ color: isPastOnset ? 'var(--c2-crimson)' : 'var(--c2-emerald)', fontWeight: 700 }}>
                    {isPastOnset ? 'CHG' : 'INV'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
