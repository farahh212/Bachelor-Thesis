# TAS Schafer: Shrink Discs vs Locking Assemblies - Detailed Breakdown

## Overview

TAS Schafer provides **two distinct product types**, each requiring separate analytical models and integration approaches:

1. **Shrink Discs** (3-part, 2-part variants)
2. **Locking Assemblies** (3015, 3015.1, RB variants)

---

## Type 1: Shrink Discs

### Data Files
- `Shrink disc 3-part.csv` (~64 rows)
- `Shrink disc 2-part_3371.csv` (~50-60 rows)
- `Shrink disc 2-part_3171.csv` (~55 rows)
- **Total: ~170 rows**

### Key Features (from CSV)
```
d (mm)        - Shaft diameter
dw (mm)       - Working diameter (clamping surface)
M max (Nm)    - Maximum transmissible torque
D (mm)        - Outer diameter
I (mm)        - Interference
e (mm)        - Clamping element geometry
H (mm)        - Clamping element height
A (mm)        - Hub length/engagement length
d1 (mm)       - Inner diameter (if applicable)
MA (Nm)       - Assembly torque (for clamping screws)
Z (Stk.)      - Number of clamping elements
pN (N/mm²)    - Nominal pressure
nmax (min-1)  - Maximum speed
I (kgm²)      - Moment of inertia
Gewicht (kg)  - Weight
```

### Physics & Mechanism
- **Base**: Interference fit (like press fit)
- **Enhancement**: Clamping elements (Z screws) that apply additional radial pressure
- **Torque transmission**: Combination of:
  1. Interference fit friction (like press fit)
  2. Clamping element pressure (additional contribution)
- **Working diameter (dw)**: Smaller than shaft diameter (d), where clamping occurs

### Analytical Model Requirements
1. **Interference fit component** (similar to press fit)
2. **Clamping element contribution**:
   - Pressure from Z clamping elements
   - Assembly torque (MA) relationship
   - Geometry factors (e, H)
3. **Combined torque capacity**: Interference + clamping

### Integration Complexity: **HIGH**
- Need new analytical equations
- Different geometry (dw vs d)
- Clamping element physics
- Assembly torque considerations

---

## Type 2: Locking Assemblies

### Data Files
- `Locking assembly_3015.csv` (35 rows)
- `Locking assembly_3015.1.csv` (35 rows)
- `Locking assembly_RB.csv` (33 rows)
- **Total: ~103 rows**

### Key Features (from CSV)
```
d (mm)        - Shaft diameter
D (mm)        - Outer diameter
Mt (Nm)       - Maximum transmissible torque
Fax (Nm)      - Maximum axial force
pW (N/mm²)    - Working pressure
pN (N/mm²)    - Nominal pressure
Z (Stk.)      - Number of clamping elements
MA (Nm)       - Assembly torque
L (mm)        - Total length
L1 (mm)       - Length dimension 1
L2 (mm)       - Length dimension 2
Gewicht (kg)  - Weight
```

### Physics & Mechanism
- **Base**: Different from shrink discs
- **Mechanism**: Clamping elements apply pressure directly (not interference-based)
- **Torque transmission**: Primarily from clamping element pressure
- **Axial force (Fax)**: Can also transmit axial loads (not just torque)
- **Two pressure types**: pW (working) and pN (nominal)

### Analytical Model Requirements
1. **Clamping element pressure calculation**
2. **Torque from pressure**: Different relationship than interference fits
3. **Axial force capacity**: Fax calculation
4. **Assembly torque**: MA relationship to clamping pressure

### Integration Complexity: **VERY HIGH**
- Completely different mechanism than shrink discs
- No interference fit component
- Axial force considerations (new dimension)
- Different pressure definitions (pW vs pN)

---

## Combined Integration Requirements

### If Integrating BOTH Types:

#### 1. Analytical Pipeline
- ✅ Current: Press fit, Key, Spline
- ❌ **NEW**: Shrink disc model (interference + clamping)
- ❌ **NEW**: Locking assembly model (pure clamping)

**Total models needed**: 5 (press, key, spline, shrink_disc, locking_assembly)

#### 2. Feature Engineering

**Common features for both TAS types**:
- `clamping_elements` (Z) - numeric
- `assembly_torque` (MA) - numeric
- `connection_type` - categorical

**Shrink disc specific**:
- `working_diameter` (dw) - numeric
- `clamping_geometry_e` (e) - numeric
- `clamping_geometry_H` (H) - numeric
- `interference` (I) - numeric

**Locking assembly specific**:
- `axial_force_capacity` (Fax) - numeric
- `working_pressure` (pW) - numeric
- `nominal_pressure` (pN) - numeric

