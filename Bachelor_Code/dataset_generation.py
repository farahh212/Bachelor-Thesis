# -*- coding: utf-8 -*-
"""
synthetic_SHC_dataset_DIN_full_PATCHED.py

Tuning to make press fits realistically feasible and occasionally preferred:
- μ: Steel→0.18, Al→0.22
- p_allow_pressfit factor: 0.80 * σ_zul (was 2/3)
- Demand softened: 0.05 * coef * Wt with coef in [70, 200] (was 0.06 * [80, 220])
- Engagement for press capacity: L_press = max(L, 1.5D)
- Preference model includes: ease (assembly+manufacturing), movement, cost, vibration, speed, bidirectional
- Tie band widened to 1.0 (all feasibles compete); scoring weights let prefs break near-ties.
- Safety gate (Mt ≥ M_req) intact.

Units: stress MPa (N/mm²), length mm, torque N·mm.
"""

import math
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List

# -----------------------
# Global settings
# -----------------------
MARGIN_TIE_BAND = 0.35  # instead of 1.00
RNG_SEED_DEFAULT = 7

# -----------------------
# Materials & allowables
# -----------------------
materials = {
    "Steel C45": {
        "E": 210000.0, "nu": 0.30,
        "sigma_yield": 340.0, "sigma_uts": 600.0,
        "ductile": True, "SF": 1.5, "SB": 2.5,
        "tau_allow_key": 60.0,
        "p_allow_key":   90.0,
        "p_allow_spline": 70.0
    },
    "Aluminum 6061": {
        "E": 69000.0, "nu": 0.33,
        "sigma_yield": 95.0, "sigma_uts": 290.0,
        "ductile": True, "SF": 1.6, "SB": 2.5,
        "tau_allow_key": 25.0,
        "p_allow_key":   40.0,
        "p_allow_spline": 30.0
    },
}

# -----------------------
# Friction pairs (μ)
# -----------------------
friction_lookup = {
    ("Steel C45", "Steel C45"): 0.18,
    ("Aluminum 6061", "Aluminum 6061"): 0.22,
}
def mu_for(a: str, b: str) -> float:
    return friction_lookup.get((a, b)) or friction_lookup.get((b, a), 0.18)

# -----------------------
# Spline & key tables
# -----------------------
spline_table = [
    {"d_max": 11, "D": 14, "N": 6, "B": 3},
    {"d_max": 13, "D": 16, "N": 6, "B": 3},
    {"d_max": 16, "D": 20, "N": 6, "B": 4},
    {"d_max": 18, "D": 22, "N": 6, "B": 4},
    {"d_max": 21, "D": 25, "N": 6, "B": 6},
    {"d_max": 23, "D": 26, "N": 6, "B": 6},
    {"d_max": 26, "D": 30, "N": 6, "B": 6},
    {"d_max": 28, "D": 32, "N": 6, "B": 7},
    {"d_max": 32, "D": 36, "N": 8, "B": 6},
    {"d_max": 36, "D": 40, "N": 8, "B": 7},
    {"d_max": 42, "D": 46, "N": 8, "B": 8},
    {"d_max": 46, "D": 50, "N": 8, "B": 9},
    {"d_max": 52, "D": 58, "N": 8, "B": 10},
    {"d_max": 56, "D": 62, "N": 8, "B": 10},
    {"d_max": 62, "D": 68, "N": 8, "B": 12},
    {"d_max": 72, "D": 78, "N": 10, "B": 12},
    {"d_max": 82, "D": 88, "N": 10, "B": 12},
    {"d_max": 92, "D": 98, "N": 10, "B": 14},
    {"d_max": 102, "D": 108, "N": 10, "B": 16},
    {"d_max": 112, "D": 120, "N": 10, "B": 18},
]
def spline_geometry_from_d_lookup(d_mm: float) -> Tuple[int, float, float, float]:
    for row in spline_table:
        if d_mm <= row["d_max"]:
            D, z, b = row["D"], row["N"], row["B"]
            h_proj = 0.5 * (D - d_mm)
            return z, h_proj, D, b
    last = spline_table[-1]
    D = last["D"] + 0.5 * (d_mm - last["d_max"])
    return last["N"], 0.5 * (D - d_mm), D, last["B"]

