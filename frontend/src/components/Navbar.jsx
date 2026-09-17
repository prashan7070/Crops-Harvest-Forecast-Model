import React from 'react';
import { Sprout, BarChart3, Cpu, Sparkles, Activity, Layers } from 'lucide-react';

export default function Navbar({ backendStatus }) {

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      background: 'var(--bg-card)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid var(--border-glass)',
      padding: '0.85rem 0'
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, hsl(154, 75%, 48%) 0%, hsl(192, 85%, 52%) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 16px var(--primary-glow)'
          }}>
            <Sprout size={24} color="#0b1329" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '1.25rem',
                fontWeight: 800,
                letterSpacing: '-0.02em',
                background: 'linear-gradient(90deg, var(--text-primary) 40%, var(--primary-emerald) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                CropForecast<span style={{ color: 'var(--primary-emerald)' }}>LK</span>
              </span>
              <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>v1.0.0</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '-2px' }}>
              Sri Lanka Highland Agricultural Intelligence
            </p>
          </div>
        </div>


        {/* Status Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.35rem 0.8rem',
            borderRadius: 'var(--radius-full)',
            background: 'var(--bg-glass-subtle)',
            border: '1px solid var(--border-glass)',
            fontSize: '0.78rem'
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: backendStatus?.status === 'online' ? 'var(--primary-emerald)' : 'var(--accent-amber)',
              boxShadow: backendStatus?.status === 'online' ? '0 0 10px var(--primary-emerald)' : 'none',
              animation: 'pulseGlow 2s infinite'
            }} />
            <span style={{ color: 'var(--text-secondary)' }}>
              {backendStatus?.status === 'online' ? 'FastAPI In-RAM Engine' : 'Offline / Standalone'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
