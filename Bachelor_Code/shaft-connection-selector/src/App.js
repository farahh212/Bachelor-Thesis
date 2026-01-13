import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import './App.css';


// API base URL configuration
// In production: uses REACT_APP_API_URL environment variable (set in Vercel)
// In development: uses localhost:8000 for local backend
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';


const DIAMETER_MIN = 6;
const DIAMETER_MAX = 230;

const pretty = (n, digits = 0) =>
  typeof n === 'number' ? n.toLocaleString(undefined, { maximumFractionDigits: digits }) : n;

const DEFAULT_FORM = {
  shaft_diameter: 30,
  hub_length: 30,
  shaft_material: 'Steel C45',
  hub_material: 'Steel C45',
  shaft_type: 'solid',
  has_bending: true,
  required_torque: 50000,
  safety_factor: 1.5,
  hub_outer_diameter: '',
  shaft_inner_diameter: '',
  mu_override: '',
  spline_major_diameter_override: '',
  spline_tooth_count_override: '',
  surface_condition: 'dry',
  user_preferences: {
    ease: 0.5,
    movement: 0.5,
    cost: 0.5,
    bidirectional: 0.5,
    vibration: 0.5,
    speed: 0.5,
    maintenance: 0.5,
    durability: 0.5,
  },
};

const connectionNames = {
  press: 'Press',
  key: 'Key',
  spline: 'Spline',
};

const formatConnectionLabel = (value) => {
  if (!value && value !== 0) return 'N/A';
  const k = value.toString().toLowerCase();
  return connectionNames[k] ? connectionNames[k].toUpperCase() : value.toString().toUpperCase();
};

const formatMlLabel = (value) => {
  if (!value && value !== 0) return 'N/A';
  const k = value.toString().toLowerCase();
  return connectionNames[k] || value.toString().toUpperCase();
};

// ---- Components ----
const SectionHeader = ({ title, open, onToggle, subtitle }) => (
  <div className="section-head">
    <button type="button" className="section-toggle" onClick={onToggle}>
      <span className="section-title">{title}</span>
      <span className="section-icon" style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)' }}>
        {open ? '−' : '+'}
      </span>
    </button>
    {subtitle && <p className="section-subtitle">{subtitle}</p>}
  </div>
);

const PreferenceSlider = ({ name, label, value, onChange }) => {
  return (
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
        onChange={onChange}
        className="slider"
        style={{
          '--slider-percent': `${value * 100}%`,
          background: `linear-gradient(90deg, var(--primary) 0%, var(--primary) var(--slider-percent), var(--border-2) var(--slider-percent), var(--border-2) 100%)`,
        }}
      />
      <div className="slider-labels">
        <span>Low</span>
        <span>High</span>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, sub, tone }) => (
  <div className={`card stat ${tone || ''}`}>
    <div className="stat-title">{title}</div>
    <div className="stat-value">{value}</div>
    {sub && <div className="stat-sub">{sub}</div>}
  </div>
);

const CapacityBar = ({ label, value, req, highlight }) => {
  const pct = Math.max(0, Math.min(1, req > 0 ? value / req : 0));
  const over = value - req;
  const margin = req > 0 ? (over / req) * 100 : 0;
  const tone = highlight ? 'bar-highlight' : '';

  return (
    <div className={`cap-row ${tone}`}>
      <div className="cap-meta">
        <span className="cap-label">{label}</span>
        <span className={`badge ${value >= req ? 'ok' : 'fail'}`}>
          {value >= req ? 'feasible' : 'insufficient'}
        </span>
      </div>
      <div className="bar">
        <div className="fill" style={{ width: `${Math.min(100, pct * 100)}%` }} />
      </div>
      <div className="cap-values">
        <span>{pretty(Math.round(value))} Nmm</span>
        <span className={value >= req ? 'pos' : 'neg'}>
          {margin >= 0 ? `+${margin.toFixed(1)}%` : `${margin.toFixed(1)}%`}
        </span>
      </div>
    </div>
  );
};

