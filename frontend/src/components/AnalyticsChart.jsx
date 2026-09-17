import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';
import { BarChart2, Filter, RefreshCw } from 'lucide-react';
import { fetchHistoricalTrends } from '../services/api';

export default function AnalyticsChart({ districts = [] }) {
  const [selectedDistrict, setSelectedDistrict] = useState('Nuwara Eliya');
  const [selectedCrop, setSelectedCrop] = useState('Potato');
  const [seasonFilter, setSeasonFilter] = useState('All');
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);

  const availableCrops = ['Potato', 'Maize', 'Kurakkan', 'Chili', 'Cassava', 'Sweet Potato', 'Green Gram'];

  useEffect(() => {
    loadTrends();
  }, [selectedDistrict, selectedCrop]);

  const loadTrends = async () => {
    setLoading(true);
    try {
      const res = await fetchHistoricalTrends(selectedDistrict, selectedCrop);
      if (res && res.data) {
        setChartData(res.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredData = chartData.filter((item) => {
    if (seasonFilter === 'All') return true;
    return item.season.toLowerCase() === seasonFilter.toLowerCase();
  });

  // Custom Glassmorphic Tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-glass)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.75rem 1rem',
          boxShadow: '0 8px 16px rgba(0,0,0,0.05)',
          fontSize: '0.9rem',
          color: 'var(--text-primary)'
        }}>
          <div style={{ fontWeight: 700, marginBottom: '0.35rem' }}>
            {item.year} — {item.season} Season
          </div>
          <div style={{ color: 'var(--primary-emerald)', marginBottom: '0.2rem' }}>
            Production: <strong>{item.production_mt?.toLocaleString()} MT</strong>
          </div>
          <div style={{ color: 'var(--accent-cyan)', marginBottom: '0.2rem' }}>
            Cultivated Extent: <strong>{item.extent_ha?.toLocaleString()} Ha</strong>
          </div>
          <div style={{ color: 'var(--accent-amber)' }}>
            Calculated Yield: <strong>{item.yield_mt_per_ha} MT/Ha</strong>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
      {/* Title & Controls Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '1.5rem'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <BarChart2 size={20} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Seasonal Agronomic Production Trajectory</h2>
            <span className="badge badge-cyan">2000 – 2023 DCS Records</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Comparative dual-axis visualization of cultivated land extent versus harvest yield across monsoons.
          </p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* District Select */}
          <select
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="input-control select-control"
            style={{ width: '170px', padding: '0.5rem 0.8rem', fontSize: '0.85rem' }}
          >
            {districts.map((d) => (
              <option key={d} value={d} style={{ color: 'var(--text-primary)' }}>{d}</option>
            ))}
          </select>

          {/* Crop Select */}
          <select
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="input-control select-control"
            style={{ width: '150px', padding: '0.5rem 0.8rem', fontSize: '0.85rem' }}
          >
            {availableCrops.map((c) => (
              <option key={c} value={c} style={{ color: 'var(--text-primary)' }}>{c}</option>
            ))}
          </select>

          {/* Season Toggle */}
          <div style={{
            display: 'flex',
            background: 'var(--bg-glass-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.25rem',
            border: '1px solid var(--border-glass)'
          }}>
            {['All', 'Maha', 'Yala'].map((s) => (
              <button
                key={s}
                onClick={() => setSeasonFilter(s)}
                style={{
                  padding: '0.35rem 0.65rem',
                  border: 'none',
                  background: seasonFilter === s ? 'var(--primary-emerald)' : 'transparent',
                  color: seasonFilter === s ? 'white' : 'var(--text-secondary)',
                  borderRadius: '4px',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {s}
              </button>
            ))}
          </div>

          <button
            onClick={loadTrends}
            className="btn btn-secondary"
            style={{ padding: '0.5rem', borderRadius: 'var(--radius-sm)' }}
            title="Refresh Data"
          >
            <RefreshCw size={15} />
          </button>
        </div>
      </div>

      {/* Chart Container */}
      <div style={{ width: '100%', height: '360px' }}>
        {loading ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
            Loading historical data...
          </div>
        ) : filteredData.length === 0 ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
            No historical records for {selectedCrop} in {selectedDistrict}.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={filteredData} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <defs>
                <linearGradient id="prodGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(154, 75%, 48%)" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="hsl(154, 75%, 48%)" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="var(--border-glass)" strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="year"
                stroke="var(--text-muted)"
                fontSize={12}
                tickLine={false}
              />
              <YAxis
                yAxisId="left"
                stroke="var(--primary-emerald)"
                fontSize={12}
                tickLine={false}
                tickFormatter={(val) => `${val >= 1000 ? (val/1000).toFixed(1) + 'k' : val}`}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="var(--accent-cyan)"
                fontSize={12}
                tickLine={false}
                tickFormatter={(val) => `${val} Ha`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                verticalAlign="top"
                align="right"
                wrapperStyle={{ paddingBottom: '1rem', fontSize: '0.82rem' }}
              />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="production_mt"
                name="Production (Metric Tons)"
                stroke="hsl(154, 75%, 48%)"
                strokeWidth={2.5}
                fill="url(#prodGradient)"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="extent_ha"
                name="Cultivated Extent (Hectares)"
                stroke="hsl(192, 85%, 52%)"
                strokeWidth={2}
                dot={{ fill: 'hsl(192, 85%, 52%)', r: 3 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.78rem',
        color: 'var(--text-muted)',
        marginTop: '0.5rem',
        paddingTop: '0.75rem',
        borderTop: '1px solid var(--border-glass)'
      }}>
        <span>Showing {filteredData.length} seasonal observation points</span>
        <span>Green Area: Production (MT) • Cyan Line: Cultivated Extent (Ha)</span>
      </div>
    </div>
  );
}
