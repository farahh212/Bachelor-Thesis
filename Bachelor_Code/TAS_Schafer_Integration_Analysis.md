# TAS Schafer Data Integration Analysis

## Executive Summary

This document analyzes the feasibility of integrating TAS Schafer shrink disc data into the existing shaft-hub connection selection framework. The analysis considers data compatibility, model requirements, and multiple integration strategies.

## Current System Overview

### Dataset Structure
- **Synthetic Dataset**: 4,993 rows
- **Features**: 15 numeric + 3 categorical
  - Numeric: `shaft_diameter`, `hub_length`, `has_bending`, `safety_factor`, `hub_outer_diameter`, `shaft_inner_diameter`, `required_torque`, 8 preference weights
  - Categorical: `shaft_type`, `shaft_material`, `surface_condition`
- **Labels**: `press`, `key`, `spline`
- **Class Distribution**: 54.7% spline, 28.6% key, 16.8% press fit

### Model Status
- **Trained and Tested**: CatBoost classifier with 91.27% accuracy
- **Performance**: F1-scores: Spline (0.9127), Key (0.8057), Press (0.6774)
- **Hybrid Approach**: ML predictions + analytical validation

## TAS Schafer Data Characteristics

### Data Structure (from Excel analysis)
Based on the `analyze_tas_data.py` script, TAS Schafer data contains:
- **Rows**: <100 samples
- **Columns**: Different schema including:
  - `d (mm)` - shaft diameter
  - `dw (mm)` - working diameter
  - `M max (Nm)` - maximum torque
  - `D (mm)` - outer diameter
  - `I (mm)` - interference
  - `e (mm)`, `H (mm)`, `A (mm)`, `d1 (mm)` - geometric parameters
  - `MA (Nm)` - assembly torque
  - `Z (Stk.)` - number of clamping elements
  - `nmax (min-1)` - maximum speed
  - `pN (N/mm²)` - pressure
  - `I (kgm²)` - moment of inertia
  - `Gewicht (kg)` - weight

### Key Differences
1. **Clamping Element**: TAS shrink discs use an additional clamping mechanism (Z clamping elements)
2. **Feature Mismatch**: Many TAS-specific features don't map to standard press/key/spline features
3. **Missing Features**: TAS data lacks:
   - User preferences (8 preference weights)
   - Surface condition information
   - Material specifications (may be implicit)
   - Safety factor (may need derivation)
4. **Different Physics**: Shrink discs with clamping elements operate differently than pure interference fits

## Integration Challenges

### 1. Feature Incompatibility
- **Problem**: TAS data has different features (clamping elements, assembly torque, etc.)
- **Impact**: Cannot directly use TAS data as training samples without feature engineering
- **Complexity**: High - would require significant pipeline modifications

### 2. Small Sample Size
- **Problem**: <100 rows vs. 4,993 synthetic rows
- **Impact**: Even if integrated, TAS data would represent <2% of dataset
- **Risk**: Model may not learn TAS-specific patterns; other types would dominate

### 3. Different Connection Type
- **Problem**: Shrink discs with clamping elements are a hybrid between press fits and form closure
- **Impact**: Doesn't fit cleanly into `press`/`key`/`spline` classification
- **Consideration**: Would need a 4th class or special handling

### 4. Analytical Pipeline Mismatch
- **Problem**: Current analytical pipeline generates pure press/key/spline fits
- **Impact**: Cannot generate synthetic shrink disc data using existing pipeline
- **Complexity**: Would require new analytical models for shrink discs

## Integration Options

### Option 1: Mention in Related Work (RECOMMENDED)
**Approach**: Include TAS Schafer as a case study in related work/discussion

**Pros**:
- ✅ No code changes required
- ✅ Acknowledges industrial relevance
- ✅ Discusses limitations of current approach
- ✅ Shows awareness of commercial solutions
- ✅ Can discuss why shrink discs weren't included (different physics, insufficient data)

**Cons**:
- ❌ Doesn't directly integrate the data
- ❌ May not fully satisfy professor's request

**Implementation**:
- Add section in related work discussing commercial shrink disc solutions
- Mention TAS Schafer as example
- Explain why shrink discs differ from standard interference fits
- Discuss data availability challenges

**Thesis Sections to Modify**:
- `thesis/sections/background.tex` - Add subsection on shrink discs
- `thesis/sections/discussion.tex` - Discuss limitations and future work

### Option 2: Comparative Analysis Section
**Approach**: Add a dedicated section comparing analytical predictions with TAS Schafer catalog data

**Pros**:
- ✅ Uses TAS data without modifying model
- ✅ Provides validation against real-world data
- ✅ Shows model's applicability boundaries
- ✅ Demonstrates industrial relevance

**Cons**:
- ❌ Requires manual mapping of TAS parameters
- ❌ May show model limitations (which could be good for discussion)

**Implementation**:
1. Map TAS parameters to model inputs (where possible)
2. Run model predictions on TAS cases
3. Compare with TAS catalog torque ratings
4. Analyze discrepancies (due to clamping elements)
5. Discuss implications