// ---- Validation ----
const validateParameters = (data) => {
  const errors = [];
  const d = Number(data.shaft_diameter);

  if (!Number.isFinite(d)) {
    errors.push({ field: 'shaft_diameter', message: 'Shaft diameter must be a number.' });
  } else {
    if (d < DIAMETER_MIN) {
      errors.push({
        field: 'shaft_diameter',
        message: `Shaft diameter must be ≥ ${DIAMETER_MIN} mm (DIN table minimum).`,
      });
    }
    if (d > DIAMETER_MAX) {
      errors.push({
        field: 'shaft_diameter',
        message: `Shaft diameter must be ≤ ${DIAMETER_MAX} mm (DIN table maximum).`,
      });
    }
  }

  if (data.shaft_type === 'hollow') {
    if (data.shaft_inner_diameter === '' || data.shaft_inner_diameter == null) {
      errors.push({ field: 'shaft_inner_diameter', message: 'Hollow shafts require an inner diameter.' });
    } else if (Number(data.shaft_inner_diameter) >= Number(data.shaft_diameter)) {
      errors.push({
        field: 'shaft_inner_diameter',
        message: 'Shaft inner diameter must be less than the shaft diameter.',
      });
    }
  }

  if (data.hub_outer_diameter !== '' && Number(data.hub_outer_diameter) <= Number(data.shaft_diameter)) {
    errors.push({
      field: 'hub_outer_diameter',
      message: 'Hub outer diameter must be greater than the shaft diameter.',
    });
  }

  if (!data.required_torque || Number(data.required_torque) <= 0) {
    errors.push({ field: 'required_torque', message: 'Required torque must be a positive number.' });
  }

  if (Number(data.safety_factor) < 1.0) {
    errors.push({ field: 'safety_factor', message: 'Safety factor should be ≥ 1.0.' });
  }

  if (data.mu_override !== '' && (Number(data.mu_override) < 0.05 || Number(data.mu_override) > 0.5)) {
    errors.push({
      field: 'mu_override',
      message: 'Friction coefficient μ override must be between 0.05 and 0.50.',
    });
  }

  if (
    data.spline_major_diameter_override !== '' &&
    Number(data.spline_major_diameter_override) <= Number(data.shaft_diameter)
  ) {
    errors.push({
      field: 'spline_major_diameter_override',
      message: 'Spline major diameter override must be greater than the shaft diameter.',
    });
  }

  if (data.spline_major_diameter_override !== '' && Number(data.spline_major_diameter_override) <= 0) {
    errors.push({
      field: 'spline_major_diameter_override',
      message: 'Spline major diameter override must be positive.',
    });
  }

  if (
    data.spline_tooth_count_override !== '' &&
    (!Number.isFinite(Number(data.spline_tooth_count_override)) || Number(data.spline_tooth_count_override) <= 0)
  ) {
    errors.push({
      field: 'spline_tooth_count_override',
      message: 'Spline tooth count override must be a positive number.',
    });
  }

  return errors;
};

