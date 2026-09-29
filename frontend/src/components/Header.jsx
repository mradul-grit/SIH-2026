import React, { useState, useEffect } from 'react';
import { Icon } from './Icons';

export const Header = () => {
  const [utcTime, setUtcTime] = useState('');
  const [telemetry, setTelemetry] = useState({
    device: 'NVIDIA RTX 3050 (4 GB)',
    cuda: true,
    latency: '18.4 ms',
    gsd: '0.5m GSD'
  });

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);

    // Probe backend health for live telemetry
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        if (data.device) {
          setTelemetry(prev => ({
            ...prev,
            device: data.device.includes('RTX') ? 'RTX 3050 (4 GB)' : data.device,
            cuda: data.cuda_available
          }));
        }
      })
      .catch(() => {});

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* Top Defense Classification Banner */}
      <div className="security-banner">
        <div>RESTRICTED // AIR-GAPPED C2 // NOFORN</div>
        <div className="security-banner-center">
          <span style={{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }}></span>
          <span>AIR-GAP SECURED // LOCAL EDGE RUNTIME // ZERO CLOUD DEPENDENCY</span>
        </div>
        <div className="security-banner-right mono-nums">{utcTime}</div>
      </div>

      {/* Main Operational C2 Header */}
      <header className="app-header">
        <div className="app-brand">
          <div className="app-logo-badge">SIH-227</div>
          <div className="app-title-group">
            <div className="app-title-main">
              <span>GEOINT RECONNAISSANCE &amp; CHANGE DETECTION C2</span>
              <span className="c2-badge badge-cyan">AIR-GAP v2.4</span>
            </div>
            <div className="app-title-sub">
              DEFENSE SATELLITE RETRIEVAL &amp; STRUCTURAL MONITORING CONSOLE
            </div>
          </div>
        </div>

        {/* Live Hardware & Edge Telemetry */}
        <div className="header-telemetry-cluster">
          <div className="telemetry-node">
            <div className="status-dot"></div>
            <span className="label">ENGINE:</span>
            <span className="val">ACTIVE</span>
          </div>

          <div className="telemetry-node">
            <span className="label">EDGE ACCELERATOR:</span>
            <span className="val">{telemetry.device}</span>
          </div>

          <div className="telemetry-node">
            <span className="label">SENSOR GSD:</span>
            <span className="val">{telemetry.gsd}</span>
          </div>

          <div className="telemetry-node">
            <span className="label">P95 RETRIEVAL:</span>
            <span className="val mono-nums">{telemetry.latency}</span>
          </div>
        </div>
      </header>
    </>
  );
};
