# TAS Schafer Integration: Barriers to Current Implementation and Future Work Path

## Executive Summary

This document provides a comprehensive analysis of why TAS Schafer shrink disc and locking assembly data cannot be integrated into the current thesis implementation, despite being relevant shaft-hub connection types. It outlines the technical barriers, data limitations, and timeline constraints that prevent integration, while providing a detailed roadmap for future work that would enable such integration.

**Key Finding**: Integration is technically feasible but requires 8-11 weeks of development time, which exceeds the thesis completion timeline. The barriers are primarily related to analytical model complexity, data incompleteness, and the need for extensive pipeline modifications.

---

## 1. Current Thesis Scope and Contribution

### 1.1 Thesis Objective
The thesis aims to develop an intelligent tool for **shaft-hub connection prediction** that:
- Evaluates three connection types: press fits, keyed fits, and splined fits
- Uses analytical models (DIN 7190, 6885, 5480) to generate synthetic training data
- Trains ML models to predict optimal connection types
- Integrates user preferences and mechanical feasibility

### 1.2 Current Implementation Status
- ✅ Analytical pipeline for 3 connection types (press, key, spline)
- ✅ Synthetic dataset: 4,993 samples
- ✅ Trained ML model: 91.27% accuracy
- ✅ Web application with hybrid analytical-ML approach
- ✅ Model tested and validated

### 1.3 TAS Schafer Connection Types
TAS Schafer provides two additional shaft-hub connection types:
1. **Shrink Discs** (3-part, 2-part variants) - ~170 catalog entries
2. **Locking Assemblies** (3015, 3015.1, RB variants) - ~103 catalog entries

Both types are legitimate shaft-hub connections that would enhance the thesis scope, but integration faces significant barriers.

---

## 2. Technical Barriers to Integration

### 2.1 Analytical Model Complexity

#### Barrier 1: Different Physics for Each Type

**Shrink Discs**:
- Mechanism: **Interference fit + clamping elements**
- Torque transmission: Combination of:
  1. Interference fit friction (similar to press fit)
  2. Clamping element pressure (Z screws applying radial force)
- Key parameters:
  - Working diameter (dw) < shaft diameter (d)
  - Clamping geometry (e, H)
  - Assembly torque (MA) for clamping screws
  - Number of clamping elements (Z)

**Locking Assemblies**:
- Mechanism: **Pure clamping** (no interference fit)
- Torque transmission: Primarily from clamping element pressure
- Key parameters:
  - Axial force capacity (Fax) - new dimension
  - Working pressure (pW) and nominal pressure (pN)
  - Assembly torque (MA)
  - Number of clamping elements (Z)

**Impact**: Requires implementing **two completely new analytical models** with different physics than the existing three types.

**Current State**: 
- Press fit: `M_t = (π/2) * μ * p * L * d²` (friction-based)
- Key: `M_t = min(T_τ, T_p)` (shear and bearing)
- Spline: `M_t = p_allow * (h/2) * L * (d/2) * N` (form closure)

**Required New Models**:
- Shrink disc: `M_t = f(interference, clamping_pressure, Z, geometry)`
- Locking assembly: `M_t = f(clamping_pressure, Z, geometry)` + `Fax = f(pressure, geometry)`

**Effort**: 2-3 weeks to:
- Study TAS equations/standards from PDFs
- Implement shrink disc analytical model
- Implement locking assembly analytical model
- Validate against catalog data

#### Barrier 2: Missing Analytical Standards

**Current Models**: Based on established DIN standards:
- DIN 7190 (press fits)
- DIN 6885 (keys)
- DIN 5480 (splines)

**TAS Models**: 
- Proprietary/commercial equations
- May be simplified for catalog purposes
- Not publicly standardized
- Requires reverse-engineering from catalog data

**Impact**: Cannot directly apply existing standards; must derive or adapt equations from TAS documentation.

### 2.2 Data Incompatibility

#### Barrier 3: Feature Mismatch

