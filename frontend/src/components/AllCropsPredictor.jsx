import React, { useState, useMemo, useEffect } from 'react';
import { Search, ChevronLeft, ShieldCheck, Zap, AlertCircle, CheckCircle2 } from 'lucide-react';
import { predictCropHarvest } from '../services/api';
import distCropMap from '../data/dist_crops.json';

const CROP_DATA = {
  "Cereals": ["Kurakkan", "Maize", "Sorghum", "Meneri"],
  "Fruits": ["Oranges", "Limes", "Mangoes", "Plantain", "Papaw", "Rambutan", "Avocado", "Melon", "Grapes", "Mngosteen", "Dragon Fruit", "Pine Apple", "Passion Fruit", "Kilo Pera", "Strawberry", "Durian"],
  "Leaves": ["Mukunuwenna", "Spinch", "Lettuce", "Thampala", "Gotukola", "Kankun", "Sarana", "Kathurumurunga", "Kohila Leave", "Cabbage Leaves"],
  "Low Country Vegetable": ["Luffa", "Bandakka", "Bitter Gourd", "Snake Gourd", "Cucumber", "Ash Pumpkin", "Red Pumpkin", "Ash Plantain", "Long Bean", "Egg Plant", "Winged Bean", "Vatana", "Gherkin", "Kekiri", "Drumstics", "Thumba Karavila", "Brinjals"],
  "Minor Export": ["Cinamon", "Cocoa", "Pepper", "Cardamoms", "Cloves", "Nutmeg", "Arecanut", "Cashew", "Coffee", "Betel"],
  "Oil Seeds": ["Gingelly", "Ground Nuts", "Musterd", "Soya Beans"],
  "Other": ["Chillies (Green)", "Cigar Tobacco", "Beedi/Chewing Tobacco"],
  "Other Perennial": ["Jak", "Bread Fruit", "Suger Cane"],
  "Pulses": ["Green Gram", "Cowpea", "Dhall", "Black Gram"],
  "Roots and Tubers": ["Manioc", "Sweet Potatoes", "Potatoes", "Red Onions", "Big Onions", "Ginger (Raw)", "Turmeric (Raw)", "Coco Yam", "Innala", "Kohila Yam"],
  "Up Country Vegetable": ["Tomatoes", "Cabbage", "Carrot", "Beetroot", "Raddish", "Leeks", "Capsicum", "Coli Flower", "Knolkhol", "Beans"]
};

const ALL_DISTRICTS = [
  "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya", 
  "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar", 
  "Vavuniya", "Mullaitivu", "Batticaloa", "Ampara", "Trincomalee", 
  "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla", 
  "Moneragala", "Ratnapura", "Kegalle"
].sort();

// Normalize UI district names to match the raw dataset spellings
const getDatasetDistrictKey = (d) => {
  const map = {
    "Hambantota": "Hanbantota",
    "Kalutara": "Kaluthara",
    "Moneragala": "Monaragala",
    "Mullaitivu": "Mullativu"
  };
  return map[d] || d;
};

