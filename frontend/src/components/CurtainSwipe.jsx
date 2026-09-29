import React, { useState, useRef, useCallback } from 'react';
import { Icon } from './Icons';

export const CurtainSwipe = ({
  bgImg,
  fgImg,
  leftLabel = "Time 1 (Pre-Change)",
  rightLabel = "Time 2 (Post-Change)"
}) => {
  const [sliderPos, setSliderPos] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);

  const handleMove = useCallback((clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
    const percent = Math.max(0, Math.min((x / rect.width) * 100, 100));
    setSliderPos(percent);
  }, []);

  const handleMouseDown = () => setIsDragging(true);
  const handleMouseUp = () => setIsDragging(false);

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    handleMove(e.clientX);
  };

  const handleTouchMove = (e) => {
    if (e.touches && e.touches[0]) {
      handleMove(e.touches[0].clientX);
    }
  };

  return (
    <div
      ref={containerRef}
      className="curtain-swipe-box"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleMouseUp}
    >
      {/* Background Layer (Revealed on the Right) */}
      <div className="curtain-layer">
        {bgImg ? (
          <img src={bgImg} alt={rightLabel} draggable={false} />
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            [AWAITING POST-EVENT SENSOR PASS (T2)]
          </div>
        )}
      </div>

      {/* Foreground Layer (Clipped to sliderPos on the Left) */}
      <div
        className="curtain-layer curtain-layer-top"
        style={{ width: `${sliderPos}%` }}
      >
        {fgImg ? (
          <img
            src={fgImg}
            alt={leftLabel}
            draggable={false}
            style={{
              width: containerRef.current ? `${containerRef.current.clientWidth}px` : '100%',
              maxWidth: 'none'
            }}
          />
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            [AWAITING PRE-EVENT SENSOR PASS (T1)]
          </div>
        )}
      </div>

      {/* Interactive Divider Line */}
      <div
        className="curtain-divider"
        style={{ left: `${sliderPos}%` }}
        onMouseDown={handleMouseDown}
        onTouchStart={handleMouseDown}
      >
        <div className="curtain-handle">
          <Icon name="split" size={12} />
        </div>
      </div>

      {/* Labels */}
      <div className="curtain-label curtain-label-left">
        {leftLabel}
      </div>
      <div className="curtain-label curtain-label-right">
        {rightLabel}
      </div>
    </div>
  );
};