**Current Model Features (18 total)**:
- Numeric (15): shaft_diameter, hub_length, has_bending, safety_factor, hub_outer_diameter, shaft_inner_diameter, required_torque, 8 preference weights
- Categorical (3): shaft_type, shaft_material, surface_condition

**TAS Data Available**:
- Shaft diameter (d) ✅
- Outer diameter (D) ✅
- Max torque (M_max / Mt) ✅
- Clamping elements (Z) ✅
- Assembly torque (MA) ✅
- Working diameter (dw) - shrink discs only ✅
- Interference (I) - shrink discs only ✅
- Axial force (Fax) - locking assemblies only ✅
- Pressure (pN, pW) ✅

**TAS Data Missing**:
- User preferences (8 weights) ❌
- Material specifications (explicit) ❌
- Safety factors ❌
- Surface condition ❌
- Hub length (some files) ❌
- Shaft inner diameter (some files) ❌

**Impact**: Cannot directly use TAS data as training samples without:
- Feature engineering (mapping TAS → model features)
- Default values for missing features
- Assumptions about materials/safety factors

**Effort**: 1 week for feature engineering and mapping

#### Barrier 4: Small Sample Size

**TAS Real Data**:
- Shrink discs: ~170 rows
- Locking assemblies: ~103 rows
- **Total: ~273 rows**

**Current Synthetic Data**: 4,993 rows

**Problem**: TAS data represents only **5.2%** of combined dataset (273 / 5,266)

**Impact**: 
- Model would be dominated by synthetic data
- Real TAS patterns may not be learned
- Severe class imbalance if added directly

**Solution Required**: Generate synthetic TAS data using new analytical models
- Shrink discs: ~2,000-3,000 synthetic samples
- Locking assemblies: ~1,000-1,500 synthetic samples
- **Total new synthetic: ~3,000-4,500 samples**

**Effort**: 1.5-2 weeks for synthetic data generation

### 2.3 Model Architecture Changes

#### Barrier 5: Extended Classification Problem

**Current Model**:
- Classes: 3 (press, key, spline)
- Features: 18
- Samples: 4,993
- Performance: 91.27% accuracy

**Extended Model Required**:
- Classes: **5** (press, key, spline, shrink_disc, locking_assembly)
- Features: **28-30** (18 existing + 10-12 new)
- Samples: **9,000-10,000** (4,993 existing + 273 real + 3,000-4,500 synthetic)
- Class distribution:
  - press: ~800 (8-9%)
  - key: ~1,400 (15-16%)
  - spline: ~2,700 (29-30%)
  - shrink_disc: ~2,500-3,000 (28-33%) ⚠️
  - locking_assembly: ~1,500-2,000 (17-22%)

**Challenges**:
1. **Class imbalance**: Shrink discs would dominate (28-33%)
2. **Feature complexity**: 67% more features (18 → 30)
3. **Model complexity**: 67% more classes (3 → 5)
4. **Performance risk**: May degrade performance on original 3 classes
5. **Training time**: Significantly longer

**Effort**: 1 week for model retraining and evaluation

### 2.4 Pipeline Modifications

#### Barrier 6: End-to-End Changes Required

**Current Pipeline**:
1. Sample parameters (geometry, torque, preferences)
2. Run analytical selector (press/key/spline)
3. Get label
4. Save to CSV
5. Train ML model
6. Deploy in web app