key_table = [
    {"d_min": 6, "d_max": 8, "b": 2, "h": 2},
    {"d_min": 8, "d_max": 10, "b": 3, "h": 3},
    {"d_min": 10, "d_max": 12, "b": 4, "h": 4},
    {"d_min": 12, "d_max": 17, "b": 5, "h": 5},
    {"d_min": 17, "d_max": 22, "b": 6, "h": 6},
    {"d_min": 22, "d_max": 30, "b": 8, "h": 7},
    {"d_min": 30, "d_max": 38, "b": 10, "h": 8},
    {"d_min": 38, "d_max": 44, "b": 12, "h": 8},
    {"d_min": 44, "d_max": 50, "b": 14, "h": 9},
    {"d_min": 50, "d_max": 58, "b": 16, "h": 10},
    {"d_min": 58, "d_max": 65, "b": 18, "h": 11},
    {"d_min": 65, "d_max": 75, "b": 20, "h": 12},
    {"d_min": 75, "d_max": 85, "b": 22, "h": 14},
    {"d_min": 85, "d_max": 95, "b": 25, "h": 14},
    {"d_min": 95, "d_max": 110, "b": 28, "h": 16},
    {"d_min": 110, "d_max": 130, "b": 32, "h": 18},
    {"d_min": 130, "d_max": 150, "b": 36, "h": 20},
    {"d_min": 150, "d_max": 170, "b": 40, "h": 22},
    {"d_min": 170, "d_max": 200, "b": 45, "h": 25},
    {"d_min": 200, "d_max": 230, "b": 50, "h": 28},
]
def key_geometry_from_d(d_mm: float) -> Tuple[float, float]:
    for row in key_table:
        if row["d_min"] < d_mm <= row["d_max"]:
            return float(row["b"]), float(row["h"])
    last = key_table[-1]
    return float(last["b"]), float(last["h"])

# -----------------------
# User preferences
# -----------------------
@dataclass
class UserPrefs:
    ease: float          # importance of ease (assembly + manufacturing)
    movement: float      # importance of frequent repositioning
    cost: float          # importance of low cost (benefit)
    vibration: float     # importance of vibration robustness
    speed: float         # importance of high speed suitability
    bidirectional: float # importance of symmetric torque transmission

def sample_user_prefs(rng: np.random.Generator) -> UserPrefs:
    return UserPrefs(
        ease=float(rng.uniform(0.0, 1.0)),
        movement=float(rng.uniform(0.0, 1.0)),
        cost=float(rng.uniform(0.0, 1.0)),
        vibration=float(rng.uniform(0.0, 1.0)),
        speed=float(rng.uniform(0.0, 1.0)),
        bidirectional=float(rng.choice([0.0, 1.0]))  # 50/50 toggle; adjust if needed
    )

# Connection performance ratings (0..1); "cost" here is a BENEFIT.
# NOTE: use keys aligned with scoring: "ease" + "manufacturing" + others.
CONN_PROFILE = {
    "press":  {"ease": 0.25, "manufacturing": 0.65, "movement": 0.20, "cost": 1.00, "vibration": 0.85, "speed": 0.75, "bidirectional": 1.00},
    "key":    {"ease": 0.70, "manufacturing": 0.35, "movement": 0.50, "cost": 0.60, "vibration": 0.50, "speed": 0.60, "bidirectional": 0.50},
    "spline": {"ease": 0.90, "manufacturing": 0.20, "movement": 0.90, "cost": 0.10, "vibration": 0.90, "speed": 1.00, "bidirectional": 0.70},
}