function App() {
  const [materials, setMaterials] = useState([]);
  const [materialsLoading, setMaterialsLoading] = useState(true);
  const [materialsError, setMaterialsError] = useState('');

  const [formData, setFormData] = useState(DEFAULT_FORM);
  const [autoLength, setAutoLength] = useState(true);

  const [showBasic, setShowBasic] = useState(false);
  const [showPrefs, setShowPrefs] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(true);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState([]);

  const lengthRecommendation = useMemo(() => {
    return formData.has_bending ? 'D (equal to shaft diameter)' : '0.5D (half shaft diameter)';
  }, [formData.has_bending]);

  const inputParams = result?.input_parameters || null;
  const designTorque = result?.M_design_Nmm ?? result?.required_torque_Nmm;
  const defaultFeasibleCount = result?.capacities_Nmm
    ? Object.entries(result.capacities_Nmm).filter(([_, v]) => v >= (designTorque ?? 0)).length
    : 0;
  const feasibleCount = result?.feasible_connections_count ?? defaultFeasibleCount;
  const hasErrors = validationErrors.length > 0;

  const getFieldError = (field) =>
    validationErrors.find((e) => e.field === field)?.message || '';

  // ---- Load materials ----
  useEffect(() => {
    let cancelled = false;

    const loadMaterials = async () => {
      try {
        const response = await axios.get(`${API_BASE}/materials`);
        if (cancelled) return;

        const available = response.data?.materials || [];
        setMaterials(available);
        setMaterialsError('');
        setMaterialsLoading(false);

        if (available.length) {
          setFormData((prev) => ({
            ...prev,
            shaft_material: available.includes(prev.shaft_material) ? prev.shaft_material : available[0],
            hub_material: available.includes(prev.hub_material) ? prev.hub_material : available[0],
          }));
        }
      } catch (err) {
        if (cancelled) return;
        setMaterialsError('Could not load materials list.');
        setMaterialsLoading(false);
      }
    };

    loadMaterials();
    return () => {
      cancelled = true;
    };
  }, []);

  // ---- Auto hub length recommendation until user overrides ----
  useEffect(() => {
    if (!autoLength) return;

    const d = Number(formData.shaft_diameter);
    if (!Number.isFinite(d) || d <= 0) return;

    const Lrec = formData.has_bending ? Math.round(d) : Math.round(d * 0.5);
    setFormData((prev) => ({ ...prev, hub_length: Lrec }));
  }, [formData.has_bending, formData.shaft_diameter, autoLength]);

  // ---- Validate on changes ----
  useEffect(() => {
    setValidationErrors(validateParameters(formData));
  }, [
    formData.shaft_diameter,
    formData.shaft_type,
    formData.shaft_inner_diameter,
    formData.hub_outer_diameter,
    formData.required_torque,
    formData.safety_factor,
    formData.mu_override,
    formData.spline_major_diameter_override,
    formData.spline_tooth_count_override,
  ]);

  const setNumberField = (name, raw) => {
    if (raw === '') {
      setFormData((prev) => ({ ...prev, [name]: '' }));
      return;
    }
    const v = Number(raw);
    setFormData((prev) => ({ ...prev, [name]: Number.isNaN(v) ? prev[name] : v }));
  };

  const clampOnBlur = (name, min, max) => {
    const v = Number(formData[name]);
    if (!Number.isFinite(v)) return;
    const clamped = Math.min(max, Math.max(min, v));
    if (clamped !== v) setFormData((prev) => ({ ...prev, [name]: clamped }));
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (name.startsWith('pref_')) {
      const prefName = name.replace('pref_', '');
      setFormData((prev) => ({
        ...prev,
        user_preferences: {
          ...prev.user_preferences,
          [prefName]: parseFloat(value),
        },
      }));
      return;
    }

    if (name === 'has_bending') {
      setFormData((prev) => ({ ...prev, has_bending: checked }));
      return;
    }

    if (name === 'shaft_diameter') {
      if (type === 'range') {
        setFormData((prev) => ({ ...prev, shaft_diameter: Math.round(Number(value)) }));
      } else {
        setNumberField('shaft_diameter', value);
      }
      return;
    }

    if (name === 'hub_length') {
      setAutoLength(false);
      setNumberField('hub_length', value);
      return;
    }

    if (
      name === 'required_torque' ||
      name === 'hub_outer_diameter' ||
      name === 'shaft_inner_diameter' ||
      name === 'safety_factor' ||
      name === 'mu_override' ||
      name === 'spline_major_diameter_override' ||
      name === 'spline_tooth_count_override'
    ) {
      setNumberField(name, value);
      return;
    }

    setFormData((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleReset = () => {
    setFormData(DEFAULT_FORM);
    setAutoLength(true);
    setResult(null);
    setError('');
    setValidationErrors([]);
    setShowPrefs(true);
    setShowAdvanced(true);
    setShowBasic(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    let snappedTorque = formData.required_torque;
    if (snappedTorque !== '' && snappedTorque != null && !Number.isNaN(Number(snappedTorque))) {
      snappedTorque = Math.round(Number(snappedTorque) / 100) * 100;
      if (snappedTorque < 0) snappedTorque = 0;
    }

    const formWithSnapped = { ...formData, required_torque: snappedTorque };

    const errors = validateParameters(formWithSnapped);
    setValidationErrors(errors);

    if (errors.length) {
      setError('Please fix the highlighted fields before calculating.');
      setFormData(formWithSnapped);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setFormData(formWithSnapped);

    try {
      const requestData = {
        ...formWithSnapped,
        hub_outer_diameter: formWithSnapped.hub_outer_diameter === '' ? null : formWithSnapped.hub_outer_diameter,
        shaft_inner_diameter:
          formWithSnapped.shaft_inner_diameter === '' ? null : formWithSnapped.shaft_inner_diameter,
        mu_override: formWithSnapped.mu_override === '' ? null : formWithSnapped.mu_override,
        spline_major_diameter_override:
          formWithSnapped.spline_major_diameter_override === '' ? null : formWithSnapped.spline_major_diameter_override,
        spline_tooth_count_override:
          formWithSnapped.spline_tooth_count_override === '' ? null : Math.round(formWithSnapped.spline_tooth_count_override),
      };

      const response = await axios.post(`${API_BASE}/select-connection`, requestData);
      console.log(response.data);
      setResult(response.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((e) => `${e.loc?.join('.')}: ${e.msg}`).join('; '));
      } else if (typeof detail === 'object' && detail !== null) {
        setError(JSON.stringify(detail));
      } else {
        setError(detail || err.message || 'An error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Shaft–Hub Connection Selector</h1>
        <p className="subtitle">Pick the optimal connection based on torque, geometry, and your preferences.</p>
      </header>

      <div className="container">
        <form onSubmit={handleSubmit} className="grid">
          {/* LEFT: Inputs */}
          <div className="panel">
            <div className="panel-head">
              <div>
                <h2 className="panel-title">Inputs</h2>
                <p className="panel-sub">DIN-based feasibility + preference scoring</p>
              </div>

              <div className="panel-actions">
                <button type="button" className="reset-button" onClick={handleReset}>
                  Reset
                </button>
              </div>
            </div>

              {/* Basic */}
              <SectionHeader
              title="Basic Parameters"
              open={showBasic}
              onToggle={() => setShowBasic(v => !v)}
              subtitle="Core geometry + materials"
            />

            {showBasic && (
            <div className="grid2">
              <div className={`form-group ${getFieldError('shaft_diameter') ? 'has-error' : ''}`}>
                <label htmlFor="shaft_diameter">
                  Shaft Diameter (mm)
                  <span className="badge mini">DIN range: {DIAMETER_MIN}–{DIAMETER_MAX}</span>
                </label>

                <small className="note">
                  Used as shaft diameter for <strong>press</strong> and <strong>key</strong>. For <strong>spline</strong>,
                  it is treated as the <strong>minor diameter d</strong>.
                </small>

                <div className="input-group">
                  <input
                    type="range"
                    min={DIAMETER_MIN}
                    max={DIAMETER_MAX}
                    step="2"
                    value={Number(formData.shaft_diameter) || DIAMETER_MIN}
                    onChange={handleInputChange}
                    name="shaft_diameter"
                    aria-label="shaft diameter slider"
                  />
                  <input
                    type="number"
                    id="shaft_diameter"
                    name="shaft_diameter"
                    value={formData.shaft_diameter}
                    onChange={handleInputChange}
                    onBlur={() => clampOnBlur('shaft_diameter', 0, 9999)}
                    inputMode="numeric"
                    placeholder={`${DIAMETER_MIN}–${DIAMETER_MAX}`}
                  />
                </div>

                {getFieldError('shaft_diameter') && <div className="error-text">{getFieldError('shaft_diameter')}</div>}
              </div>

              <div className={`form-group ${getFieldError('hub_length') ? 'has-error' : ''}`}>
                <label htmlFor="hub_length">
                  Hub Length (mm) <span className="hint">Recommended: {lengthRecommendation}</span>
                </label>
                <input
                  type="number"
                  id="hub_length"
                  name="hub_length"
                  value={formData.hub_length}
                  onChange={handleInputChange}
                  onBlur={() => clampOnBlur('hub_length', 0, 99999)}
                  inputMode="numeric"
                  placeholder="e.g. 30"
                />
                <small>
                  Auto-set based on bending ({formData.has_bending ? 'L = D' : 'L = 0.5D'}) until you edit this field.
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="shaft_material">Shaft Material</label>
                <select
                  id="shaft_material"
                  name="shaft_material"
                  value={formData.shaft_material}
                  onChange={handleInputChange}
                  disabled={materialsLoading || !materials.length}
                >
                  {materials.length === 0 && <option>Loading…</option>}
                  {materials.map((mat) => (
                    <option key={mat} value={mat}>
                      {mat}
                    </option>
                  ))}
                </select>
                {materialsLoading && <small>Loading available materials…</small>}
                {materialsError && <div className="error-text">{materialsError}</div>}
              </div>

              <div className="form-group">
                <label htmlFor="hub_material">Hub Material</label>
                <select
                  id="hub_material"
                  name="hub_material"
                  value={formData.hub_material}
                  onChange={handleInputChange}
                  disabled={materialsLoading || !materials.length}
                >
                  {materials.length === 0 && <option>Loading…</option>}
                  {materials.map((mat) => (
                    <option key={mat} value={mat}>
                      {mat}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="surface_condition">Surface Condition (DIN 7190)</label>
                <select
                  id="surface_condition"
                  name="surface_condition"
                  value={formData.surface_condition}
                  onChange={handleInputChange}
                >
                  <option value="dry">Dry (degreased)</option>
                  <option value="oiled">Oiled</option>
                </select>
                <small>Affects friction coefficient μ for press fits.</small>
              </div>

              <div className="form-group">
                <label htmlFor="shaft_type">Shaft Type</label>
                <select id="shaft_type" name="shaft_type" value={formData.shaft_type} onChange={handleInputChange}>
                  <option value="solid">Solid</option>
                  <option value="hollow">Hollow</option>
                </select>
              </div>

              <div className="form-group checkbox-group">
                <label className="checkline">
                  <input 
                    type="checkbox" 
                    name="has_bending" 
                    checked={formData.has_bending} 
                    onChange={handleInputChange} 
                  />
                  <span>
                    Bending Moments Present{' '}
                    <span className="hint-inline">({formData.has_bending ? 'L = D' : 'L = 0.5D'} recommended)</span>
                  </span>
                </label>
              </div>
            </div>
        )}



            {/* Preferences */}
            <SectionHeader
              title="User Preferences"
              open={showPrefs}
              onToggle={() => setShowPrefs((v) => !v)}
              subtitle="Rate importance (0 = low, 1 = high)"
            />
            {showPrefs && (
              <div className="prefs">
                <PreferenceSlider name="ease" label="Ease of Assembly / Disassembly" value={formData.user_preferences.ease} onChange={handleInputChange} />
                <PreferenceSlider name="movement" label="Frequent Axial Movement" value={formData.user_preferences.movement} onChange={handleInputChange} />
                <PreferenceSlider name="bidirectional" label="Bidirectional / Reversing Torque" value={formData.user_preferences.bidirectional} onChange={handleInputChange} />
                <PreferenceSlider name="maintenance" label="Easy Maintenance / Repair" value={formData.user_preferences.maintenance} onChange={handleInputChange} />
                <PreferenceSlider name="vibration" label="Vibration Resistance" value={formData.user_preferences.vibration} onChange={handleInputChange} />
                <PreferenceSlider name="speed" label="High-Speed Suitability" value={formData.user_preferences.speed} onChange={handleInputChange} />
                <PreferenceSlider name="durability" label="Durability / Fatigue Life" value={formData.user_preferences.durability} onChange={handleInputChange} />
                <PreferenceSlider name="cost" label="Low Manufacturing Cost" value={formData.user_preferences.cost} onChange={handleInputChange} />
              </div>
            )}

            {/* Advanced */}
            <SectionHeader
              title="Advanced"
              open={showAdvanced}
              onToggle={() => setShowAdvanced((v) => !v)}
              subtitle="Decision-critical parameters + overrides"
            />
            {showAdvanced && (
              <>
                {hasErrors && (
                  <div className="validation-panel">
                    <strong>Validation issues</strong>
                    <ul>
                      {validationErrors.map((err) => (
                        <li key={err.field + err.message}>{err.message}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="grid2">
                  <div className={`form-group ${getFieldError('required_torque') ? 'has-error' : ''}`}>
                    <label htmlFor="required_torque">
                      Required Torque (Nmm) <span className="badge req">Required</span>
                    </label>
                    <input
                      type="number"
                      id="required_torque"
                      name="required_torque"
                      value={formData.required_torque}
                      onChange={handleInputChange}
                      onBlur={() => clampOnBlur('required_torque', 0, 1e12)}
                      inputMode="numeric"
                      placeholder="e.g. 50000"
                    />
                    <small>Snaps to nearest 100 on submit.</small>
                    {getFieldError('required_torque') && <div className="error-text">{getFieldError('required_torque')}</div>}
                  </div>

                  <div className={`form-group ${getFieldError('safety_factor') ? 'has-error' : ''}`}>
                    <label htmlFor="safety_factor">Safety Factor (≥ 1.0)</label>
                    <input
                      type="number"
                      id="safety_factor"
                      name="safety_factor"
                      value={formData.safety_factor}
                      onChange={handleInputChange}
                      onBlur={() => clampOnBlur('safety_factor', 0, 999)}
                      step="0.1"
                      inputMode="decimal"
                      placeholder="e.g. 1.5"
                    />
                    {getFieldError('safety_factor') && <div className="error-text">{getFieldError('safety_factor')}</div>}
                  </div>

                  {formData.shaft_type === 'hollow' && (
                    <div className={`form-group ${getFieldError('shaft_inner_diameter') ? 'has-error' : ''}`}>
                      <label htmlFor="shaft_inner_diameter">Shaft Inner Diameter (mm)</label>
                      <input
                        type="number"
                        id="shaft_inner_diameter"
                        name="shaft_inner_diameter"
                        value={formData.shaft_inner_diameter}
                        onChange={handleInputChange}
                        onBlur={() => clampOnBlur('shaft_inner_diameter', 0, 99999)}
                        inputMode="numeric"
                        placeholder="e.g. 15"
                      />
                      <small>Must be &lt; shaft diameter.</small>
                      {getFieldError('shaft_inner_diameter') && <div className="error-text">{getFieldError('shaft_inner_diameter')}</div>}
                    </div>
                  )}

                  <div className={`form-group ${getFieldError('hub_outer_diameter') ? 'has-error' : ''}`}>
                    <label htmlFor="hub_outer_diameter">Hub Outer Diameter (mm)</label>
                    <input
                      type="number"
                      id="hub_outer_diameter"
                      name="hub_outer_diameter"
                      value={formData.hub_outer_diameter}
                      onChange={handleInputChange}
                      onBlur={() => clampOnBlur('hub_outer_diameter', 0, 999999)}
                      inputMode="numeric"
                      placeholder="Auto: 2×d if empty"
                    />
                    <small>Must be &gt; shaft diameter (for press-fit hub stiffness).</small>
                    {getFieldError('hub_outer_diameter') && <div className="error-text">{getFieldError('hub_outer_diameter')}</div>}
                  </div>

                  <div className={`form-group ${getFieldError('mu_override') ? 'has-error' : ''}`}>
                    <label htmlFor="mu_override">Friction Coefficient (μ) Override</label>
                    <input
                      type="number"
                      id="mu_override"
                      name="mu_override"
                      value={formData.mu_override}
                      onChange={handleInputChange}
                      onBlur={() => clampOnBlur('mu_override', 0, 1)}
                      step="0.01"
                      inputMode="decimal"
                      placeholder="Auto if empty (DIN table)"
                    />
                    {getFieldError('mu_override') && <div className="error-text">{getFieldError('mu_override')}</div>}
                  </div>
                </div>

                <div className="grid2">
                  <div className={`form-group ${getFieldError('spline_major_diameter_override') ? 'has-error' : ''}`}>
                    <label htmlFor="spline_major_diameter_override">Spline Major Diameter Override (D)</label>
                    <small className="note">
                      If set: spline uses <strong>d = shaft_diameter (minor)</strong> and <strong>D = this value (major)</strong>.
                      Leave empty for table / heuristic geometry.
                    </small>
                    <input
                      type="number"
                      id="spline_major_diameter_override"
                      name="spline_major_diameter_override"
                      value={formData.spline_major_diameter_override}
                      onChange={handleInputChange}
                      onBlur={() => clampOnBlur('spline_major_diameter_override', 0, 999999)}
                      step="0.1"
                      inputMode="decimal"
                      placeholder="e.g. 36"
                    />
                    {getFieldError('spline_major_diameter_override') && (
                      <div className="error-text">{getFieldError('spline_major_diameter_override')}</div>
                    )}
                  </div>

                  <div className={`form-group ${getFieldError('spline_tooth_count_override') ? 'has-error' : ''}`}>
                    <label htmlFor="spline_tooth_count_override">Spline Tooth Count Override (z)</label>
                    <input
                      type="number"
                      id="spline_tooth_count_override"
                      name="spline_tooth_count_override"
                      value={formData.spline_tooth_count_override}
                      onChange={handleInputChange}
                      onBlur={() => clampOnBlur('spline_tooth_count_override', 0, 999999)}
                      inputMode="numeric"
                      placeholder="optional"
                    />
                    <small>Optional: set z only if you already know it.</small>
                    {getFieldError('spline_tooth_count_override') && (
                      <div className="error-text">{getFieldError('spline_tooth_count_override')}</div>
                    )}
                  </div>
                </div>
              </>
            )}

            <div className="action-row">
              <button type="submit" disabled={loading || hasErrors} className="submit-button">
                {loading ? (
                  <>
                    <span className="loading-shimmer" style={{ display: 'inline-block', width: '20px', height: '20px', marginRight: '10px', verticalAlign: 'middle' }}></span>
                    Calculating…
                  </>
                ) : 'Find Optimal Connection'}
              </button>
            </div>

            {!!error && <div className="error-banner">{error}</div>}
          </div>

          {/* RIGHT: Results */}
          <div className="panel">
            <h2>Results</h2>

            {!result && (
              <div className="empty">
                <p>
                  Fill the form and click <strong>Find Optimal Connection</strong>.
                </p>
                <p className="muted">We'll show feasibility, margins, and the recommended connection here.</p>
              </div>
            )}

            {result && (
              <>
                {!result.feasible && (
                  <div className="results-banner warn">
                    <strong>No feasible connection found.</strong>{' '}
                    {result.reason ||
                      'Try increasing shaft diameter, hub length, or reducing required torque/safety factor.'}
                  </div>
                )}

                <div className="comparison-grid">
                  <div className="comparison-card comparison-ml">
                    <h4>ML Prediction</h4>
                    <p className="comparison-conn">
                      {result.ml_recommendation ? formatConnectionLabel(result.ml_recommendation) : 'N/A'}
                    </p>
                    <p className="muted"> Output probabilities:</p>
                    {result.ml_probabilities && (
                      <div className="ml-probs">
                        {Object.entries(result.ml_probabilities).map(([conn, prob]) => (
                          <div key={conn} className="ml-row">
                            <span>{formatMlLabel(conn)}</span>
                            <span>{(prob * 100).toFixed(1)}%</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className={`recommend card ${result.recommended_connection}`}>
                  <div className="rec-top">
                    <span className="pill">Analytical Recommendation</span>
                    <h3 className="rec-title">{result.recommended_connection?.toUpperCase()}</h3>
                  </div>

                  <div className="rec-grid">
                    <StatCard
                      title="Required Torque"
                      value={`${pretty(result.required_torque_Nmm)} Nmm`}
                      sub="From your input (snapped on submit)"
                      tone="primary"
                    />
                    <StatCard
                      title="μ Used"
                      value={typeof result.mu_used === 'number' ? result.mu_used.toFixed(3) : String(result.mu_used)}
                      sub={`Surface: ${result.surface_condition || 'dry'}`}
                      tone="neutral"
                    />
                    <StatCard
                      title="Hub Stiffness"
                      value={
                        typeof result.hub_stiffness_factor === 'number'
                          ? result.hub_stiffness_factor >= 0.85
                            ? '✓ Thick'
                            : result.hub_stiffness_factor >= 0.5
                            ? '◐ Medium'
                            : '⚠ Thin'
                          : 'N/A'
                      }
                      sub={
                        typeof result.hub_stiffness_factor === 'number'
                          ? `Factor: ${result.hub_stiffness_factor.toFixed(2)}`
                          : ''
                      }
                      tone={
                        result.hub_stiffness_factor >= 0.7
                          ? 'ok'
                          : result.hub_stiffness_factor >= 0.4
                          ? 'warn'
                          : 'fail'
                      }
                    />
                    <StatCard
                      title="Feasible Options"
                      value={feasibleCount}
                      sub={`Connections meeting design torque${designTorque ? ` (${pretty(designTorque)} Nmm)` : ''}`}
                      tone="neutral"
                    />  
                  </div>

                  <div className="caps">
                    <h4>Torque Capacities</h4>
                    <p className="muted">
                      Each bar compares torque capacity against the factored design torque
                      {designTorque ? ` (${pretty(designTorque)} Nmm)` : ''}.
                    </p>
                    {Object.entries(result.capacities_Nmm).map(([type, capacity]) => (
                      <CapacityBar
                        key={type}
                        label={type.toUpperCase()}
                        value={capacity}
                        req={designTorque ?? result.required_torque_Nmm}
                        highlight={type === result.recommended_connection}
                      />
                    ))}
                  </div>

                  {result.scores && Object.keys(result.scores).length > 0 && (
                    <div className="scores-block">
                      <h4>Selection Scores (feasible only)</h4>
                      <p className="muted">Scores combine your preferences with safety margin and penalties.</p>
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
                  <h4>Detail Snapshot (raw data)</h4>
                  <p className="muted">Useful for thesis appendices / validation.</p>
                  <pre className="json">{JSON.stringify(result.details, null, 2)}</pre>
                </div>
              </>
            )}
          </div>
        </form>

        <div className="footer">DIN-based shaft–hub connection selector • Press / Key / Spline</div>
      </div>
    </div>
  );
}

export default App;