**Total new features**: ~10-12 (vs current 18)

#### 3. Dataset Structure

**Current**: 4,993 rows, 3 classes
**After integration**:
- Existing: 4,993 (press/key/spline)
- TAS real: ~273 (shrink disc ~170, locking ~103)
- TAS synthetic: ~4,000-5,000 (generated)
- **Total**: ~9,000-10,000 rows, **5 classes**

**Class distribution**:
- press: ~800 (8-9%)
- key: ~1,400 (15-16%)
- spline: ~2,700 (29-30%)
- shrink_disc: ~2,500-3,000 (28-33%)
- locking_assembly: ~1,500-2,000 (17-22%)

#### 4. Model Complexity

**Current model**:
- 3 classes
- 18 features
- 4,993 samples
- Performance: 91.27% accuracy

**New model**:
- **5 classes** (67% more classes)
- **28-30 features** (67% more features)
- **9,000-10,000 samples** (100% more data)
- **Severe class imbalance** (shrink_disc dominates)

**Risk**: High probability of degraded performance on original 3 classes

---

## Effort Breakdown by Type

### Shrink Discs Only
- Analytical model: 1.5-2 weeks
- Dataset generation: 1 week
- Feature engineering: 0.5 week
- **Subtotal: 3-3.5 weeks**

### Locking Assemblies Only
- Analytical model: 1.5-2 weeks (different physics)
- Dataset generation: 1 week
- Feature engineering: 0.5 week
- **Subtotal: 3-3.5 weeks**

### Both Types (Full Integration)
- Analytical models: 2-3 weeks (both types)
- Dataset generation: 1.5-2 weeks (both types)
- Feature engineering: 1 week (handle both)
- Model retraining: 1 week
- Frontend/backend: 2 weeks
- Testing: 1 week
- **Total: 8.5-11 weeks**

---

## Key Differences Summary

| Aspect | Shrink Discs | Locking Assemblies |
|--------|-------------|-------------------|
| **Base mechanism** | Interference fit + clamping | Pure clamping |
| **Working diameter** | Yes (dw < d) | No |
| **Interference** | Yes (I) | No |
| **Axial force** | Limited | Yes (Fax) |
| **Pressure types** | pN only | pW and pN |
| **Clamping geometry** | e, H parameters | Simpler |
| **Data rows** | ~170 | ~103 |
| **Complexity** | High | Very High |
| **Analytical model** | Interference + clamping | Pure clamping |

---

## Recommendation Impact

### If integrating BOTH types:

**Pros**:
- ✅ More comprehensive coverage
- ✅ Shows both TAS product lines
- ✅ Demonstrates extensibility

**Cons**:
- ❌ **DOUBLE the analytical work** (2 different models)
- ❌ **DOUBLE the complexity** (2 different physics)
- ❌ **More features** (10-12 new vs 5-6 for one type)
- ❌ **More class imbalance** (2 new classes vs 1)
- ❌ **Higher risk** (more moving parts)
- ❌ **Longer timeline** (8.5-11 weeks vs 4-5 weeks for one type)

### Recommendation Remains: **DO NOT integrate**

**Reasons**:
1. **Two different analytical models** needed (not just one)
2. **Different physics** for each type
3. **Even more complex** than initially assessed
4. **Timeline**: 8.5-11 weeks is definitely too long
5. **Risk**: Higher with two new types

---

## Alternative: Comparative Analysis for BOTH Types

### Approach
1. **Shrink Discs**:
   - Map parameters to model inputs
   - Run predictions (expect "press" class)
   - Compare with catalog M_max
   - Explain: clamping elements add capacity beyond pure press fit

2. **Locking Assemblies**:
   - Map parameters to model inputs
   - Run predictions (may not match any class well)
   - Compare with catalog Mt
   - Explain: different mechanism, model doesn't apply

### Thesis Integration
- **Background**: Discuss both shrink discs AND locking assemblies
- **Related Work**: Mention TAS Schafer product lines
- **Results**: Two case studies (one for each type)
- **Discussion**: Model boundaries for both types

### Effort: **1-2 weeks** (same as before, just more examples)

---

## Conclusion

Having **both shrink discs and locking assemblies** actually makes full integration **MORE complex**, not less:

- **Two analytical models** instead of one
- **Different physics** for each
- **More features** to handle
- **More classes** to learn
- **Longer timeline** (8.5-11 weeks)

**Recommendation**: Use **comparative analysis** for both types, which:
- ✅ Handles both product lines
- ✅ Shows understanding of differences
- ✅ Low risk, high value
- ✅ Feasible timeline (1-2 weeks)

This approach allows you to discuss both TAS product types in your thesis without the massive integration effort.


