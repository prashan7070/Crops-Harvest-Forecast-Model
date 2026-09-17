import React, { useState } from 'react';
import { Sparkles, Calculator, CheckCircle2, AlertCircle, ShieldCheck, Zap } from 'lucide-react';
import { predictCropHarvest } from '../services/api';

const HIGHLAND_CROPS = [
  { name: 'Potato', icon: '🥔' },
  { name: 'Maize', icon: '🌽' },
  { name: 'Kurakkan', icon: '🌾' },
  { name: 'Chili', icon: '🌶️' },
  { name: 'Cassava', icon: '🌿' },
  { name: 'Sweet Potato', icon: '🍠' },
  { name: 'Green Gram', icon: '🌱' },
];

export default function PredictorCard({ districts = [] }) {
  const [district, setDistrict] = useState('Nuwara Eliya');
  const [season, setSeason] = useState('Maha');
  const [crop, setCrop] = useState('Potato');
  const [extent, setExtent] = useState(250);
  const [year, setYear] = useState(2024);

  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handlePredict = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await predictCropHarvest({
        district,
        season,
        crop,
        extent_ha: parseFloat(extent),
        year: parseInt(year, 10)
      });
      setPrediction(res);
    } catch (err) {
      setError(err.message || 'Error computing forecast');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <Sparkles size={22} color="var(--primary-emerald)" />
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>Harvest Forecast Engine</h2>
      </div>

      <div className="grid-dashboard">
        <form onSubmit={handlePredict} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                District
              </label>
              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="input-control select-control"
              >
                {districts.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                Forecast Year
              </label>
              <select
                value={year}
                onChange={(e) => setYear(e.target.value)}
                className="input-control select-control"
              >
                {[2024, 2025, 2026, 2027].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Season
            </label>
            <div style={{
              display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem',
              background: 'var(--bg-glass-subtle)', padding: '0.4rem', borderRadius: 'var(--radius-md)'
            }}>
              <button
                type="button"
                onClick={() => setSeason('Maha')}
                style={{
                  padding: '0.75rem', borderRadius: 'var(--radius-sm)', border: 'none',
                  background: season === 'Maha' ? 'var(--accent-cyan)' : 'transparent',
                  color: season === 'Maha' ? 'white' : 'var(--text-secondary)',
                  fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s ease'
                }}
              >
                Maha (North-East)
              </button>
              <button
                type="button"
                onClick={() => setSeason('Yala')}
                style={{
                  padding: '0.75rem', borderRadius: 'var(--radius-sm)', border: 'none',
                  background: season === 'Yala' ? 'var(--accent-amber)' : 'transparent',
                  color: season === 'Yala' ? 'white' : 'var(--text-secondary)',
                  fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s ease'
                }}
              >
                Yala (South-West)
              </button>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Select Crop
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '0.5rem' }}>
              {HIGHLAND_CROPS.map((c) => {
                const isSelected = crop === c.name;
                return (
                  <button
                    key={c.name}
                    type="button"
                    onClick={() => setCrop(c.name)}
                    style={{
                      padding: '0.6rem', borderRadius: 'var(--radius-sm)',
                      background: isSelected ? 'var(--primary-emerald)' : 'var(--bg-glass-subtle)',
                      border: '1px solid', borderColor: isSelected ? 'var(--primary-emerald)' : 'var(--border-glass)',
                      color: isSelected ? 'white' : 'var(--text-primary)',
                      cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500
                    }}
                  >
                    <span>{c.icon}</span>
                    <span>{c.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
              <label style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                Cultivated Extent (Hectares)
              </label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <input
                  type="number" min="0" max="10000" step="any" value={extent}
                  onChange={(e) => setExtent(e.target.value)}
                  style={{
                    width: '100px', padding: '0.35rem 0.5rem',
                    background: 'var(--bg-card)', border: '1px solid var(--border-glass)',
                    borderRadius: '6px', color: 'var(--primary-emerald)',
                    fontWeight: 700, fontSize: '1rem', textAlign: 'right'
                  }}
                />
                <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Ha</span>
              </div>
            </div>
            <input
              type="range" min="10" max="2000" step="10" value={extent}
              onChange={(e) => setExtent(e.target.value)}
              style={{ width: '100%', accentColor: 'var(--primary-emerald)', cursor: 'pointer' }}
            />
          </div>

          <button
            type="submit" disabled={loading} className="btn btn-primary"
            style={{ width: '100%', padding: '1rem', fontSize: '1rem', marginTop: '0.5rem' }}
          >
            {loading ? 'Forecasting...' : <><Zap size={18} /><span>Calculate Forecast</span></>}
          </button>
        </form>

        <div style={{
          background: 'var(--bg-glass-subtle)',
          border: '1px solid var(--border-glass)',
          borderRadius: 'var(--radius-md)',
          padding: '2rem',
          display: 'flex', flexDirection: 'column',
          justifyContent: prediction ? 'flex-start' : 'center',
          alignItems: prediction ? 'stretch' : 'center',
          minHeight: '400px'
        }}>
          {error && (
            <div style={{ background: '#fee2e2', color: '#b91c1c', padding: '1rem', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <AlertCircle size={18} /><span>{error}</span>
            </div>
          )}

          {!prediction && !error && (
            <div style={{ textAlign: 'center' }}>
              <div style={{
                width: '70px', height: '70px', borderRadius: '50%', background: 'white',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 1.5rem auto', color: 'var(--primary-emerald)',
                boxShadow: '0 4px 10px rgba(0,0,0,0.05)'
              }}>
                <Calculator size={34} strokeWidth={1.8} />
              </div>
              <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Ready for Prediction</h3>
              <p style={{ color: 'var(--text-secondary)' }}>Enter the parameters and run the forecast model.</p>
            </div>
          )}

          {prediction && (
            <div className="animate-fade-in" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <CheckCircle2 color="var(--primary-emerald)" size={20} />
                <span style={{ fontWeight: 600, color: 'var(--primary-emerald)' }}>Forecast Successful</span>
              </div>
              
              <div style={{ background: 'white', padding: '1.5rem', borderRadius: 'var(--radius-md)', boxShadow: '0 4px 12px rgba(0,0,0,0.03)', border: '1px solid var(--border-glass)', marginBottom: '1.5rem' }}>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Predicted Production</div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                  <span style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {prediction.predicted_production_mt.toLocaleString()}
                  </span>
                  <span style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-muted)' }}>MT</span>
                </div>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: 'auto' }}>
                 <div style={{ background: 'white', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-glass)' }}>
                   <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Est. Yield</div>
                   <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>{prediction.predicted_yield_mt_per_ha} MT/Ha</div>
                 </div>
                 <div style={{ background: 'white', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-glass)' }}>
                   <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Season</div>
                   <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>{prediction.season} {prediction.forecast_year}</div>
                 </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
