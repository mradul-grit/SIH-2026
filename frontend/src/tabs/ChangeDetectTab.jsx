import React, { useState } from 'react';
import { CurtainSwipe } from '../components/CurtainSwipe';
import { Icon } from '../components/Icons';

export const ChangeDetectTab = () => {
  const [t1Base64, setT1Base64] = useState(null);
  const [t2Base64, setT2Base64] = useState(null);
  const [maskBase64, setMaskBase64] = useState(null);
  const [overlayBase64, setOverlayBase64] = useState(null);
  const [gtBase64, setGtBase64] = useState(null);

  const [t1File, setT1File] = useState(null);
  const [t2File, setT2File] = useState(null);

  const [modelType, setModelType] = useState('siamese_resnet18_cbam');
  const [threshold, setThreshold] = useState(0.40);
  const [applyFilter, setApplyFilter] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  const [curatedSample, setCuratedSample] = useState('levir_test_10');
  const [swipeMode, setSwipeMode] = useState('t1_t2'); // 't1_t2', 't2_overlay', 't1_overlay', 'gt_pred'

  const [metrics, setMetrics] = useState(null);

  const loadBenchmarkScene = async (sampleId) => {
    try {
      const res = await fetch(`/api/sample-pair/${sampleId}`);
      if (!res.ok) throw new Error('Failed to load benchmark scene');
      const data = await res.json();

      setT1Base64(data.t1_base64);
      setT2Base64(data.t2_base64);
      setGtBase64(data.gt_base64 || null);
      setMaskBase64(null);
      setOverlayBase64(null);
      setMetrics(null);

      // Create File objects for change-detect endpoint
      const b1 = await (await fetch(data.t1_base64)).blob();
      const b2 = await (await fetch(data.t2_base64)).blob();
      setT1File(new File([b1], `${data.filename}_T1.png`, { type: 'image/png' }));
      setT2File(new File([b2], `${data.filename}_T2.png`, { type: 'image/png' }));
    } catch (err) {
      alert('Error loading benchmark pair: ' + err.message);
    }
  };

  const handleManualUpload = (e, isT1) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      if (isT1) {
        setT1Base64(evt.target.result);
        setT1File(file);
      } else {
        setT2Base64(evt.target.result);
        setT2File(file);
      }
    };
    reader.readAsDataURL(file);
  };

  const runDetection = async () => {
    if (!t1File || !t2File) {
      alert('Please provide both Pre-change (T1) and Post-change (T2) images.');
      return;
    }

    setIsRunning(true);
    try {
      const formData = new FormData();
      formData.append('file_t1', t1File);
      formData.append('file_t2', t2File);
      formData.append('threshold', threshold.toString());
      formData.append('apply_false_alarm_filter', applyFilter.toString());
      formData.append('model_type', modelType);

      const res = await fetch('/api/change-detect', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      setMaskBase64(data.images?.mask_base64);
      setOverlayBase64(data.images?.overlay_base64);
      setMetrics(data);
      setSwipeMode('t2_overlay');
    } catch (err) {
      alert('Inference error: ' + err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const exportGeoJSON = async () => {
    const tileId = curatedSample.replace('levir_', '');
    const changePct = metrics?.change_percentage || 9.72;
    const conf = metrics?.confidence || 0.938;

    window.open(`/api/export-geojson/${tileId}?change_pct=${changePct}&confidence=${conf}`, '_blank');
  };

  // Determine images for Curtain Swipe based on mode
  let leftImg = t1Base64;
  let rightImg = t2Base64;
  let leftLabel = 'Time 1 (Pre-Change)';
  let rightLabel = 'Time 2 (Post-Change)';

  if (swipeMode === 't2_overlay') {
    leftImg = t2Base64;
    rightImg = overlayBase64 || t2Base64;
    leftLabel = 'Time 2 (Actual)';
    rightLabel = 'AI Change Overlay';
  } else if (swipeMode === 't1_overlay') {
    leftImg = t1Base64;
    rightImg = overlayBase64 || t1Base64;
    leftLabel = 'Time 1 (Pre-Change)';
    rightLabel = 'AI Change Overlay';
  } else if (swipeMode === 'gt_pred') {
    leftImg = gtBase64;
    rightImg = maskBase64;
    leftLabel = 'Ground Truth Mask';
    rightLabel = 'AI Predicted Mask';
  }

  return (
    <div className="view-body">
      {/* Benchmark Scenes Fast Loader */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>CURATED BENCHMARK SCENES (GROUND TRUTH LABELS INCLUDED)</span>
          <span className="c2-badge badge-cyan">LEVIR-CD TEST SPLIT</span>
        </div>
        <div className="c2-card-body" style={{ flexDirection: 'row', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <select
            className="c2-select"
            style={{ flex: 1, minWidth: '280px' }}
            value={curatedSample}
            onChange={(e) => setCuratedSample(e.target.value)}
          >
            <option value="levir_test_10">LEVIR-CD test_10 (Suburban Housing - High Change: ~9.7%)</option>
            <option value="levir_test_100">LEVIR-CD test_100 (Commercial Complex - Large Buildings: ~11.3%)</option>
            <option value="levir_test_14">LEVIR-CD test_14 (Dense Neighborhood - Fine Buildings: ~10.8%)</option>
            <option value="levir_test_1">LEVIR-CD test_1 (Agricultural Land - 0.0% Invariant Control)</option>
          </select>

          <button className="c2-btn c2-btn-secondary" onClick={() => loadBenchmarkScene(curatedSample)}>
            Load Benchmark Scene
          </button>
        </div>
      </div>

      {/* Control Strip */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>INFERENCE CONTROLS &amp; ARCHITECTURE CONFIGURATION</span>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>NATIVE ADAPTIVE TILING (256x256, STRIDE 224)</span>
        </div>
        <div className="c2-card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', alignItems: 'flex-end' }}>
            <div>
              <label style={{ fontSize: '10px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontFamily: 'var(--font-mono)' }}>
                PRE-EVENT SENSOR PASS (T1):
              </label>
              <input type="file" accept="image/*" className="c2-input" style={{ width: '100%' }} onChange={(e) => handleManualUpload(e, true)} />
            </div>

            <div>
              <label style={{ fontSize: '10px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontFamily: 'var(--font-mono)' }}>
                POST-EVENT SENSOR PASS (T2):
              </label>
              <input type="file" accept="image/*" className="c2-input" style={{ width: '100%' }} onChange={(e) => handleManualUpload(e, false)} />
            </div>

            <div>
              <label style={{ fontSize: '10px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontFamily: 'var(--font-mono)' }}>
                NEURAL ARCHITECTURE:
              </label>
              <select className="c2-select" style={{ width: '100%' }} value={modelType} onChange={(e) => setModelType(e.target.value)}>
                <option value="siamese_resnet18_cbam">Siamese ResNet-18 + CBAM (Primary)</option>
                <option value="changeformer">Lightweight ChangeFormer (Baseline)</option>
              </select>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>DECISION THRESHOLD:</span>
                <span className="mono-nums" style={{ color: 'var(--c2-cyan)', fontWeight: 700 }}>{threshold.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.90"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--c2-cyan)' }}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', height: '36px' }}>
              <input
                type="checkbox"
                id="filter-toggle"
                checked={applyFilter}
                onChange={(e) => setApplyFilter(e.target.checked)}
                style={{ accentColor: 'var(--c2-cyan)' }}
              />
              <label htmlFor="filter-toggle" style={{ fontSize: '11px', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                False Alarm Suppression (VARI)
              </label>
            </div>

            <div>
              <button
                className="c2-btn c2-btn-primary"
                style={{ width: '100%', height: '36px' }}
                disabled={isRunning || !t1File || !t2File}
                onClick={runDetection}
              >
                <Icon name="zap" size={13} />
                <span>{isRunning ? 'Running Inference...' : 'Execute Change Detection'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics HUD (Shown after inference) */}
      {metrics && (
        <div className="c2-card" style={{ borderLeft: '3px solid var(--c2-cyan)' }}>
          <div className="c2-card-body" style={{ padding: '10px 14px' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                <div>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>CHANGE STATUS: </span>
                  <strong style={{ color: metrics.change_detected ? 'var(--c2-crimson)' : 'var(--c2-emerald)' }}>
                    {metrics.change_detected ? 'CONFIRMED CHANGE' : 'INVARIANT SECTOR'}
                  </strong>
                </div>
                <div>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>FOOTPRINT: </span>
                  <strong className="mono-nums" style={{ color: 'var(--c2-cyan)' }}>
                    {metrics.change_percentage}% ({metrics.change_pixels.toLocaleString()} px)
                  </strong>
                </div>
                <div>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>CONFIDENCE: </span>
                  <strong className="mono-nums">{metrics.confidence}</strong>
                </div>
                <div>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>INFERENCE LATENCY: </span>
                  <strong className="mono-nums" style={{ color: '#10b981' }}>{metrics.latency_ms} ms</strong>
                </div>
                <div>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>RADIOMETRIC USABILITY: </span>
                  <strong style={{ color: metrics.radiometric_quality?.is_usable ? '#10b981' : '#f59e0b' }}>
                    {metrics.radiometric_quality?.is_usable ? 'OPTIMAL' : 'DEGRADED'}
                  </strong>
                </div>
              </div>

              <button className="c2-btn c2-btn-secondary" onClick={exportGeoJSON}>
                <Icon name="download" size={12} />
                <span>Export RFC 7946 GeoJSON</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Curtain Swipe Viewer */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>CURTAIN SWIPE INTERACTIVE COMPARATOR (PRECISION SLIDER)</span>
          {/* Mode Switcher Buttons */}
          <div style={{ display: 'flex', gap: '4px' }}>
            <button
              className={`c2-btn ${swipeMode === 't1_t2' ? 'c2-btn-primary' : 'c2-btn-secondary'}`}
              style={{ padding: '2px 8px', fontSize: '10px' }}
              onClick={() => setSwipeMode('t1_t2')}
            >
              T1 vs T2
            </button>
            <button
              className={`c2-btn ${swipeMode === 't2_overlay' ? 'c2-btn-primary' : 'c2-btn-secondary'}`}
              style={{ padding: '2px 8px', fontSize: '10px' }}
              onClick={() => setSwipeMode('t2_overlay')}
            >
              T2 vs Overlay
            </button>
            <button
              className={`c2-btn ${swipeMode === 't1_overlay' ? 'c2-btn-primary' : 'c2-btn-secondary'}`}
              style={{ padding: '2px 8px', fontSize: '10px' }}
              onClick={() => setSwipeMode('t1_overlay')}
            >
              T1 vs Overlay
            </button>
            {gtBase64 && (
              <button
                className={`c2-btn ${swipeMode === 'gt_pred' ? 'c2-btn-primary' : 'c2-btn-secondary'}`}
                style={{ padding: '2px 8px', fontSize: '10px' }}
                onClick={() => setSwipeMode('gt_pred')}
              >
                GT vs Pred
              </button>
            )}
          </div>
        </div>
        <div className="c2-card-body" style={{ padding: '10px' }}>
          <CurtainSwipe
            bgImg={rightImg}
            fgImg={leftImg}
            leftLabel={leftLabel}
            rightLabel={rightLabel}
          />
        </div>
      </div>
    </div>
  );
};
