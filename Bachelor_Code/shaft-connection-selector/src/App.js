import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

const pretty = (n, digits = 0) =>
  typeof n === 'number' ? n.toLocaleString(undefined, { maximumFractionDigits: digits }) : n;

function App() {
  const [formData, setFormData] = useState({
    shaft_diameter: 30,
    hub_length: 30,
    shaft_material: 'Steel C45',
    hub_material: 'Steel C45', // locked to shaft_material
    shaft_type: 'solid',
    has_bending: true,
    required_torque: 50000, // REQUIRED now
    safety_factor: 1.5,
    hub_outer_diameter: '',
    shaft_inner_diameter: '',
    mu_override: '',
    user_preferences: {
      ease: 0.5,
      movement: 0.5,
      cost: 0.5,
      bidirectional: 0.5
    }
  });

  const [autoLength, setAutoLength] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lengthRecommendation, setLengthRecommendation] = useState('D (equal to shaft diameter)');

  // --- Keep hub material locked to the shaft material ---
  useEffect(() => {
    setFormData(prev => ({ ...prev, hub_material: prev.shaft_material }));
  }, [formData.shaft_material]);

  // --- Bending hint: auto-apply until user overrides hub_length once ---
  useEffect(() => {
    const recommendationText = formData.has_bending ? 'D (equal to shaft diameter)' : '0.5D (half shaft diameter)';
    setLengthRecommendation(recommendationText);

    if (autoLength) {
      const Lrec = formData.has_bending
        ? Math.round(formData.shaft_diameter)
        : Math.round(formData.shaft_diameter * 0.5);
      setFormData(prev => ({ ...prev, hub_length: Lrec }));
    }
  }, [formData.has_bending, formData.shaft_diameter, autoLength]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (name.startsWith('pref_')) {
      const prefName = name.replace('pref_', '');
      setFormData(prev => ({
        ...prev,
        user_preferences: {
          ...prev.user_preferences,
          [prefName]: parseFloat(value)
        }
      }));
    } else if (name === 'shaft_diameter') {
      const newShaftDiameter = Math.max(1, Math.round(parseFloat(value || 0)));
      setFormData(prev => ({ ...prev, shaft_diameter: newShaftDiameter }));
    } else if (name === 'has_bending') {
      setFormData(prev => ({ ...prev, has_bending: checked }));
    } else if (name === 'hub_length') {
      const newHubLength = Math.max(1, Math.round(parseFloat(value || 0)));
      setAutoLength(false); // user override
      setFormData(prev => ({ ...prev, hub_length: newHubLength }));
    } else if (name === 'required_torque') {
      const val = value === '' ? '' : Math.max(1, parseFloat(value));
      setFormData(prev => ({ ...prev, required_torque: val }));
    } else if (name === 'hub_outer_diameter' || name === 'shaft_inner_diameter' || name === 'safety_factor' || name === 'mu_override') {
      setFormData(prev => ({
        ...prev,
        [name]: value === '' ? '' : parseFloat(value)
      }));
    } else if (name === 'shaft_material') {
      setFormData(prev => ({ ...prev, shaft_material: value, hub_material: value }));
    } else {
      setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const requestData = {
        ...formData,
        // Backend expects numbers or nulls for optional geometry
        hub_outer_diameter: formData.hub_outer_diameter === '' ? null : formData.hub_outer_diameter,
        shaft_inner_diameter: formData.shaft_inner_diameter === '' ? null : formData.shaft_inner_diameter,
        // hub_material locked by effect; send as-is
      };

      const response = await axios.post(`${API_BASE}/select-connection`, requestData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const PreferenceSlider = ({ name, label, value }) => (
    <div className="pref">
      <div className="pref-top">
        <label htmlFor={`pref_${name}`}>{label}</label>
        <span className="pref-value">{value.toFixed(2)}</span>
      </div>
      <input
        type="range"
        id={`pref_${name}`}
        name={`pref_${name}`}
        min="0"
        max="1"
        step="0.1"
        value={value}
        onChange={handleInputChange}
        className="slider"
      />
      <div className="slider-labels"><span>Low</span><span>High</span></div>
    </div>
  );

  const StatCard = ({ title, value, sub, tone }) => (
    <div className={`card stat ${tone || ''}`}>
      <div className="stat-title">{title}</div>
      <div className="stat-value">{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );

  const CapacityBar = ({ label, value, req, highlight }) => {
    const pct = Math.max(0, Math.min(1, req > 0 ? value / req : 0));
    const pctText = (pct * 100).toFixed(0) + '%';
    const over = value - req;
    const margin = req > 0 ? ((over) / req) * 100 : 0;
    const tone = highlight ? 'bar-highlight' : '';
    return (
      <div className={`cap-row ${tone}`}>
        <div className="cap-meta">
          <span className="cap-label">{label}</span>
          <span className={`badge ${value >= req ? 'ok' : 'fail'}`}>{value >= req ? 'feasible' : 'insufficient'}</span>
        </div>
        <div className="bar">
          <div className="fill" style={{ width: `${Math.min(100, pct * 100)}%` }} />
        </div>
        <div className="cap-values">
          <span>{pretty(Math.round(value))} Nmm</span>
          <span className={value >= req ? 'pos' : 'neg'}>
            {value >= req ? `+${margin.toFixed(1)}%` : `${margin.toFixed(1)}%`}
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Shaft–Hub Connection Selector</h1>
        <p className="subtitle">Pick the optimal connection based on torque, geometry, and your preferences.</p>
      </header>

      <div className="container">
        <form onSubmit={handleSubmit} className="grid">
          {/* Left column: inputs */}
          <div className="panel">
            <h2>Basic Parameters</h2>
            <div className="grid2">
              <div className="form-group">
                <label htmlFor="shaft_diameter">Shaft Diameter (mm)</label>
                <input
                  type="number"
                  id="shaft_diameter"
                  name="shaft_diameter"
                  value={formData.shaft_diameter}
                  onChange={handleInputChange}
                  min="1"
                  step="1"
                  required
                />
                <small>Whole numbers recommended.</small>
              </div>

              <div className="form-group">
                <label htmlFor="hub_length">
                  Hub Length (mm){' '}
                  <span className="hint">Recommended: {lengthRecommendation}</span>
                </label>
                <input
                  type="number"
                  id="hub_length"
                  name="hub_length"
                  value={formData.hub_length}
                  onChange={handleInputChange}
                  min="1"
                  step="1"
                  required
                />
                <small>
                  We’ll auto-apply the bending hint ({formData.has_bending ? 'L = D' : 'L = 0.5D'}) until you edit this once.
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="shaft_material">Material (shaft & hub)</label>
                <select
                  id="shaft_material"
                  name="shaft_material"
                  value={formData.shaft_material}
                  onChange={handleInputChange}
                >
                  <option value="Steel C45">Steel C45</option>
                  <option value="Aluminum 6061">Aluminum 6061</option>
                </select>
                <small>Hub material is locked to match the shaft.</small>
              </div>

              <div className="form-group">
                <label htmlFor="shaft_type">Shaft Type</label>
                <select
                  id="shaft_type"
                  name="shaft_type"
                  value={formData.shaft_type}
                  onChange={handleInputChange}
                >
                  <option value="solid">Solid</option>
                  <option value="hollow">Hollow</option>
                </select>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="has_bending"
                    checked={formData.has_bending}
                    onChange={handleInputChange}
                  />
                  Bending Moments Present
                  <span className="hint-inline">
                    ({formData.has_bending ? 'L = D recommended' : 'L = 0.5D recommended'})
                  </span>
                </label>
              </div>
            </div>

            <h2>User Preferences</h2>
            <div className="prefs">
              <PreferenceSlider name="ease" label="Ease of Assembly / Disassembly" value={formData.user_preferences.ease} />
              <PreferenceSlider name="movement" label="Frequent Movement Needed" value={formData.user_preferences.movement} />
              <PreferenceSlider name="cost" label="Cost Sensitivity (Affordability)" value={formData.user_preferences.cost} />
              <PreferenceSlider name="bidirectional" label="Bidirectional Torque" value={formData.user_preferences.bidirectional} />
            </div>

            <h2>Advanced (Decision-Critical)</h2>
            <div className="grid2">
              <div className="form-group">
                <label htmlFor="required_torque">Required Torque (Nmm) <span className="badge req">Required</span></label>
                <input
                  type="number"
                  id="required_torque"
                  name="required_torque"
                  value={formData.required_torque}
                  onChange={handleInputChange}
                  min="1"
                  step="100"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="safety_factor">Safety Factor (≥ 1.0)</label>
                <input
                  type="number"
                  id="safety_factor"
                  name="safety_factor"
                  value={formData.safety_factor}
                  onChange={handleInputChange}
                  min="1.0"
                  step="0.1"
                />
              </div>

              {formData.shaft_type === 'hollow' && (
                <div className="form-group">
                  <label htmlFor="shaft_inner_diameter">Shaft Inner Diameter (mm)</label>
                  <input
                    type="number"
                    id="shaft_inner_diameter"
                    name="shaft_inner_diameter"
                    value={formData.shaft_inner_diameter}
                    onChange={handleInputChange}
                    min="1"
                    step="1"
                    required
                  />
                  <small>Must be &lt; shaft diameter.</small>
                </div>
              )}

              <div className="form-group">
                <label htmlFor="hub_outer_diameter">Hub Outer Diameter (mm)</label>
                <input
                  type="number"
                  id="hub_outer_diameter"
                  name="hub_outer_diameter"
                  value={formData.hub_outer_diameter}
                  onChange={handleInputChange}
                  placeholder="Auto: 2×D if empty"
                  step="1"
                />
                <small>Must be &gt; shaft diameter.</small>
              </div>

              <div className="form-group">
                <label htmlFor="mu_override">Friction Coefficient (μ) Override</label>
                <input
                  type="number"
                  id="mu_override"
                  name="mu_override"
                  value={formData.mu_override}
                  onChange={handleInputChange}
                  placeholder="Auto if empty"
                  min="0.05"
                  max="0.5"
                  step="0.01"
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Calculating…' : 'Find Optimal Connection'}
            </button>
            {!!error && <div className="error-banner">{error}</div>}
          </div>

          {/* Right column: results */}
          <div className="panel">
            <h2>Results</h2>
            {!result && (
              <div className="empty">
                <p>Fill the form and click <strong>Find Optimal Connection</strong>.</p>
                <p className="muted">We’ll show feasibility, margins, and the recommended connection here.</p>
              </div>
            )}

            {result && (
              <>
                <div className={`recommend card ${result.recommended_connection}`}>
                  <div className="rec-top">
                    <span className="pill">Recommended</span>
                    <h3 className="rec-title">{result.recommended_connection?.toUpperCase()}</h3>
                  </div>

                  <div className="rec-grid">
                    <StatCard
                      title="Required Torque"
                      value={`${pretty(result.required_torque_Nmm)} Nmm`}
                      sub="From your input"
                      tone="primary"
                    />
                    <StatCard
                      title="μ Used"
                      value={typeof result.mu_used === 'number' ? result.mu_used.toFixed(2) : String(result.mu_used)}
                      sub="Auto or override"
                      tone="neutral"
                    />
                    <StatCard
                      title="Feasible Options"
                      value={Object.entries(result.capacities_Nmm).filter(([_, v]) => v >= result.required_torque_Nmm).length}
                      sub="≥ required torque"
                      tone="neutral"
                    />
                  </div>

                  <div className="caps">
                    <h4>Torque Capacities</h4>
                    {Object.entries(result.capacities_Nmm).map(([type, capacity]) => (
                      <CapacityBar
                        key={type}
                        label={type.toUpperCase()}
                        value={capacity}
                        req={result.required_torque_Nmm}
                        highlight={type === result.recommended_connection}
                      />
                    ))}
                  </div>

                  {result.scores && Object.keys(result.scores).length > 0 && (
                    <div className="scores-block">
                      <h4>Selection Scores (feasible only)</h4>
                      <div className="scores-grid">
                        {Object.entries(result.scores).map(([type, score]) => (
                          <div key={type} className={`chip ${type === result.recommended_connection ? 'chip-active' : ''}`}>
                            <span className="chip-label">{type}</span>
                            <span className="chip-value">{Number(score).toFixed(3)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="details card">
                  <h4>Detail Snapshot</h4>
                  <pre className="json">{JSON.stringify(result.details, null, 2)}</pre>
                </div>
              </>
            )}
          </div>
        </form>
      </div>

      <footer className="footer">
        <span>Materials locked: Shaft = Hub (changeable later). Backend WIP.</span>
      </footer>
    </div>
  );
}

export default App;
