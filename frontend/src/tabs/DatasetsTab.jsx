import React from 'react';

export const DatasetsTab = () => {
  const datasets = [
    {
      name: 'LEVIR-CD',
      sensor: 'Google Earth VHR',
      resolution: '0.5m GSD',
      dimensions: '1024x1024',
      pairs: '637 pairs',
      size: '2.30 GB',
      splits: 'Train: 445, Val: 64, Test: 128',
      type: 'Bitemporal Building Emergence'
    },
    {
      name: 'LEVIR-CD+',
      sensor: 'Google Earth VHR',
      resolution: '0.5m GSD',
      dimensions: '1024x1024',
      pairs: '985 pairs',
      size: '3.53 GB',
      splits: 'Train: 637, Test: 348',
      type: 'Multi-season Complex Buildings'
    },
    {
      name: 'WHU-CD',
      sensor: 'Aerial Orthophoto (NZ)',
      resolution: '0.2m GSD',
      dimensions: '512x512 & Mosaics',
      pairs: '1,950 pairs',
      size: '7.10 GB',
      splits: 'Train: 1260, Test: 690',
      type: 'High-Precision Aerial Reconstruction'
    },
    {
      name: 'S2Looking',
      sensor: 'GaoFen / SuperView-1',
      resolution: '0.5–0.8m GSD',
      dimensions: '1024x1024',
      pairs: '3,918 pairs',
      size: '8.64 GB',
      splits: 'Train: 2918, Test: 1000',
      type: 'Off-Nadir Side-Looking Surveillance'
    },
    {
      name: 'SYSU-CD',
      sensor: 'Aerial Optical RGB',
      resolution: '0.5m GSD',
      dimensions: '256x256',
      pairs: '12,000 pairs',
      size: '3.25 GB',
      splits: 'Official 12k Benchmark Set',
      type: 'Dense Urban & Vegetation Classes'
    }
  ];

  return (
    <div className="view-body">
      <div className="c2-card">
        <div className="c2-card-header">
          <span>FIVE BENCHMARK SATELLITE DATASET REPOSITORIES</span>
          <span className="c2-badge badge-cyan">AIR-GAPPED STORAGE VERIFIED</span>
        </div>
        <div className="c2-card-body">
          <div className="c2-table-wrapper">
            <table className="c2-table">
              <thead>
                <tr>
                  <th>Dataset Corpus</th>
                  <th>Sensor / Platform</th>
                  <th>Optical Resolution</th>
                  <th>Tile Dimensions</th>
                  <th>Image Pairs</th>
                  <th>Storage Footprint</th>
                  <th>Operational Focus</th>
                  <th>Train / Test Partition</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map((d, i) => (
                  <tr key={i}>
                    <td><strong style={{ color: 'var(--c2-cyan)' }}>{d.name}</strong></td>
                    <td>{d.sensor}</td>
                    <td className="mono-nums">{d.resolution}</td>
                    <td className="mono-nums">{d.dimensions}</td>
                    <td className="mono-nums">{d.pairs}</td>
                    <td className="mono-nums">{d.size}</td>
                    <td>{d.type}</td>
                    <td style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{d.splits}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