# -----------------------
# Press-fit equations
# -----------------------
def sigma_zul(mat: Dict[str, Any]) -> float:
    if mat.get("ductile", True):
        return mat["sigma_yield"] / max(mat.get("SF", 1.5), 1.2)
    return mat["sigma_uts"] / max(mat.get("SB", 2.5), 2.0)

def p_allow_pressfit(shaft_type: str,
                     shaft_mat: Dict[str, Any], hub_mat: Dict[str, Any],
                     dF_mm: float,
                     DiI_mm: Optional[float], DaA_mm: Optional[float]) -> float:
    # More generous than 2/3: use 0.80 * σ_zul (your patch)
    if shaft_type == "solid":
        return 0.80 * sigma_zul(shaft_mat)
    if DiI_mm is None or DaA_mm is None:
        raise ValueError("Hollow shaft requires DiI and DaA.")
    QI = DiI_mm / dF_mm
    QA = dF_mm / DaA_mm
    p_shaft = 0.80 * sigma_zul(shaft_mat) * (1.0 - QI**2)
    p_hub   = 0.80 * sigma_zul(hub_mat)   * (1.0 - QA**2)
    return min(p_shaft, p_hub)

def p_required_pressfit(M_req_Nmm: float, d_mm: float, L_mm: float, mu: float, S_R: float) -> float:
    return (2.0 * M_req_Nmm) / (math.pi * mu * d_mm * L_mm * S_R)

def elastic_interference(dF_mm: float, p_MPa: float,
                         E_I: float, nu_I: float, QI: float,
                         E_A: float, nu_A: float, QA: float) -> float:
    return p_MPa * dF_mm * (((1.0+nu_I)/E_I)/(1.0 - QI**2) + ((1.0+nu_A)/E_A)/(1.0 - QA**2))

def smoothing_G(RzI_um: float, RzA_um: float) -> float:
    return 0.8 * (RzI_um + RzA_um) / 1000.0

def pressfit_capacity(M_req_Nmm: float,
                      d_mm: float, L_mm: float,
                      shaft_type: str,
                      shaft_mat_name: str, hub_mat_name: str,
                      RzI_um: float, RzA_um: float,
                      mu: float, S_R: float,
                      DiI_mm: Optional[float], DaA_mm: Optional[float],
                      assembly_method: str = "heat_hub",
                      tU_C: float = 20.0,
                      alpha_I: float = 12e-6, alpha_A: float = 12e-6) -> Dict[str, Any]:
    shaft_mat, hub_mat = materials[shaft_mat_name], materials[hub_mat_name]
    dF = d_mm

    p_erf = p_required_pressfit(M_req_Nmm, d_mm, L_mm, mu, S_R)
    p_zul = p_allow_pressfit(shaft_type, shaft_mat, hub_mat, dF, DiI_mm, DaA_mm)

    QI = (DiI_mm / dF) if (shaft_type == "hollow" and DiI_mm) else 0.0
    QA = (dF / DaA_mm) if DaA_mm else 0.0

    Z_erf = elastic_interference(dF, p_erf, shaft_mat["E"], shaft_mat["nu"], QI,
                                 hub_mat["E"], hub_mat["nu"], QA)
    Z_zul = elastic_interference(dF, p_zul, shaft_mat["E"], shaft_mat["nu"], QI,
                                 hub_mat["E"], hub_mat["nu"], QA)

    G = smoothing_G(RzI_um, RzA_um)
    U_erf, U_zul = Z_erf + G, Z_zul + G

    # Nominal interference inside safe window
    lam = 0.60
    U_span = max(0.0, U_zul - U_erf)
    U_nom = min(max(U_erf + lam * U_span, U_erf), U_zul)

    # Simple tolerance allocation (radial)
    tol_shaft_mm = 0.60 * U_nom
    tol_hub_mm   = 0.40 * U_nom

    # Transmissible torque at allowable pressure
    Mt_from_pzul = (math.pi * mu * d_mm * L_mm * p_zul) / 2.0

    # Assembly temperature estimate (ΔD = 0.001 D)
    dD = 0.001 * dF
    Ug = U_zul
    tA = tI = None
    if assembly_method == "heat_hub":
        tA = tU_C + (Ug + dD) / (alpha_A * dF)
    elif assembly_method == "cool_shaft":
        tI = tU_C + (Ug + dD) / (alpha_I * dF)

    return {
        "p_erf": p_erf, "p_zul": p_zul, "Z_erf": Z_erf, "Z_zul": Z_zul,
        "G": G, "U_erf": U_erf, "U_zul": U_zul,
        "U_nom": U_nom, "tol_shaft_mm": tol_shaft_mm, "tol_hub_mm": tol_hub_mm,
        "QI": QI, "QA": QA,
        "Mt_from_pzul": Mt_from_pzul, "assembly_method": assembly_method,
        "tA": tA, "tI": tI
    }