export default function AllCropsPredictor({ onBack }) {
  const [district, setDistrict] = useState('Anuradhapura');
  const [season, setSeason] = useState('Maha');
  const [year, setYear] = useState(2025);
  const [extent, setExtent] = useState(100);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCrop, setSelectedCrop] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  // Auto-reset selected crop if user changes district and it becomes invalid
  useEffect(() => {
    if (selectedCrop) {
      const lookupKey = getDatasetDistrictKey(district);
      const validCrops = distCropMap[lookupKey] || [];
      if (!validCrops.includes(selectedCrop)) {
        setSelectedCrop('');
      }
    }
  }, [district, selectedCrop]);

  // Filter crops based on valid crops for district AND search query
  const filteredCropData = useMemo(() => {
    const lookupKey = getDatasetDistrictKey(district);
    const validCrops = distCropMap[lookupKey] || [];
    const query = searchQuery.toLowerCase();
    const filtered = {};
    
    Object.entries(CROP_DATA).forEach(([category, crops]) => {
      // First restrict strictly to physically valid crops in this district
      const availableCrops = crops.filter(c => validCrops.includes(c));
      if (availableCrops.length === 0) return;

      if (!searchQuery) {
        filtered[category] = availableCrops;
      } else if (category.toLowerCase().includes(query)) {
        filtered[category] = availableCrops;
      } else {
        const matchingCrops = availableCrops.filter(c => c.toLowerCase().includes(query));
        if (matchingCrops.length > 0) {
          filtered[category] = matchingCrops;
        }
      }
    });
    return filtered;
  }, [searchQuery, district]);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!selectedCrop) {
        setError('Please select a crop first.');
        return;
    }
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const res = await predictCropHarvest({
        district,
        season,
        crop: selectedCrop,
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
    <div className="container" style={{ padding: '2rem 1rem' }}>
      <button 
        onClick={onBack}
        style={{
          display: 'flex', alignItems: 'center', gap: '0.4rem', 
          background: 'transparent', border: '1px solid var(--border-glass)',
          padding: '0.5rem 1rem', borderRadius: 'var(--radius-sm)',
          cursor: 'pointer', fontWeight: 600, color: 'var(--text-secondary)',
          marginBottom: '1.5rem', transition: 'all 0.2s ease'
        }}
        onMouseOver={e => e.currentTarget.style.color = 'var(--primary-emerald)'}
        onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}
      >
        <ChevronLeft size={18} /> Back to Dashboard
      </button>

      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          Comprehensive Crop Forecasting
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Select from all 91 agricultural crops and all 25 districts to generate localized harvest predictions.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem', alignItems: 'start' }}>
        
        {/* Left Side: Crop Selector & Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-primary)' }}>1. Environmental Variables</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>District</label>
                <select value={district} onChange={(e) => setDistrict(e.target.value)} className="input-control select-control" style={{ width: '100%' }}>
                  {ALL_DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>Season</label>
                <select value={season} onChange={(e) => setSeason(e.target.value)} className="input-control select-control" style={{ width: '100%' }}>
                  <option value="Maha">Maha (North-East)</option>
                  <option value="Yala">Yala (South-West)</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>Forecast Year</label>
                <select value={year} onChange={(e) => setYear(e.target.value)} className="input-control select-control" style={{ width: '100%' }}>
                  {[2024, 2025, 2026, 2027, 2028].map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>Cultivated Extent (Ha)</label>
                <input type="number" min="0" step="any" value={extent} onChange={(e) => setExtent(e.target.value)} className="input-control" style={{ width: '100%' }} />
              </div>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '1.5rem', maxHeight: '600px', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>2. Select Crop</h3>
                <div style={{ position: 'relative', width: '250px' }}>
                    <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input 
                        type="text" 
                        placeholder="Search crops or categories..." 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="input-control"
                        style={{ width: '100%', paddingLeft: '2.2rem' }}
                    />
                </div>
            </div>

            {Object.keys(filteredCropData).length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No crops found matching "{searchQuery}"</div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {Object.entries(filteredCropData).map(([category, crops]) => (
                        <div key={category}>
                            <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary-emerald)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                                {category}
                            </h4>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                {crops.map(c => (
                                    <button
                                        key={c}
                                        onClick={() => setSelectedCrop(c)}
                                        style={{
                                            padding: '0.5rem 0.85rem',
                                            borderRadius: '20px',
                                            border: '1px solid',
                                            borderColor: selectedCrop === c ? 'var(--primary-emerald)' : 'var(--border-glass)',
                                            background: selectedCrop === c ? 'var(--primary-emerald)' : 'var(--bg-glass-subtle)',
                                            color: selectedCrop === c ? 'white' : 'var(--text-primary)',
                                            fontSize: '0.85rem', fontWeight: selectedCrop === c ? 600 : 500,
                                            cursor: 'pointer', transition: 'all 0.2s'
                                        }}
                                    >
                                        {c}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
          </div>
        </div>

        {/* Right Side: Prediction Output */}
        <div style={{ position: 'sticky', top: '100px' }}>
            <div className="glass-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0, borderBottom: '1px solid var(--border-glass)', paddingBottom: '1rem' }}>
                    Prediction Panel
                </h3>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Target Crop:</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 600, color: selectedCrop ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                        {selectedCrop || 'No crop selected...'}
                    </div>
                </div>
                
                <button
                    onClick={handlePredict}
                    disabled={loading || !selectedCrop}
                    className="btn btn-primary"
                    style={{ width: '100%', padding: '1rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}
                >
                    {loading ? 'Forecasting...' : <><Zap size={18} /><span>Calculate Global Forecast</span></>}
                </button>

                {error && (
                    <div style={{ background: '#fee2e2', color: '#b91c1c', padding: '1rem', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <AlertCircle size={18} /><span>{error}</span>
                    </div>
                )}

                {prediction && !error && (
                    <div className="animate-fade-in" style={{ background: 'var(--bg-glass-subtle)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)', padding: '1.5rem', marginTop: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                            <CheckCircle2 color="var(--primary-emerald)" size={20} />
                            <span style={{ fontWeight: 600, color: 'var(--primary-emerald)' }}>Forecast Successful</span>
                        </div>
                        
                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Predicted Production</div>
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '1.5rem' }}>
                            <span style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                                {prediction.predicted_production_mt.toLocaleString()}
                            </span>
                            <span style={{ fontWeight: 700, color: 'var(--text-muted)' }}>MT</span>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
                            <div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Est. Yield</div>
                                <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{prediction.predicted_yield_mt_per_ha} MT/Ha</div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Region</div>
                                <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{district}</div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>

      </div>
    </div>
  );
}
