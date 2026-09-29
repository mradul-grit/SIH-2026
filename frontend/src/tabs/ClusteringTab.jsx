import React, { useState, useEffect } from 'react';
import { Icon } from '../components/Icons';

export const ClusteringTab = () => {
  const [clusterData, setClusterData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [hoveredPoint, setHoveredPoint] = useState(null);

  const fetchClusters = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/clusters');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setClusterData(data);
    } catch (err) {
      alert('Error fetching clusters: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, []);

  const points = clusterData?.coordinates_2d || [];
  const labels = clusterData?.cluster_labels || [];
  const meta = clusterData?.metadata || [];

  // Color palette for clusters
  const clusterColors = [
    '#00e5ff', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#3b82f6', '#14b8a6'
  ];

  // Map 2D coords to SVG coordinate space
  const minX = points.length ? Math.min(...points.map(p => p[0])) : -5;
  const maxX = points.length ? Math.max(...points.map(p => p[0])) : 5;
  const minY = points.length ? Math.min(...points.map(p => p[1])) : -5;
  const maxY = points.length ? Math.max(...points.map(p => p[1])) : 5;

  const toSvgX = (x) => ((x - minX) / (maxX - minX || 1)) * 640 + 30;
  const toSvgY = (y) => ((y - minY) / (maxY - minY || 1)) * 360 + 20;

  return (
    <div className="view-body">
      {/* Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
        <div className="c2-card">
          <div className="c2-card-header">
            <span>DISCOVERED THEMATIC CLUSTERS</span>
            <span className="c2-badge badge-cyan">HDBSCAN</span>
          </div>
          <div className="c2-card-body">
            <div style={{ fontSize: '22px', fontWeight: 800, color: 'var(--c2-cyan)', fontFamily: 'var(--font-mono)' }}>
              {clusterData?.num_clusters ?? '--'} Discrete Themes
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
              Unsupervised clustering on 512-dim RemoteCLIP embeddings.
            </div>
          </div>
        </div>

        <div className="c2-card">
          <div className="c2-card-header">
            <span>UNCLUSTERED ANOMALIES (NOISE)</span>
            <span className="c2-badge badge-amber">OUTLIERS</span>
          </div>
          <div className="c2-card-body">
            <div style={{ fontSize: '22px', fontWeight: 800, color: 'var(--c2-amber)', fontFamily: 'var(--font-mono)' }}>
              {clusterData?.noise_points ?? '--'} Points
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
              Isolated spatial patterns differing from prevailing clusters.
            </div>
          </div>
        </div>

        <div className="c2-card">
          <div className="c2-card-header">
            <span>TOTAL EMBEDDINGS ANALYZED</span>
            <span className="c2-badge badge-emerald">PROCESSED</span>
          </div>
          <div className="c2-card-body">
            <div style={{ fontSize: '22px', fontWeight: 800, color: '#10b981', fontFamily: 'var(--font-mono)' }}>
              {points.length} Tiles
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
              LEVIR-CD &amp; WHU-CD multimodal validation catalog.
            </div>
          </div>
        </div>
      </div>

      {/* 2D Projection Scatter Map */}
      <div className="c2-card">
        <div className="c2-card-header">
          <span>UMAP 2D LATENT PROJECTION MAP</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="c2-btn c2-btn-secondary" style={{ padding: '2px 8px', fontSize: '10px' }} onClick={fetchClusters}>
              Recompute
            </button>
          </div>
        </div>
        <div className="c2-card-body" style={{ position: 'relative' }}>
          {isLoading ? (
            <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--c2-cyan)', fontFamily: 'var(--font-mono)' }}>
              Computing UMAP projection &amp; HDBSCAN density clustering...
            </div>
          ) : (
            <div style={{ position: 'relative', width: '100%', height: '400px', background: '#02050a', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <svg width="100%" height="100%" viewBox="0 0 700 400">
                {/* Subtle grid lines */}
                <line x1="30" y1="200" x2="670" y2="200" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
                <line x1="350" y1="20" x2="350" y2="380" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />

                {points.map((pt, i) => {
                  const clusterId = labels[i];
                  const isNoise = clusterId === -1;
                  const color = isNoise ? '#64748b' : clusterColors[clusterId % clusterColors.length];
                  const cx = toSvgX(pt[0]);
                  const cy = toSvgY(pt[1]);

                  const isFiltered = selectedCluster !== null && selectedCluster !== clusterId;

                  return (
                    <circle
                      key={i}
                      cx={cx}
                      cy={cy}
                      r={isNoise ? 3 : 4.5}
                      fill={color}
                      opacity={isFiltered ? 0.15 : 0.85}
                      style={{ cursor: 'pointer', transition: 'all 0.1s ease' }}
                      onMouseEnter={() => setHoveredPoint({ ...meta[i], clusterId, x: pt[0], y: pt[1] })}
                      onMouseLeave={() => setHoveredPoint(null)}
                    />
                  );
                })}
              </svg>

              {/* Hover Tooltip */}
              {hoveredPoint && (
                <div
                  style={{
                    position: 'absolute',
                    top: '12px',
                    right: '12px',
                    background: 'rgba(9, 14, 23, 0.95)',
                    border: '1px solid var(--c2-cyan)',
                    padding: '8px 12px',
                    borderRadius: '3px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: '#fff',
                    pointerEvents: 'none'
                  }}
                >
                  <div style={{ color: 'var(--c2-cyan)', fontWeight: 700 }}>{hoveredPoint.tile_id}</div>
                  <div>Dataset: {hoveredPoint.dataset_name || 'LEVIR-CD'}</div>
                  <div>Cluster: {hoveredPoint.clusterId === -1 ? 'Noise (Outlier)' : `Cluster #${hoveredPoint.clusterId}`}</div>
                  <div style={{ color: 'var(--text-muted)' }}>Lat/Lon: {hoveredPoint.latitude?.toFixed(4)}, {hoveredPoint.longitude?.toFixed(4)}</div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