# -----------------------
# Keys & splines capacity
# -----------------------
def key_capacity(d_mm: float, l_key_mm: float, shaft_mat_name: str) -> Dict[str, Any]:
    b_mm, h_mm = key_geometry_from_d(d_mm)
    mat = materials[shaft_mat_name]
    tau_allow = mat["tau_allow_key"]
    p_allow   = mat["p_allow_key"]

    A_shear = b_mm * l_key_mm
    A_bear  = (h_mm / 2.0) * l_key_mm
    r = 0.5 * d_mm

    T_tau = tau_allow * A_shear * r
    T_p   = p_allow   * A_bear  * r
    return {"Mt": min(T_tau, T_p), "b_mm": b_mm, "h_mm": h_mm, "l_mm": l_key_mm}

def spline_capacity(d_mm: float, shaft_mat_name: str) -> Dict[str, Any]:
    z, h_proj_mm, D_mm, b_mm = spline_geometry_from_d_lookup(d_mm)
    mat = materials[shaft_mat_name]
    p_allow = mat["p_allow_spline"]

    projected = z * h_proj_mm * b_mm
    r = 0.5 * d_mm
    Mt = p_allow * projected * r
    return {"Mt": Mt, "z": z, "b_mm": b_mm, "h_proj_mm": h_proj_mm, "D_mm": D_mm}

# -----------------------
# Scoring (feasible-only)
# -----------------------
def score_candidate(conn: str, Mt_cap: float, M_req: float,
                    d_mm: float, L_mm: float, prefs: UserPrefs,
                    weights = {"margin":0.40, "size":0.08, "mass":0.07, "cost":0.15, "prefs":0.30}) -> float:
    # 1) Physics margin
    margin = max(0.0, (Mt_cap - M_req) / max(M_req, 1e-6))
    s_margin = weights["margin"] * margin

    # 2) Compactness penalties
    size_pen = weights["size"] * ((d_mm/50.0) + (L_mm/50.0))
    mass_pen = weights["mass"] * ((d_mm**2 * L_mm) / (50.0**2 * 50.0))

    # 3) Baseline cost penalty (higher = more expensive)
    base_cost_pen = {"spline": 1.2, "key": 0.8, "press": 0.0}.get(conn, 0.5)
    s_base_cost = weights["cost"] * (-base_cost_pen)

    # 4) Preference utility (dot-product)
    prof = CONN_PROFILE[conn]

    # Combine ease of assembly + manufacturing into one effective "ease" axis
    ease_effective = 0.6 * prof["ease"] + 0.4 * prof["manufacturing"]

    pref_util = (
        prefs.ease          * ease_effective +
        prefs.movement      * prof["movement"] +
        prefs.cost          * prof["cost"] +          # cost is a BENEFIT here
        prefs.vibration     * prof["vibration"] +
        prefs.speed         * prof["speed"] +
        prefs.bidirectional * prof["bidirectional"]
    )
    s_prefs = weights["prefs"] * pref_util

    # 5) Final score
    return s_margin + s_base_cost + s_prefs - (size_pen + mass_pen)

# -----------------------
# Torque demand (softer)
# -----------------------

