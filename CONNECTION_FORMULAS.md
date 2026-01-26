# Formulas for Shaft-Hub Connections

Complete list of formulas for each connection type from the thesis, ready to paste into Gemini.

---

## PRESS FITS (Friction Closure) - DIN 7190

### Basic Torque Transmission

**Contact Area:**
```
A_contact = π × d × L
```
where:
- d = shaft diameter
- L = engagement length

**Torque Capacity:**
```
M_t,press = (π/2) × μ × p × L × d²
```
or equivalently:
```
M_t,press = μ × p × A_contact × (d/2)
```
where:
- μ = friction coefficient
- p = interface pressure
- L = engagement length
- d = shaft diameter

**Required Interface Pressure:**
```
p_req = (2 × M_req × S_R) / (π × μ × L × d²)
```
where:
- M_req = required torque
- S_R = safety factor (applied to torque demand)

### Allowable Pressure

**Effective Allowable Pressure:**
```
p_allow = min(p_allow,shaft, p_allow,hub)
```

**Allowable Stress (Material-Dependent):**
```
σ_zul = {
    σ_y / S_F,  if ductile material
    σ_uts / S_B, if brittle material
}
```
where:
- σ_y = yield strength
- σ_uts = ultimate tensile strength
- S_F = safety factor for yield-based limits
- S_B = safety factor for ultimate-based limits

**Geometric Ratios:**
```
Q_A = d / D    (hub wall thickness ratio)
Q_I = d_i / d  (shaft hollowness ratio)
```
where:
- D = hub outer diameter
- d_i = shaft inner diameter (zero for solid shafts)

**Component-Specific Pressure Limits:**
```
p_allow,hub = ((1 - Q_A²) / √3) × σ_zul,hub

p_allow,shaft = (2 / √3) × σ_zul,shaft × (1 - Q_I²)
```

**Mechanical Feasibility:**
```
p_req ≤ p_allow
```

### Von Mises Yield Criterion

**Von Mises Equivalent Stress (Biaxial Stress State):**
```
σ_vM = √(σ_θ² - σ_θ × σ_r + σ_r²)
```
where:
- σ_θ = circumferential (hoop) stress
- σ_r = radial stress

The factor 1/√3 in the pressure limit equations arises from applying the von Mises criterion to the biaxial stress state in cylindrical components.

---

## PARALLEL KEYS (Form Closure) - DIN 6885

### Torque Capacity - Two Failure Modes

**Shear Failure (Shear-Limited Capacity):**
```
T_τ = τ_allow × b × L × (d/2)
```
where:
- τ_allow = allowable shear stress of key material
- b = key width
- L = engagement length
- d = shaft diameter

**Bearing Failure (Bearing-Pressure-Limited Capacity):**
```
T_p = p_allow × (h/2) × L × (d/2)
```
where:
- p_allow = allowable bearing pressure
- h = key height
- L = engagement length
- d = shaft diameter
- h/2 = effective moment arm for bearing force

**Governing Torque Capacity:**
```
M_t,key = min(T_τ, T_p)
```
The transmissible torque is governed by the more restrictive of the two failure modes.

**Effective Allowable Bearing Pressure (Multi-Material):**
```
p_allow = min(p_allow,shaft, p_allow,hub)
```
For keyed connections involving different shaft and hub materials, the allowable bearing pressure is conservatively taken as the minimum of both material allowables.

---

## SPLINES (Form Closure) - DIN 5480

### Geometric Parameters

**Projected Flank Height:**
```
h_proj = (D - d) / 2
```
where:
- D = outer diameter of spline
- d = inner diameter of spline

**Projected Flank Area:**
```
A_proj = z × b × h_proj
```
where:
- z = number of teeth
- b = tooth width (circumferential dimension)
- h_proj = projected flank height

**Mean Radius (Effective Lever Arm):**
```
r_m = (d + D) / 4
```
The mean radius represents the effective moment arm for torque transmission (average of inner and outer radii).

**Effective Flank Height:**
```
h_eff ≈ 0.8 × h_proj
```
The 0.8 factor is an empirical/conservative reduction to account for non-uniform contact along the tooth height (edge contact, micro-misalignment, manufacturing tolerances).

### Torque Capacity

**Spline Torque Capacity:**
```
M_t,spline = K × L × z × h_eff × r_m × p_allow
```
where:
- K = load-sharing factor (K = 0.75 in this work)
  - Accounts for non-uniform load distribution across teeth
  - Conservative reduction for manufacturing tolerances, elastic deformation, geometric misalignment
- L = engagement length
- z = number of teeth
- h_eff = effective flank height (≈ 0.8 × h_proj)
- r_m = mean radius ((d + D) / 4)
- p_allow = maximum allowable contact (bearing) pressure on spline flanks

**Load-Sharing Factor:**
The factor K = 0.75 is used to represent load-sharing losses and practical non-uniformities. In reality, not all teeth carry equal load; some teeth are loaded more heavily due to small geometric errors and elastic deformation.

---

## SUMMARY OF KEY FORMULAS

### Press Fit Torque:
```
M_t,press = (π/2) × μ × p × L × d²
```

### Key Torque:
```
M_t,key = min(τ_allow × b × L × d/2,  p_allow × h/2 × L × d/2)
```

### Spline Torque:
```
M_t,spline = 0.75 × L × z × (0.8 × h_proj) × r_m × p_allow
```
where:
- h_proj = (D - d) / 2
- r_m = (d + D) / 4

---

## NOTES FOR PRESENTATION

1. **Safety Factor:** In press fits, safety factor S_R is applied to torque demand (M_req × S_R), not to capacity.

2. **Governing Failure Mode:** For keys, the governing capacity is the minimum of shear and bearing capacities. Bearing pressure often governs, especially for larger shafts or softer hub materials.

3. **Load Sharing:** Splines use a conservative factor K = 0.75 to account for non-uniform load distribution across teeth.

4. **Effective Allowables:** For multi-material connections (press fits and keys), the effective allowable is taken as the minimum of shaft and hub material allowables.

5. **Von Mises Criterion:** The factor 1/√3 in press fit pressure limits comes from applying the von Mises yield criterion to the biaxial stress state (radial and circumferential stresses).

6. **Geometric Ratios:** 
   - Q_A = d/D (hub wall thickness) - as Q_A → 1, hub becomes thinner, allowable pressure decreases
   - Q_I = d_i/d (shaft hollowness) - as Q_I increases, shaft becomes more hollow, allowable pressure decreases

