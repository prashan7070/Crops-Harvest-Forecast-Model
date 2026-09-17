import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import PredictorCard from './components/PredictorCard';
import AnalyticsChart from './components/AnalyticsChart';
import AllCropsPredictor from './components/AllCropsPredictor';
import { checkBackendHealth, fetchDistricts, fetchModelStats } from './services/api';
import { Sprout, CloudRain, SunMedium, Compass, ShieldCheck, GitBranch } from 'lucide-react';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [backendStatus, setBackendStatus] = useState({ status: 'online' });
  const [districts, setDistricts] = useState([
    'Nuwara Eliya', 'Badulla', 'Kandy', 'Matale', 'Moneragala',
    'Anuradhapura', 'Kurunegala', 'Hambantota', 'Ratnapura', 'Jaffna'
  ]);
  const [currentDistrict, setCurrentDistrict] = useState('Nuwara Eliya');
  const [modelStats, setModelStats] = useState(null);

  useEffect(() => {
    async function init() {
      const health = await checkBackendHealth();
      setBackendStatus(health);

      const dData = await fetchDistricts();
      if (dData && dData.districts) {
        setDistricts(dData.districts);
      }

      const mData = await fetchModelStats();
      if (mData) {
        setModelStats(mData);
      }
    }
    init();
  }, []);

  const handleSelectDistrict = (districtName) => {
    setCurrentDistrict(districtName);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Glass Navbar */}
      <Navbar
        backendStatus={backendStatus}
      />

      {/* Main Content Area */}
      <main className="container" style={{ flex: 1, padding: '2rem 1.5rem' }}>
        {/* Hero Header Banner */}
        <section style={{
          marginBottom: '2rem',
          padding: '2.25rem',
          borderRadius: 'var(--radius-lg)',
          background: 'linear-gradient(135deg, hsla(150, 60%, 92%, 0.8) 0%, hsla(154, 75%, 85%, 0.4) 50%, hsla(192, 85%, 90%, 0.4) 100%)',
          border: '1px solid var(--border-glass)',
          boxShadow: 'var(--shadow-card)',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{ maxWidth: '820px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.6rem', flexWrap: 'wrap' }}>
              <span className="badge badge-emerald">Sri Lanka Agricultural Intelligence</span>
              <span className="badge badge-cyan">Maha & Yala Dual Monsoon Regimes</span>
              <span className="badge badge-amber">Department of Census & Statistics</span>
            </div>

            <h1 style={{
              fontSize: '2.5rem',
              fontWeight: 800,
              lineHeight: 1.15,
              marginBottom: '0.75rem',
              letterSpacing: '-0.03em',
              background: 'linear-gradient(120deg, var(--text-primary) 40%, hsl(154, 75%, 35%) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Highland Crop Production & Yield Forecasting
            </h1>

            <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '1.25rem' }}>
              An end-to-end Machine Learning intelligence platform forecasting seasonal crop yields across
              Nuwara Eliya, Badulla, Kandy, Matale, and Moneragala using 23 years (2000–2023) of empirical census records.
            </p>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-cyan)' }}>
                <CloudRain size={16} />
                <span>Maha Season (North-East Monsoon)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-amber)' }}>
                <SunMedium size={16} />
                <span>Yala Season (South-West Monsoon)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary-emerald)' }}>
                <ShieldCheck size={16} />
                <span>Sub-20ms Low-Latency Model Inference</span>
              </div>
            </div>

            <div style={{ marginTop: '2rem' }}>
              <button 
                onClick={() => setCurrentPage('all-crops')}
                className="btn btn-primary"
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                  padding: '0.75rem 1.5rem', fontSize: '0.95rem', fontWeight: 600,
                  borderRadius: 'var(--radius-full)'
                }}
              >
                View All Crops Harvest Predictions
              </button>
            </div>
          </div>
        </section>

        {/* Dynamic View Rendering */}
        {currentPage === 'all-crops' ? (
            <div className="animate-fade-in">
              <AllCropsPredictor onBack={() => setCurrentPage('dashboard')} />
            </div>
        ) : (
            <div className="animate-fade-in" style={{ display: 'grid', gap: '2rem' }}>
              <PredictorCard districts={districts} />
              <AnalyticsChart districts={districts} />
            </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        marginTop: 'auto',
        borderTop: '1px solid var(--border-glass)',
        background: 'var(--bg-glass-subtle)',
        padding: '2rem 0',
        fontSize: '0.82rem',
        color: 'var(--text-muted)'
      }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)', fontWeight: 600 }}>
              <Sprout size={16} color="var(--primary-emerald)" />
              <span>CropForecastLK Monorepo System</span>
            </div>
            <p style={{ marginTop: '0.25rem' }}>
              Academic Module: Machine Learning Development & Full-Stack Application | Monorepo Delivery
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span className="badge badge-emerald">Git Branch: main</span>
            <span className="badge badge-cyan">FastAPI + React 18</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