**Thesis Sections to Add**:
- New section: "Industrial Case Study: TAS Schafer Shrink Discs"
- Compare model predictions vs. catalog values
- Discuss why shrink discs outperform pure press fits

### Option 3: Feature Engineering + Limited Integration
**Approach**: Map TAS features to model features, add as separate class or special handling

**Pros**:
- ✅ Directly uses TAS data
- ✅ Shows integration capability

**Cons**:
- ❌ High complexity (new class, feature engineering)
- ❌ Small sample size (<2% of dataset)
- ❌ Model retraining required
- ❌ May degrade performance on existing classes
- ❌ Requires new analytical models

**Implementation Complexity**: Very High
- Feature mapping script
- New class label "shrink_disc"
- Model retraining
- New analytical shrink disc capacity function
- Updated scoring logic

### Option 4: Separate Validation Dataset
**Approach**: Use TAS data as external validation, not training data

**Pros**:
- ✅ Uses TAS data meaningfully
- ✅ No model changes required
- ✅ Provides real-world validation

**Cons**:
- ❌ Requires parameter mapping
- ❌ May show model doesn't apply to shrink discs (expected)

**Implementation**:
1. Map TAS parameters to closest model inputs
2. Run predictions (expecting "press" class)
3. Compare torque capacities
4. Document that shrink discs exceed pure press fit capacity due to clamping

## Recommended Approach: Hybrid (Options 1 + 2)

### Phase 1: Related Work Integration
1. **Add shrink disc discussion to background**:
   - Explain shrink discs as interference fits with clamping elements
   - Mention TAS Schafer as commercial example
   - Discuss why they weren't included (different physics, data limitations)

2. **Add to discussion/limitations**:
   - Acknowledge that commercial solutions exist
   - Explain scope limitations (pure press/key/spline)
   - Discuss future work: shrink disc integration

### Phase 2: Comparative Analysis
1. **Create TAS comparison script**:
   - Map TAS parameters to model inputs
   - Run model predictions
   - Compare with catalog values
   - Analyze differences

2. **Add case study section**:
   - Present comparison results
   - Explain why shrink discs outperform pure press fits
   - Discuss model's applicability boundaries

## Implementation Steps

### Step 1: Analyze TAS Data Structure
```python
# Run existing analyze_tas_data.py to understand data
# Identify mappable parameters:
# - d (mm) → shaft_diameter
# - M max (Nm) → required_torque (for comparison)
# - D (mm) → hub_outer_diameter
# - I (mm) → interference (for validation)
```

### Step 2: Create Mapping Script
```python
# tas_to_model_inputs.py
# Map TAS parameters to model features where possible
# Handle missing features with defaults or estimates
```

### Step 3: Run Comparative Analysis
```python
# compare_tas_predictions.py
# 1. Load TAS data
# 2. Map to model inputs
# 3. Run model predictions
# 4. Compare with TAS catalog M_max values
# 5. Generate comparison report
```

### Step 4: Thesis Integration
- Add background section on shrink discs
- Add case study section with comparison results
- Update discussion/limitations
- Add to future work

## Expected Outcomes

### Positive Outcomes
1. **Academic Rigor**: Shows awareness of commercial solutions and limitations
2. **Industrial Relevance**: Demonstrates connection to real-world applications
3. **Validation**: Provides external validation of model (even if limited)
4. **Discussion Material**: Rich material for limitations and future work sections

### Potential Challenges
1. **Model Limitations**: May show model doesn't apply to shrink discs (expected and acceptable)
2. **Data Gaps**: Missing features require assumptions
3. **Comparison Complexity**: Different physics make direct comparison difficult

## Conclusion

**Recommended Strategy**: **Options 1 + 2 (Related Work + Comparative Analysis)**

This approach:
- ✅ Satisfies professor's request to "include the company somehow"
- ✅ Maintains model integrity (no retraining needed)
- ✅ Provides valuable discussion material
- ✅ Shows industrial awareness
- ✅ Demonstrates model boundaries
- ✅ Low risk, high value

**Not Recommended**: Option 3 (Full Integration)
- Too complex for thesis timeline
- Small sample size would be dominated
- Requires significant pipeline changes
- May degrade model performance

## Next Steps

1. **Immediate**: Run `analyze_tas_data.py` to get full data structure
2. **Week 1**: Create parameter mapping script
3. **Week 1**: Run comparative analysis
4. **Week 2**: Write thesis sections (background, case study, discussion)
5. **Week 2**: Review with professor

## Files to Create/Modify

### New Files
- `Bachelor_Code/tas_comparison_analysis.py` - Comparative analysis script
- `Bachelor_Code/tas_parameter_mapping.py` - Parameter mapping utilities

### Modified Files
- `thesis/sections/background.tex` - Add shrink disc subsection
- `thesis/sections/discussion.tex` - Add limitations and future work
- `thesis/sections/results.tex` - Add TAS case study section (optional)