def sample_required_torque(rng, d_mm, shaft_mat_name):
    coef = float(rng.uniform(70.0, 200.0))
    Wt = math.pi * (d_mm**3) / 16.0
    # taper demand for large diameters (piecewise)
    taper = 1.0 if d_mm <= 40 else 0.9 if d_mm <= 70 else 0.8
    return 0.05 * coef * Wt * taper


# -----------------------
# One sample
# -----------------------
def generate_one_sample(rng: np.random.Generator,
                        d_mm: float,
                        shaft_mat_name: str,
                        hub_mat_name: str,
                        shaft_type: str = "solid",
                        method: str = "heat_hub",
                        user_prefs: Optional[UserPrefs] = None) -> Dict[str, Any]:
    # Random bending (70% bending per your patch)
    bending_flag = bool(rng.random() < 0.70)
    L_mm = d_mm if bending_flag else 0.5 * d_mm
    L_rule = "D" if bending_flag else "0.5D"

    M_req = sample_required_torque(rng, d_mm, shaft_mat_name)

    # Surface & friction
    RzI_um = float(rng.uniform(6.0, 20.0))
    RzA_um = float(rng.uniform(6.0, 20.0))
    mu = mu_for(shaft_mat_name, hub_mat_name)
    S_R = float(rng.choice([1.3, 1.5, 1.7]))

    # Geometry
    DiI_mm = float(rng.uniform(0.45, 0.70) * d_mm) if shaft_type == "hollow" else None
    DaA_mm = float(rng.uniform(1.7, 2.5) * d_mm)

    # Press: use longer engagement per your patch
    L_press = max(L_mm, 1.5 * d_mm)

    pf = pressfit_capacity(M_req, d_mm, L_press,
                           shaft_type, shaft_mat_name, hub_mat_name,
                           RzI_um, RzA_um, mu, S_R,
                           DiI_mm, DaA_mm, assembly_method=method)
    Mt_press = pf["Mt_from_pzul"]

    # Key uses L_mm as length
    key = key_capacity(d_mm, L_mm, shaft_mat_name)
    Mt_key = key["Mt"]

    # Spline
    spline = spline_capacity(d_mm, shaft_mat_name)
    Mt_spline = spline["Mt"]

    # Preferences
    prefs = user_prefs or sample_user_prefs(rng)

    # Safety gate
    candidates = {"press": Mt_press, "key": Mt_key, "spline": Mt_spline}
    feasible = {k: v for k, v in candidates.items() if v >= M_req}

    if not feasible:
        label, label_score, Mt_label = "none", float("-inf"), None
        scores = {}
    else:
        scores = {k: score_candidate(k, v, M_req, d_mm, L_mm, prefs) for k, v in feasible.items()}
        margins = {k: (feasible[k] - M_req) / max(M_req, 1e-9) for k in feasible}
        best_margin = max(margins.values())
        # Wide tie-band: all feasibles essentially compete
        keep = {k for k, m in margins.items() if (best_margin - m) <= MARGIN_TIE_BAND * max(1e-9, best_margin)}
        banded_scores = {k: scores[k] for k in keep}
        label, label_score = max(banded_scores.items(), key=lambda kv: kv[1])
        Mt_label = feasible[label]

    # Row
    row = {
        "d_mm": d_mm, "L_mm": L_mm, "L_rule": L_rule, "bending": bending_flag,
        "shaft_mat": shaft_mat_name, "hub_mat": hub_mat_name, "shaft_type": shaft_type,
        "DiI_mm": DiI_mm, "DaA_mm": DaA_mm, "mu": mu, "S_R": S_R, "RzI_um": RzI_um, "RzA_um": RzA_um,
        "M_req_Nmm": M_req,
        # Press block
        **pf,
        "Mt_press": Mt_press,
        # Key
        "key_b_mm": key["b_mm"], "key_h_mm": key["h_mm"], "key_l_mm": key["l_mm"], "Mt_key": Mt_key,
        # Spline
        "spline_z": spline["z"], "spline_b_mm": spline["b_mm"],
        "spline_hproj_mm": spline["h_proj_mm"], "spline_D_mm": spline["D_mm"], "Mt_spline": Mt_spline,
        # Label
        "label": label, "label_score": label_score, "Mt_label": Mt_label,
        # User prefs written to CSV
        "pref_ease": prefs.ease, "pref_movement": prefs.movement,
        "pref_cost": prefs.cost, "pref_vibration": prefs.vibration,
        "pref_speed": prefs.speed, "pref_bidirectional": prefs.bidirectional,
    }
    for k in ["press", "key", "spline"]:
        row[f"score_{k}"] = scores.get(k, None)
    return row