**Extended Pipeline Required**:
1. Sample parameters (geometry, torque, preferences, **clamping parameters**)
2. Run analytical selector (press/key/spline/**shrink_disc/locking**)
3. Get label (5 classes)
4. Save to CSV (with new features)
5. Train ML model (5 classes, 30 features)
6. Deploy in web app (with new UI fields)

**Changes Needed**:
- **Backend**: New analytical functions, extended selector, new model
- **Frontend**: New input fields (clamping elements, assembly torque, etc.)
- **API**: Extended request/response formats
- **Model Service**: Load 5-class model, handle new features

**Effort**: 2 weeks (1 week backend, 1 week frontend)

### 2.5 Timeline Constraints

#### Barrier 7: Development Time Exceeds Thesis Timeline

**Total Effort Breakdown**:
- Analytical models: 2-3 weeks
- Dataset generation: 1.5-2 weeks
- Feature engineering: 1 week
- Model retraining: 1 week
- Pipeline modifications: 2 weeks
- Testing & validation: 1 week
- **Total: 8.5-11 weeks**

**Reality Check**:
- Thesis completion timeline: Limited
- Risk of timeline overrun: High
- Impact on thesis quality: Negative (rushed implementation)

**Impact**: Integration would require extending thesis timeline significantly, which may not be feasible.

---

## 3. Why Integration Cannot Be Done Now

### 3.1 Summary of Barriers

| Barrier | Type | Impact | Mitigation Effort |
|---------|------|--------|-------------------|
| Different physics | Technical | High | 2-3 weeks |
| Missing standards | Technical | Medium | 1-2 weeks |
| Feature mismatch | Data | High | 1 week |
| Small sample size | Data | High | 1.5-2 weeks |
| Model complexity | Architecture | High | 1 week |
| Pipeline changes | System | Medium | 2 weeks |
| Timeline | Project | Critical | N/A |

### 3.2 Root Causes

1. **Scope Expansion**: Adding 2 new connection types doubles the analytical work
2. **Different Mechanisms**: Each type requires unique analytical models
3. **Data Incompleteness**: TAS data missing critical features (preferences, materials)
4. **Timeline**: 8.5-11 weeks exceeds available time
5. **Risk**: High probability of degrading existing model performance

### 3.3 Conclusion: Why Not Now

**Integration is not feasible for thesis completion because**:
1. Requires 8.5-11 weeks of development (exceeds timeline)
2. Two new analytical models needed (different physics)
3. Incomplete TAS data (missing features require assumptions)
4. High risk to existing model performance
5. Would require extensive testing and validation

**However**: Integration is **technically feasible** and could be accomplished with proper time allocation and resources.

---

## 4. Future Work: Integration Roadmap

### 4.1 Phase 1: Analytical Model Development (Weeks 1-3)

#### 4.1.1 Shrink Disc Analytical Model

**Objective**: Implement analytical model for shrink disc torque capacity

**Steps**:
1. **Study TAS Documentation** (Week 1)
   - Review `shrink_discs_equations 3-part.pdf`
   - Extract equations for torque capacity
   - Understand clamping element contribution
   - Document assumptions and simplifications

2. **Implement Base Model** (Week 1-2)
   ```python
   def shrink_disc_capacity(
       d_mm: float,           # Shaft diameter
       dw_mm: float,           # Working diameter
       L_mm: float,            # Engagement length
       Z: int,                 # Number of clamping elements
       MA_Nm: float,           # Assembly torque
       e_mm: float,            # Clamping geometry
       H_mm: float,            # Clamping height
       I_mm: float,            # Interference
       material_props: dict    # Material properties
   ) -> Dict[str, Any]:
       """
       Calculate shrink disc torque capacity.
       
       Combines:
       1. Interference fit contribution (similar to press fit)
       2. Clamping element contribution
       """
       # Interference fit component
       p_interference = calculate_interference_pressure(I_mm, d_mm, material_props)
       Mt_interference = (π/2) * μ * p_interference * L_mm * d_mm²
       
       # Clamping element component
       p_clamping = calculate_clamping_pressure(MA_Nm, Z, e_mm, H_mm, dw_mm)
       Mt_clamping = (π/2) * μ * p_clamping * L_mm * dw_mm²
       
       # Combined capacity
       Mt_total = Mt_interference + Mt_clamping
       
       return {
           "Mt_total": Mt_total,
           "Mt_interference": Mt_interference,
           "Mt_clamping": Mt_clamping,
           "p_interference": p_interference,
           "p_clamping": p_clamping,
       }
   ```

3. **Validate Against Catalog** (Week 2)
   - Compare calculated capacities with TAS catalog M_max values
   - Identify discrepancies and refine model
   - Document accuracy and limitations

4. **Integration with Selector** (Week 2-3)
   - Add shrink disc to `select_shaft_connection()`
   - Implement feasibility checks
   - Add scoring logic for shrink discs

#### 4.1.2 Locking Assembly Analytical Model

**Objective**: Implement analytical model for locking assembly torque and axial force capacity

**Steps**:
1. **Study TAS Documentation** (Week 2)
   - Review locking assembly equations
   - Understand pure clamping mechanism
   - Extract Fax (axial force) calculations

2. **Implement Base Model** (Week 2-3)
   ```python
   def locking_assembly_capacity(
       d_mm: float,           # Shaft diameter
       D_mm: float,           # Outer diameter
       L_mm: float,           # Engagement length
       Z: int,                # Number of clamping elements
       MA_Nm: float,          # Assembly torque
       material_props: dict   # Material properties
   ) -> Dict[str, Any]:
       """
       Calculate locking assembly torque and axial force capacity.
       
       Pure clamping mechanism (no interference fit).
       """
       # Clamping pressure from assembly torque
       p_clamping = calculate_clamping_pressure(MA_Nm, Z, geometry)
       
       # Torque capacity
       Mt = (π/2) * μ * p_clamping * L_mm * d_mm²
       
       # Axial force capacity
       Fax = π * d_mm * L_mm * p_clamping * μ_axial
       
       return {
           "Mt": Mt,
           "Fax": Fax,
           "p_clamping": p_clamping,
       }
   ```

3. **Validate Against Catalog** (Week 3)
   - Compare with TAS catalog Mt and Fax values
   - Refine model parameters

4. **Integration with Selector** (Week 3)
   - Add locking assembly to selector
   - Handle axial force requirements (new dimension)

### 4.2 Phase 2: Dataset Generation and Feature Engineering (Weeks 4-5)

#### 4.2.1 Feature Engineering

**Objective**: Map TAS parameters to model features and handle missing data

**Implementation**:
```python
def map_tas_to_model_features(tas_row: dict) -> dict:
    """
    Map TAS catalog data to model input features.
    
    Handles missing features with defaults/estimates.
    """
    # Direct mappings
    features = {
        "shaft_diameter": tas_row["d"],
        "hub_outer_diameter": tas_row["D"],
        "required_torque": tas_row["M_max"],  # For comparison
    }
    
    # TAS-specific features
    if "shrink_disc" in tas_row["type"]:
        features.update({
            "working_diameter": tas_row["dw"],
            "clamping_elements": tas_row["Z"],
            "assembly_torque": tas_row["MA"],
            "clamping_geometry_e": tas_row["e"],
            "clamping_geometry_H": tas_row["H"],
            "interference": tas_row["I"],
        })
    elif "locking" in tas_row["type"]:
        features.update({
            "clamping_elements": tas_row["Z"],
            "assembly_torque": tas_row["MA"],
            "axial_force_capacity": tas_row["Fax"],
            "working_pressure": tas_row["pW"],
        })
    
    # Missing features - use defaults/estimates
    features.update({
        "hub_length": tas_row.get("A") or tas_row.get("L") or estimate_hub_length(tas_row["d"]),
        "shaft_type": "solid",  # Default assumption
        "shaft_material": "Steel E360",  # Common assumption
        "hub_material": "Steel E360",
        "surface_condition": "oiled",  # Common for TAS products
        "safety_factor": 1.5,  # Typical for catalog ratings
        "has_bending": True,  # Common assumption
        # User preferences: use neutral values (0.5)
        "pref_ease": 0.5,
        "pref_movement": 0.5,
        "pref_cost": 0.5,
        "pref_vibration": 0.5,
        "pref_speed": 0.5,
        "pref_bidirectional": 0.5,
        "pref_maintenance": 0.5,
        "pref_durability": 0.5,
    })
    
    return features
```

#### 4.2.2 Synthetic Data Generation

**Objective**: Generate synthetic TAS data using new analytical models

**Implementation**:
```python
def generate_synthetic_tas_data(
    n_shrink_disc: int = 2500,
    n_locking: int = 1500,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic shrink disc and locking assembly data.
    
    Uses new analytical models to create training samples.
    """
    rng = np.random.default_rng(seed)
    rows = []
    
    # Generate shrink disc samples
    for _ in range(n_shrink_disc):
        # Sample parameters
        d = sample_diameter(rng)
        dw = d * rng.uniform(0.7, 0.9)  # Working diameter < shaft diameter
        L = sample_hub_length(rng, d)
        Z = rng.integers(3, 30)  # Clamping elements
        MA = sample_assembly_torque(rng, d, Z)
        e = sample_clamping_geometry_e(rng, d)
        H = sample_clamping_geometry_H(rng, d)
        I = sample_interference(rng, d)
        
        # Calculate capacity
        capacity = shrink_disc_capacity(d, dw, L, Z, MA, e, H, I, materials)
        
        # Create sample
        rows.append({
            "shaft_diameter": d,
            "working_diameter": dw,
            "hub_length": L,
            "clamping_elements": Z,
            "assembly_torque": MA,
            "clamping_geometry_e": e,
            "clamping_geometry_H": H,
            "interference": I,
            "required_torque": capacity["Mt_total"] * rng.uniform(0.3, 1.0),
            "label": "shrink_disc",
            # ... other features ...
        })
    
    # Generate locking assembly samples (similar process)
    # ...
    
    return pd.DataFrame(rows)
```

#### 4.2.3 Dataset Combination

**Objective**: Combine existing synthetic data with TAS real and synthetic data

**Implementation**:
```python
def combine_datasets():
    # Load existing
    df_existing = pd.read_csv("synthetic_SHC_dataset.csv")  # 4,993 rows
    
    # Load TAS real data
    df_tas_real = load_and_map_tas_data()  # ~273 rows
    
    # Generate TAS synthetic data
    df_tas_synthetic = generate_synthetic_tas_data()  # ~4,000 rows
    
    # Combine
    df_combined = pd.concat([
        df_existing,
        df_tas_real,
        df_tas_synthetic
    ], ignore_index=True)
    
    # Verify class distribution
    print(df_combined["label"].value_counts())
    # Expected:
    # shrink_disc: ~2,500-3,000 (28-33%)
    # spline: ~2,700 (29-30%)
    # locking_assembly: ~1,500-2,000 (17-22%)
    # key: ~1,400 (15-16%)
    # press: ~800 (8-9%)
    
    return df_combined
```

### 4.3 Phase 3: Model Retraining (Week 6)

#### 4.3.1 Model Architecture Updates

**Changes Required**:
- Extend feature list (18 → 30 features)
- Update preprocessor to handle new features
- Modify model to output 5 classes

**Implementation**:
```python
# Extended feature list
FEATURE_NUMERIC = [
    # Existing (15)
    "shaft_diameter", "hub_length", "has_bending", "safety_factor",
    "hub_outer_diameter", "shaft_inner_diameter", "required_torque",
    "pref_ease", "pref_movement", "pref_cost", "pref_vibration",
    "pref_speed", "pref_bidirectional", "pref_maintenance", "pref_durability",
    # New TAS features (10-12)
    "clamping_elements", "assembly_torque",
    "working_diameter",  # shrink disc
    "clamping_geometry_e", "clamping_geometry_H",  # shrink disc
    "interference",  # shrink disc
    "axial_force_capacity",  # locking
    "working_pressure", "nominal_pressure",  # locking
]

CATEGORICAL = [
    "shaft_type", "shaft_material", "surface_condition",
    "connection_type",  # NEW: press/key/spline/shrink_disc/locking
]

# Update label encoder
label_mapping = {
    0: "press",
    1: "key",
    2: "spline",
    3: "shrink_disc",  # NEW
    4: "locking_assembly",  # NEW
}
```

#### 4.3.2 Training and Evaluation

**Considerations**:
- Class imbalance handling (shrink_disc dominates)
- Feature importance analysis
- Performance on original 3 classes (must not degrade)
- Cross-validation with class stratification

**Metrics**:
- Overall accuracy
- Per-class F1 scores (especially original 3 classes)
- Confusion matrix
- Feature importance

### 4.4 Phase 4: System Integration (Weeks 7-8)

#### 4.4.1 Backend Updates

**API Changes**:
```python
class ShaftConnectionRequest(BaseModel):
    # Existing fields...
    
    # New TAS fields (optional)
    clamping_elements: Optional[int] = None
    assembly_torque: Optional[float] = None
    working_diameter: Optional[float] = None  # shrink disc
    axial_force_required: Optional[float] = None  # locking
    
    # Toggle for TAS types
    include_tas_types: bool = False
```

**Selector Updates**:
```python
def select_shaft_connection(request: ShaftConnectionRequest):
    candidates = {}
    
    # Existing types
    candidates["press"] = pressfit_capacity(...)
    candidates["key"] = key_capacity(...)
    candidates["spline"] = spline_capacity(...)
    
    # TAS types (if enabled)
    if request.include_tas_types:
        candidates["shrink_disc"] = shrink_disc_capacity(...)
        candidates["locking_assembly"] = locking_assembly_capacity(...)
    
    # Select best candidate
    best = select_best_candidate(candidates, request.user_preferences)
    
    return {"recommended_connection": best, ...}
```

#### 4.4.2 Frontend Updates

**New UI Elements**:
- Toggle: "Include TAS Schafer connection types"
- Conditional fields (shown when toggle ON):
  - Clamping elements count
  - Assembly torque
  - Working diameter (shrink disc)
  - Axial force requirement (locking)
- Results display: Show 5 connection types

### 4.5 Phase 5: Testing and Validation (Week 9)

**Testing Requirements**:
1. Analytical model validation against TAS catalog
2. ML model performance (especially original 3 classes)
3. End-to-end system testing
4. User acceptance testing

**Success Criteria**:
- Shrink disc model accuracy: >85% vs catalog
- Locking assembly model accuracy: >85% vs catalog
- Original 3 classes: No degradation (<2% accuracy drop)
- Overall 5-class accuracy: >88%

---

## 5. What to Do Now: Thesis Integration Strategy

### 5.1 Acknowledge Scope and Limitations

**In Background Section** (Chapter 2):
Add subsection: "Commercial Shaft-Hub Connection Solutions"

```latex
\subsection{Commercial Shaft--Hub Connection Solutions}
\label{subsec:commercial_solutions}

While this thesis focuses on three fundamental connection types (press fits, 
keys, and splines), commercial solutions exist that extend these concepts. 
TAS Schafer, for example, offers shrink discs and locking assemblies that 
combine interference fits with clamping elements to achieve higher torque 
capacities~\cite{TAS_Schafer_Catalog}.

\textbf{Shrink Discs} utilize an interference fit base enhanced by radial 
clamping elements (typically screws) that apply additional pressure at a 
working diameter smaller than the shaft diameter. This hybrid approach 
combines the benefits of interference fits with the adjustability and 
higher capacity of clamping mechanisms.

\textbf{Locking Assemblies} employ a pure clamping mechanism without 
interference fits, providing both torque transmission and axial force 
capacity through controlled clamping element pressure.

These commercial solutions represent an extension of the fundamental 
connection types considered in this thesis. While they offer advantages 
in specific applications, their integration would require:
\begin{itemize}
    \item Proprietary analytical models (not standardized in DIN)
    \item Additional geometric parameters (clamping elements, working 
          diameters)
    \item Extended feature engineering (assembly torque, axial forces)
    \item Significant pipeline modifications
\end{itemize}

For the scope of this thesis, the focus remains on the three fundamental 
types that form the basis of most shaft--hub connections and are fully 
standardized in DIN standards.
```

### 5.2 Document Future Work Path

**In Future Work Section** (Chapter 6):
Extend existing future work with detailed TAS integration plan

```latex
\paragraph{Extension to Commercial Connection Types.}
The current framework considers three fundamental connection types based 
on DIN standards. A natural extension would integrate commercial solutions 
such as TAS Schafer shrink discs and locking assemblies, which combine 
interference fits with clamping elements.

\textbf{Integration Requirements:}
\begin{enumerate}
    \item \textbf{Analytical Model Development:} Implement analytical 
          models for shrink disc and locking assembly torque capacity, 
          accounting for clamping element contributions and working 
          diameter effects. This requires studying proprietary equations 
          and validating against catalog data.
    
    \item \textbf{Feature Engineering:} Extend the feature set to include 
          clamping-specific parameters (number of clamping elements, 
          assembly torque, working diameter) and handle missing features 
          in catalog data (user preferences, explicit materials) through 
          defaults or estimates.
    
    \item \textbf{Synthetic Data Generation:} Generate synthetic training 
          data for TAS types using the new analytical models, maintaining 
          the same DIN-compliant sampling approach used for the three 
          fundamental types.
    
    \item \textbf{Model Extension:} Retrain the ML classifier to handle 
          five classes (press, key, spline, shrink disc, locking assembly) 
          with extended features (~30 vs. 18), ensuring no degradation in 
          performance on the original three classes.
    
    \item \textbf{System Integration:} Extend the web application to 
          support TAS-specific input fields and display recommendations 
          for all five connection types.
\end{enumerate}

\textbf{Estimated Effort:} 8-11 weeks of development time, including 
analytical model implementation, dataset generation, model retraining, 
and system integration.

\textbf{Challenges:}
\begin{itemize}
    \item Proprietary equations require reverse-engineering from catalog 
          data
    \item Different physics for each type (interference+clamping vs. 
          pure clamping)
    \item Class imbalance (TAS types would represent ~50\% of combined 
          dataset)
    \item Feature incompatibility (catalog data missing preferences, 
          materials)
\end{itemize}

This extension would demonstrate the framework's extensibility and provide 
a more comprehensive solution covering both standardized and commercial 
connection types.
```

### 5.3 Show Understanding of Extension Path

**In Discussion Section** (Chapter 5):
Add paragraph on extensibility

```latex
\paragraph{Extensibility to Additional Connection Types.}
The developed framework demonstrates a clear pathway for extending to 
additional connection types. The methodology of encoding analytical 
models into synthetic data generation and training ML classifiers is 
directly applicable to other connection types, such as commercial shrink 
discs or locking assemblies.

The key requirements for such extensions are:
\begin{enumerate}
    \item Analytical models for the new connection type(s)
    \item Parameter sampling strategies aligned with the new type's 
          design space
    \item Feature engineering to map new parameters to the model's 
          feature set
    \item Synthetic data generation using the analytical models
    \item Model retraining with extended classes and features
\end{enumerate}

While this thesis focuses on three fundamental types, the framework's 
architecture supports such extensions, as demonstrated by the modular 
design of the analytical pipeline and the ML training infrastructure.
```

### 5.4 Create Supporting Documentation

**Create**: `Bachelor_Code/TAS_Integration_Plan.md`
- Detailed technical specification
- Code structure for future implementation
- Reference for future work section

**Benefits**:
- Shows comprehensive understanding
- Provides clear roadmap
- Demonstrates thesis extensibility
- Satisfies professor's request to "include the company somehow"

---

## 6. Recommended Actions for Thesis Completion

### Immediate Actions (This Week)

1. **Add Background Section** (2-3 hours)
   - Write subsection on commercial solutions
   - Mention TAS Schafer shrink discs and locking assemblies
   - Explain why they're out of scope

2. **Extend Future Work Section** (2-3 hours)
   - Add detailed TAS integration roadmap
   - Include effort estimates and challenges
   - Reference this document

3. **Update Discussion Section** (1-2 hours)
   - Add paragraph on extensibility
   - Show understanding of extension path

4. **Create Integration Plan Document** (2-3 hours)
   - Technical specification for future work
   - Code structure outline
   - Reference in thesis

**Total Time**: ~8-11 hours (1-2 days)

### Benefits of This Approach

1. **Serves Thesis Purpose**: 
   - Shows comprehensive understanding of shaft-hub connections
   - Acknowledges commercial solutions
   - Demonstrates extensibility knowledge

2. **Satisfies Professor**:
   - "Includes the company" through background and future work
   - Shows you understand integration path
   - Demonstrates research depth

3. **Maintains Focus**:
   - Keeps thesis scope manageable
   - Preserves model quality
   - Avoids timeline risks

4. **Future Value**:
   - Clear roadmap for post-thesis work
   - Technical specification ready
   - Demonstrates planning capability

---

## 7. Conclusion

### Why Integration Cannot Be Done Now

1. **Timeline**: 8.5-11 weeks exceeds thesis completion timeline
2. **Complexity**: Two new analytical models with different physics
3. **Data**: Incomplete TAS data (missing critical features)
4. **Risk**: High probability of degrading existing model
5. **Scope**: Would significantly expand thesis beyond original objectives

### How Future Work Can Integrate

1. **Phase 1**: Develop analytical models (2-3 weeks)
2. **Phase 2**: Generate synthetic data and engineer features (2-3 weeks)
3. **Phase 3**: Retrain model with 5 classes (1 week)
4. **Phase 4**: Integrate into system (2 weeks)
5. **Phase 5**: Test and validate (1 week)

**Total**: 8-11 weeks with proper planning and resources

### What to Do Now

1. **Acknowledge scope** in background section
2. **Document future work** with detailed roadmap
3. **Show extensibility** in discussion
4. **Create integration plan** as supporting document

**Result**: Thesis that demonstrates comprehensive understanding, acknowledges commercial solutions, shows extensibility, and provides clear future work path—all while maintaining focus and quality.

---

## Appendix: Technical Specifications for Future Implementation

### A.1 Shrink Disc Analytical Model Structure

```python
# Pseudo-code structure
def shrink_disc_capacity(...):
    """
    Inputs:
    - d: shaft diameter
    - dw: working diameter (where clamping occurs)
    - L: engagement length
    - Z: number of clamping elements
    - MA: assembly torque per clamping element
    - e, H: clamping geometry
    - I: interference
    - material properties
    
    Outputs:
    - Mt_total: total torque capacity
    - Mt_interference: interference fit contribution
    - Mt_clamping: clamping element contribution
    - p_interference: interference pressure
    - p_clamping: clamping pressure
    """
    pass
```

### A.2 Locking Assembly Analytical Model Structure

```python
# Pseudo-code structure
def locking_assembly_capacity(...):
    """
    Inputs:
    - d: shaft diameter
    - D: outer diameter
    - L: engagement length
    - Z: number of clamping elements
    - MA: assembly torque
    - material properties
    
    Outputs:
    - Mt: torque capacity
    - Fax: axial force capacity
    - p_clamping: clamping pressure
    """
    pass
```

### A.3 Extended Feature Set

**New Features for Shrink Discs**:
- `working_diameter` (dw)
- `clamping_elements` (Z)
- `assembly_torque` (MA)
- `clamping_geometry_e` (e)
- `clamping_geometry_H` (H)
- `interference` (I)

**New Features for Locking Assemblies**:
- `clamping_elements` (Z)
- `assembly_torque` (MA)
- `axial_force_capacity` (Fax)
- `working_pressure` (pW)
- `nominal_pressure` (pN)

**Common New Feature**:
- `connection_type` (categorical: press/key/spline/shrink_disc/locking)

---

**Document Version**: 1.0  
**Date**: 2025-01-XX  
**Author**: Thesis Analysis  
**Status**: Final Recommendation


