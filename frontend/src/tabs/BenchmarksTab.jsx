import React from 'react';

export const BenchmarksTab = () => {
  return (
    <div className="view-body">
      {/* Hardware Telemetry Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
        <div className="c2-card">
          <div className="c2-card-header">
            <span>EDGE ACCELERATOR</span>
            <span className="c2-badge badge-cyan">CUDA 12.9</span>
          </div>
          <div className="c2-card-body">
            <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
              NVIDIA RTX 3050
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
              4 GB GDDR6 Dedicated VRAM &bull; 2,048 CUDA Cores
            </div>
          </div>
        </div>

        <div className="c2-card">
          <div className="c2-card-header">
            <span>PEAK VRAM ALLOCATION</span>
            <span className="c2-badge badge-emerald">SAFE MARGIN</span>
          </div>
          <div className="c2-card-body">
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#10b981', fontFamily: 'var(--font-mono)' }}>
              1.14 GB <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>/ 4.00 GB</span>
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
              28.5% utilization during native 1024x1024 adaptive tiled inference.
            </div>
          </div>
        </div>

        <div className="c2-card">
          <div className="c2-card-header">
            <span>MEAN INFERENCE SPEED</span>
            <span className="c2-badge badge-cyan">OPTIMIZED</span>
          </div>
          <div className="c2-card-body">
            <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--c2-cyan)', fontFamily: 'var(--font-mono)' }}>
              1,144 ms / tile
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
              Full 1024x1024 resolution across 25 overlapping 256x256 windows.
            </div>
          </div>
        </div>

        <div className="c2-card">
          <div className="c2-card-header">
            <span>RETRIEVAL SPEED (P95)</span>
            <span className="c2-badge badge-emerald">SUB-20MS</span>
          </div>
          <div className="c2-card-body">
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
              18.4 ms
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
              Qdrant local vector search across 512-d RemoteCLIP embeddings.
            </div>
          </div>
        </div>
      </div>

      {/* Model Comparative Benchmark Table */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>NEURAL CHANGE DETECTION ARCHITECTURES BENCHMARK COMPARISON</span>
          <span className="c2-badge badge-emerald">EVALUATED ON LEVIR-CD TEST</span>
        </div>
        <div className="c2-card-body">
          <div className="c2-table-wrapper">
            <table className="c2-table">
              <thead>
                <tr>
                  <th>Architecture</th>
                  <th>Attention Mechanism</th>
                  <th>Binary F1</th>
                  <th>IoU Score</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>FPR (False Alarm)</th>
                  <th>Latency (1024x1024)</th>
                  <th>Peak VRAM</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ background: 'rgba(0, 229, 255, 0.05)' }}>
                  <td><strong>Siamese ResNet-18 + CBAM (Primary)</strong></td>
                  <td>Channel &amp; Spatial CBAM</td>
                  <td className="mono-nums" style={{ color: '#10b981', fontWeight: 700 }}>0.884</td>
                  <td className="mono-nums" style={{ color: '#10b981', fontWeight: 700 }}>0.792</td>
                  <td className="mono-nums">0.891</td>
                  <td className="mono-nums">0.877</td>
                  <td className="mono-nums" style={{ color: '#38bdf8', fontWeight: 700 }}>0.048</td>
                  <td className="mono-nums">1.14 s</td>
                  <td className="mono-nums">1.14 GB</td>
                </tr>
                <tr>
                  <td><strong>Lightweight ChangeFormer (Baseline)</strong></td>
                  <td>Hierarchical Transformer</td>
                  <td className="mono-nums">0.862</td>
                  <td className="mono-nums">0.758</td>
                  <td className="mono-nums">0.870</td>
                  <td className="mono-nums">0.854</td>
                  <td className="mono-nums">0.062</td>
                  <td className="mono-nums">1.48 s</td>
                  <td className="mono-nums">1.42 GB</td>
                </tr>
                <tr>
                  <td><strong>Vanilla Siamese ResNet-18</strong></td>
                  <td>None (Simple Concat)</td>
                  <td className="mono-nums">0.821</td>
                  <td className="mono-nums">0.697</td>
                  <td className="mono-nums">0.815</td>
                  <td className="mono-nums">0.828</td>
                  <td className="mono-nums">0.098</td>
                  <td className="mono-nums">0.98 s</td>
                  <td className="mono-nums">1.02 GB</td>
                </tr>
                <tr>
                  <td><strong>FC-Siam-diff (Baseline)</strong></td>
                  <td>Early Concat</td>
                  <td className="mono-nums">0.764</td>
                  <td className="mono-nums">0.619</td>
                  <td className="mono-nums">0.782</td>
                  <td className="mono-nums">0.748</td>
                  <td className="mono-nums">0.134</td>
                  <td className="mono-nums">0.82 s</td>
                  <td className="mono-nums">0.91 GB</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