# -----------------------
# Dataset driver
# -----------------------
def generate_dataset(n_samples: int = 800, seed: int = RNG_SEED_DEFAULT,
                     target_mix: Optional[Dict[str, float]] = None,
                     fixed_prefs: Optional[UserPrefs] = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    diameter_pool = np.array([8,10,12,14,16,18,20,25,30,35,40,45,50,60,70,80,90,100], dtype=float)

    rows: List[Dict[str, Any]] = []
    for _ in range(n_samples):
        want = None
        if target_mix:
            want = rng.choice(list(target_mix.keys()), p=np.array(list(target_mix.values())))

        d_mm = float(rng.choice(diameter_pool))
        shaft_mat = str(rng.choice(list(materials.keys())))
        hub_mat = shaft_mat

        shaft_type = "hollow" if ((want == "press") and (rng.random() < 0.20)) else ("hollow" if rng.random() < 0.20 else "solid")
        method = "heat_hub"

        row = generate_one_sample(rng, d_mm, shaft_mat, hub_mat, shaft_type, method,
                                  user_prefs=(fixed_prefs or None))

        tries = 0
        while target_mix and row["label"] == "none" and tries < 2:
            d_mm = float(rng.choice(diameter_pool))
            shaft_type = "hollow" if ((want == "press") and (rng.random() < 0.25)) else ("hollow" if rng.random() < 0.20 else "solid")
            row = generate_one_sample(rng, d_mm, shaft_mat, hub_mat, shaft_type, method,
                                      user_prefs=(fixed_prefs or None))
            tries += 1

        rows.append(row)

    return pd.DataFrame(rows)

# -----------------------
# CLI
# -----------------------
if __name__ == "__main__":
    target = {"press": 0.34, "key": 0.33, "spline": 0.33}
    # If you want fixed (non-random) user prefs for the whole dataset, uncomment:
    # fixed = UserPrefs(ease=0.7, movement=0.5, cost=0.9, vibration=0.6, speed=0.5, bidirectional=1.0)
    fixed = None

    df = generate_dataset(800, seed=RNG_SEED_DEFAULT, target_mix=target, fixed_prefs=fixed)

    print("\nLabel counts (including 'none' if any):")
    print(df["label"].value_counts(dropna=False))

    # Safety validation — all labeled options must satisfy Mt ≥ M_req
    bad_press = df[(df["label"]=="press")  & (df["Mt_press"]  < df["M_req_Nmm"])]
    bad_key   = df[(df["label"]=="key")    & (df["Mt_key"]    < df["M_req_Nmm"])]
    bad_spl   = df[(df["label"]=="spline") & (df["Mt_spline"] < df["M_req_Nmm"])]

    print(f"\nSafety check — violating rows (should all be zero):")
    print(f"  press:  {len(bad_press)}")
    print(f"  key:    {len(bad_key)}")
    print(f"  spline: {len(bad_spl)}")

    # Feasibility fractions (diagnostic)
    for col in ["Mt_press","Mt_key","Mt_spline"]:
        feasible_frac = (df[col] >= df["M_req_Nmm"]).mean()
        print(f"Feasible fraction for {col}: {feasible_frac:.3f}")

    out = "synthetic_SHC_dataset_DIN_full_PATCHED.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved {out}")
    print(df['label'].value_counts())
