# make_prediction.py
# Enhanced with professor's feedback: expanded materials, DIN friction tables,
# hub stiffness consideration, corrected maintenance values, durability criterion
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
import math
import numpy as np

# -----------------------
# Global settings
# -----------------------
MARGIN_TIE_BAND = 0.35
RNG_SEED_DEFAULT = 7

# -----------------------
# Materials & allowables (expanded per professor's notes)
# -----------------------
# Material properties based on DIN standards
# E = Young's modulus (MPa), nu = Poisson's ratio
# sigma_yield = yield strength (MPa), sigma_uts = ultimate tensile strength (MPa)
# SF = safety factor for ductile, SB = safety factor for brittle
# tau_allow_key = allowable shear stress for keys (MPa)
# p_allow_key = allowable bearing pressure for keys (MPa)
# p_allow_spline = allowable bearing pressure for splines (MPa)

materials = {
    # Steels
    "Steel S235": {
        "E": 210000.0, "nu": 0.30,
        "sigma_yield": 235.0, "sigma_uts": 360.0,
        "ductile": True, "SF": 1.5, "SB": 2.5,
        "tau_allow_key": 45.0,
        "p_allow_key":   70.0,
        "p_allow_spline": 55.0,
        "category": "steel"
    },
    "Steel C45": {
        "E": 210000.0, "nu": 0.30,
        "sigma_yield": 340.0, "sigma_uts": 600.0,
        "ductile": True, "SF": 1.5, "SB": 2.5,
        "tau_allow_key": 60.0,
        "p_allow_key":   90.0,
        "p_allow_spline": 70.0,
        "category": "steel"
    },
    "Steel 42CrMo4": {
        "E": 210000.0, "nu": 0.30,
        "sigma_yield": 650.0, "sigma_uts": 900.0,
        "ductile": True, "SF": 1.5, "SB": 2.5,
        "tau_allow_key": 100.0,
        "p_allow_key":   150.0,
        "p_allow_spline": 120.0,
        "category": "steel"
    },
    # Stainless Steel
    "Stainless 304": {
        "E": 193000.0, "nu": 0.29,
        "sigma_yield": 215.0, "sigma_uts": 505.0,
        "ductile": True, "SF": 1.6, "SB": 2.5,
        "tau_allow_key": 40.0,
        "p_allow_key":   65.0,
        "p_allow_spline": 50.0,
        "category": "steel"
    },
    # Cast Irons
    "Cast Iron GG25": {
        "E": 110000.0, "nu": 0.26,
        "sigma_yield": 165.0, "sigma_uts": 250.0,  # No clear yield, use 0.2% proof
        "ductile": False, "SF": 2.0, "SB": 3.0,   # Brittle - higher safety factors
        "tau_allow_key": 30.0,
        "p_allow_key":   50.0,
        "p_allow_spline": 40.0,
        "category": "cast_iron"
    },
    "Cast Iron GGG40": {
        "E": 169000.0, "nu": 0.275,
        "sigma_yield": 250.0, "sigma_uts": 400.0,
        "ductile": True, "SF": 1.6, "SB": 2.5,    # Ductile iron
        "tau_allow_key": 50.0,
        "p_allow_key":   75.0,
        "p_allow_spline": 60.0,
        "category": "cast_iron"
    },
    # Bronze
    "Bronze CuSn8": {
        "E": 110000.0, "nu": 0.34,
        "sigma_yield": 150.0, "sigma_uts": 300.0,
        "ductile": True, "SF": 1.6, "SB": 2.5,
        "tau_allow_key": 30.0,
        "p_allow_key":   45.0,
        "p_allow_spline": 35.0,
        "category": "bronze"
    },
    # Aluminum
    "Aluminum 6061": {
        "E": 69000.0, "nu": 0.33,
        "sigma_yield": 95.0, "sigma_uts": 290.0,
        "ductile": True, "SF": 1.6, "SB": 2.5,
        "tau_allow_key": 25.0,
        "p_allow_key":   40.0,
        "p_allow_spline": 30.0,
        "category": "aluminum"
    },
    "Aluminum 7075": {
        "E": 71700.0, "nu": 0.33,
        "sigma_yield": 503.0, "sigma_uts": 572.0,
        "ductile": True, "SF": 1.6, "SB": 2.5,
        "tau_allow_key": 80.0,
        "p_allow_key":   120.0,
        "p_allow_spline": 95.0,
        "category": "aluminum"
    },
}

# -----------------------
# Friction coefficients based on DIN 7190-1 Table 1
# -----------------------
# Format: (shaft_category, hub_category, surface_condition) -> μ
# surface_condition: "dry", "oiled", "greased"
# Using CONSERVATIVE (lower) values per professor's guidance

FRICTION_TABLE_DIN = {
    # Steel - Steel
    ("steel", "steel", "dry"):      0.12,   # DIN 7190: 0.12-0.20, use lower
    ("steel", "steel", "oiled"):    0.08,   # DIN 7190: 0.08-0.12
    ("steel", "steel", "greased"):  0.06,   # With grease lubrication
    
    # Steel - Cast Iron
    ("steel", "cast_iron", "dry"):      0.10,   # DIN 7190: 0.10-0.16
    ("steel", "cast_iron", "oiled"):    0.06,   # DIN 7190: 0.06-0.10
    ("steel", "cast_iron", "greased"):  0.05,
    
    # Steel - Bronze
    ("steel", "bronze", "dry"):      0.08,   # DIN 7190: 0.08-0.14
    ("steel", "bronze", "oiled"):    0.05,   # DIN 7190: 0.05-0.08
    ("steel", "bronze", "greased"):  0.04,
    
    # Steel - Aluminum
    ("steel", "aluminum", "dry"):      0.10,
    ("steel", "aluminum", "oiled"):    0.07,
    ("steel", "aluminum", "greased"):  0.05,
    
    # Cast Iron - Cast Iron
    ("cast_iron", "cast_iron", "dry"):      0.10,
    ("cast_iron", "cast_iron", "oiled"):    0.06,
    ("cast_iron", "cast_iron", "greased"):  0.04,
    
    # Aluminum - Aluminum
    ("aluminum", "aluminum", "dry"):      0.15,   # Higher for Al-Al
    ("aluminum", "aluminum", "oiled"):    0.10,
    ("aluminum", "aluminum", "greased"):  0.08,
    
    # Bronze - Bronze
    ("bronze", "bronze", "dry"):      0.08,
    ("bronze", "bronze", "oiled"):    0.05,
    ("bronze", "bronze", "greased"):  0.04,
}

def get_material_category(mat_name: str) -> str:
    """Get the category of a material for friction lookup."""
    if mat_name in materials:
        return materials[mat_name].get("category", "steel")
    return "steel"  # Default

def mu_for(shaft_mat: str, hub_mat: str, 
           surface_condition: str = "dry",
           override: float | None = None) -> float:

    """
    Return friction coefficient μ based on DIN 7190-1.
    
    Args:
        shaft_mat: Shaft material name
        hub_mat: Hub material name
        surface_condition: "dry", "oiled", or "greased"
        override: Manual override value (clamped to 0.05-0.50)
    
    Returns:
        Friction coefficient (conservative/lower value per DIN guidance)
    """
    if override is not None:
        return max(0.05, min(0.50, float(override)))
    
    cat_shaft = get_material_category(shaft_mat)
    cat_hub = get_material_category(hub_mat)
    
    # Try both orderings (symmetric lookup)
    key1 = (cat_shaft, cat_hub, surface_condition)
    key2 = (cat_hub, cat_shaft, surface_condition)
    
    if key1 in FRICTION_TABLE_DIN:
        return FRICTION_TABLE_DIN[key1]
    if key2 in FRICTION_TABLE_DIN:
        return FRICTION_TABLE_DIN[key2]
    
    # Fallback: conservative steel-steel dry
    return 0.12

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
# User preferences (8 criteria total)
# -----------------------
@dataclass
class UserPrefs:
    ease: float           # importance of assembly/disassembly ease
    movement: float       # importance of frequent axial movement capability
    cost: float           # importance of low manufacturing cost
    bidirectional: float  # importance of bidirectional torque capability
    vibration: float      # importance of vibration resistance
    speed: float          # importance of high-speed suitability
    maintenance: float    # importance of easy maintenance/repair (replacement simplicity)
    durability: float     # importance of fatigue life / durability under cyclic loads

# Full engineering profile with 8 criteria
# MAINTENANCE: Per professor's note - press fit is EASIER for repair because replacement
# only requires simple cylindrical machining, while key/spline need matching geometry
# DURABILITY: Based on fatigue behavior - splines distribute load best, keys have stress concentration
CONN_PROFILE = {
    # Press fit: cheapest, excellent vibration/speed, easy repair (simple geometry)
    "press": {
        "assembly/disassembly_ease": 0.15,  # requires special equipment (press/heating)
        "manufacturing_cost":        0.80,  # cheapest: only toleranced turning/boring
        "movement_ease":             0.00,  # zero - it's a permanent fit
        "bidirectional":             0.95,  # excellent: symmetric friction, no backlash
        "vibration_resistance":      0.90,  # excellent damping due to friction interface
        "high_speed_suitability":    0.95,  # no moving parts, perfect balance possible
        "maintenance_ease":          0.70,  # CORRECTED: easy repair - just machine new cylinder
        "durability":                0.60,  # fretting fatigue at interface under cyclic loads
    },

    # Keyed: easy assembly, but repair needs new keyway, poor fatigue at keyway corners
    "key": {
        "assembly/disassembly_ease": 0.70,  # slide-in, screw/tap out
        "manufacturing_cost":        0.45,  # medium: keyway broaching required
        "movement_ease":             0.30,  # possible with clearance fit, not intended
        "bidirectional":             0.35,  # poor: backlash causes hammering under reversals
        "vibration_resistance":      0.40,  # backlash amplifies vibration
        "high_speed_suitability":    0.55,  # imbalance from keyway, stress concentration
        "maintenance_ease":          0.40,  # CORRECTED: repair needs matching keyway (broaching)
        "durability":                0.35,  # stress concentration at keyway corners
    },

    # Spline: best for movement & bidirectional, good fatigue life, expensive repair
    "spline": {
        "assembly/disassembly_ease": 0.80,  # easy axial insertion, but alignment critical
        "manufacturing_cost":        0.15,  # expensive: hobbing/grinding + inspection
        "movement_ease":             0.90,  # designed for this purpose
        "bidirectional":             0.85,  # very good: multiple teeth share load symmetrically
        "vibration_resistance":      0.70,  # good load distribution, some play possible
        "high_speed_suitability":    0.85,  # symmetric, self-centering
        "maintenance_ease":          0.25,  # CORRECTED: repair needs matching spline (expensive)
        "durability":                0.85,  # distributed load = best fatigue life
    },
}


# -----------------------
# Press-fit equations
# -----------------------
def sigma_zul(mat: Dict[str, Any]) -> float:
    if mat.get("ductile", True):
        return mat["sigma_yield"] / max(mat.get("SF", 1.5), 1.2)
    return mat["sigma_uts"] / max(mat.get("SB", 2.5), 2.0)

# KEEP this version
def p_allow_pressfit(shaft_type: str,
                     shaft_mat: Dict[str, Any], hub_mat: Dict[str, Any],
                     dF_mm: float,
                     DiI_mm: Optional[float], DaA_mm: Optional[float]) -> float:
    """
    Allowable pressure is the minimum of shaft and hub sides (DIN-style).
    For solid: QI = 0. For hub OD, default to 2*d if not provided.
    """
    dF = float(dF_mm)

    if shaft_type == "hollow":
        if DiI_mm is None:
            raise ValueError("Hollow shaft requires shaft_inner_diameter (DiI_mm).")
        if not (0.0 < float(DiI_mm) < dF):
            raise ValueError("shaft_inner_diameter must be in (0, shaft_diameter).")
        QI = float(DiI_mm) / dF
    else:
        QI = 0.0

    DaA_eff = float(DaA_mm) if DaA_mm is not None else 2.0 * dF
    if not (DaA_eff > dF):
        raise ValueError("hub_outer_diameter (DaA) must be > shaft_diameter.")
    QA = dF / DaA_eff

    p_shaft = 0.80 * sigma_zul(shaft_mat) * (1.0 - QI**2)
    p_hub   = 0.80 * sigma_zul(hub_mat)   * (1.0 - QA**2)
    return min(p_shaft, p_hub)


def p_required_pressfit(M_req_Nmm: float, d_mm: float, L_mm: float, mu: float, S_R: float) -> float:
    """
    Required contact pressure to transmit torque with slip safety S_R.
    DIN 7190-1 Eq. (1):  T = (π/2) * D * l * ν_ru * (p / S_r)
    => p = (2 * T * S_R) / (π * D * l * μ).
    """
    return (2.0 * M_req_Nmm * S_R) / (math.pi * mu * d_mm * L_mm)

def elastic_interference(dF_mm: float, p_MPa: float,
                         E_I: float, nu_I: float, QI: float,
                         E_A: float, nu_A: float, QA: float) -> float:
    return p_MPa * dF_mm * (((1.0+nu_I)/E_I)/(1.0 - QI**2) + ((1.0+nu_A)/E_A)/(1.0 - QA**2))

def smoothing_G(RzI_um: float, RzA_um: float) -> float:
    """
    DIN 7190-1: use glättungsfaktor g_F = 0.4 for both longitudinal/transverse fits:
    Uw = U - 0.4 * (RzA + RzI). Convert μm -> mm here.
    """
    return 0.4 * (RzI_um + RzA_um) / 1000.0  # was 0.8

# KEEP this version
def pressfit_capacity(M_req_Nmm: float,
                      d_mm: float, L_mm: float,
                      shaft_type: str,
                      shaft_mat_name: str, hub_mat_name: str,
                      mu: float, S_R: float,
                      DiI_mm: Optional[float], DaA_mm: Optional[float]) -> Dict[str, Any]:
    shaft_mat, hub_mat = materials[shaft_mat_name], materials[hub_mat_name]

    p_erf = (2.0 * M_req_Nmm * S_R) / (math.pi * mu * d_mm * L_mm)
    p_zul = p_allow_pressfit(shaft_type, shaft_mat, hub_mat, d_mm, DiI_mm, DaA_mm)

    Mt_from_pzul = (math.pi * mu * d_mm * L_mm * p_zul) / 2.0
    return {"p_erf": p_erf, "p_zul": p_zul, "Mt_from_pzul": Mt_from_pzul}



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
# Hub stiffness evaluation (for press fit penalty)
# -----------------------
def calculate_hub_stiffness_factor(d_mm: float, DaA_mm: Optional[float]) -> float:
    """
    Calculate hub stiffness factor based on wall thickness ratio QA = d/DaA.
    
    Returns a factor 0-1 where:
    - 1.0 = thick-walled hub (QA < 0.5), suitable for press fits
    - 0.0 = very thin-walled hub (QA > 0.8), risky for press fits
    
    Per professor's note: thin/flexible hubs are problematic for press fits
    due to stress concentration and potential plastic deformation.
    """
    if DaA_mm is None or DaA_mm <= d_mm:
        return 0.5  # Unknown geometry, neutral
    
    QA = d_mm / DaA_mm  # Wall thickness ratio
    
    if QA < 0.5:
        return 1.0   # Thick-walled: excellent for press fit
    elif QA < 0.6:
        return 0.85  # Good
    elif QA < 0.7:
        return 0.60  # Acceptable but not ideal
    elif QA < 0.8:
        return 0.30  # Thin: problematic for press fits
    else:
        return 0.10  # Very thin: press fit risky

# -----------------------
# Scoring (feasible-only) with 8 criteria + hub stiffness
# -----------------------
def score_candidate(conn: str, Mt_cap: float, M_req: float,
                    d_mm: float, L_mm: float, prefs: UserPrefs,
                    DaA_mm: Optional[float] = None,
                    weights = {
                        "margin":       0.20,   # reward for useful safety margin
                        "prefs":        0.70,   # user intent drives choice (8 criteria)
                        "overkill":     0.06,   # SMALL penalty for excessive overdesign
                        "hub_stiffness": 0.10,  # penalty for press fit on thin hubs
                    },
                    margin_cap: float = 0.35  # +35% surplus capacity treated as fully useful
                    ) -> float:
    """
    User-preference-first scoring with 8 criteria + hub stiffness consideration.
    
    Criteria: ease, movement, cost, bidirectional, vibration, speed, maintenance, durability.
    
    Hub stiffness penalty: Applies to press fits when hub wall is thin (QA > 0.6).
    Per professor's guidance on stiff/flexible hub consideration.
    """
    
    # 1) Margin with diminishing returns
    margin_raw = max(0.0, (Mt_cap - M_req) / max(M_req, 1e-6))
    margin_useful = min(margin_raw, margin_cap) / margin_cap
    s_margin = weights["margin"] * margin_useful

    # SMALL overkill penalty (>35%)
    overkill = max(0.0, margin_raw - margin_cap)
    s_overkill = -weights["overkill"] * overkill

    # 2) User preferences (dominant factor) - all 8 criteria
    prof = CONN_PROFILE[conn]
    pref_util = (
        prefs.ease          * prof.get("assembly/disassembly_ease", 0.0) +
        prefs.movement      * prof.get("movement_ease", 0.0) +
        prefs.cost          * prof.get("manufacturing_cost", 0.0) +
        prefs.bidirectional * prof.get("bidirectional", 0.0) +
        prefs.vibration     * prof.get("vibration_resistance", 0.0) +
        prefs.speed         * prof.get("high_speed_suitability", 0.0) +
        prefs.maintenance   * prof.get("maintenance_ease", 0.0) +
        prefs.durability    * prof.get("durability", 0.0)
    )
    # Normalize by number of criteria (8)
    s_prefs = weights["prefs"] * pref_util

    # 3) Hub stiffness penalty (only for press fits)
    s_hub_stiffness = 0.0
    if conn == "press" and DaA_mm is not None:
        hub_factor = calculate_hub_stiffness_factor(d_mm, DaA_mm)
        # Penalty when hub is thin (factor < 1.0)
        # Thin hub = lower factor = higher penalty
        s_hub_stiffness = weights["hub_stiffness"] * (hub_factor - 1.0)  # Negative when thin

    return s_margin + s_overkill + s_prefs + s_hub_stiffness
# -----------------------
# Torque demand calculation
# -----------------------
def calculate_required_torque(d_mm: float, shaft_mat_name: str, torque_coefficient: float = 135.0) -> float:
    Wt = math.pi * (d_mm**3) / 16.0
    taper = 1.0 if d_mm <= 40 else 0.9 if d_mm <= 70 else 0.8
    return 0.05 * torque_coefficient * Wt * taper

# -----------------------
# Main selection function
# -----------------------
def select_shaft_connection(request) -> Dict[str, Any]:
    # Validate enums/materials
    if request.shaft_material not in materials:
        raise HTTPException(status_code=400, detail=f"Invalid shaft material: {request.shaft_material}")
    if request.hub_material not in materials:
        raise HTTPException(status_code=400, detail=f"Invalid hub material: {request.hub_material}")
    if request.shaft_type not in ["solid", "hollow"]:
        raise HTTPException(status_code=400, detail="Shaft type must be 'solid' or 'hollow'")

    # REQUIRED torque (no more estimating)
    if request.required_torque is None:
        raise HTTPException(status_code=400, detail="required_torque is mandatory")
    M_req = float(request.required_torque)


        # User preferences - all 8 criteria
    prefs = UserPrefs(
        ease=request.user_preferences.ease,
        movement=request.user_preferences.movement,
        cost=request.user_preferences.cost,
        bidirectional=request.user_preferences.bidirectional,
        vibration=request.user_preferences.vibration,
        speed=request.user_preferences.speed,
        maintenance=request.user_preferences.maintenance,
        durability=request.user_preferences.durability,
    )


        # Friction μ (allow override)
    mu = mu_for(
        request.shaft_material,
        request.hub_material,
        surface_condition=getattr(request, "surface_condition", "dry"),
        override=getattr(request, "mu_override", None),
    )


    # Geometry & defaults
    d = request.shaft_diameter
    L_press = max(request.hub_length, 1.5 * d)  # same guard as before
    DiI_mm = request.shaft_inner_diameter if request.shaft_type == "hollow" else None
    DaA_mm = request.hub_outer_diameter if request.hub_outer_diameter is not None else 2.0 * d

    # Capacities
    try:
        pf = pressfit_capacity(
            M_req, d, L_press,
            request.shaft_type, request.shaft_material, request.hub_material,
            mu, request.safety_factor,
            DiI_mm, DaA_mm
        )
        Mt_press = pf["Mt_from_pzul"]
    except Exception as e:
        pf = {"error": str(e)}
        Mt_press = 0.0

    key = key_capacity(d, request.hub_length, request.shaft_material)
    spline = spline_capacity(d, request.shaft_material)

    candidates = {"press": Mt_press, "key": key["Mt"], "spline": spline["Mt"]}
    feasible = {k: v for k, v in candidates.items() if v >= M_req}

    if not feasible:
        return {
            "recommended_connection": "none",
            "reason": "No connection type can safely transmit the required torque",
            "required_torque_Nmm": M_req,
            "capacities_Nmm": candidates,
            "feasible": False,
            "mu_used": mu,
            "scores": None,
            "surface_condition": request.surface_condition,  # 👈 add this
            "hub_stiffness_factor": calculate_hub_stiffness_factor(d, DaA_mm),
            "input_parameters": request.dict(),
            "details": {"press": pf, "key": key, "spline": spline},
        }

        
    # Score only feasible candidates (your scoring already ignores non-profile axes)
    scores = {k: score_candidate(k, v, M_req, d, request.hub_length, prefs) for k, v in feasible.items()}
    best_connection = max(scores.items(), key=lambda x: x[1])[0]

    return {
        "recommended_connection": best_connection,
        "required_torque_Nmm": M_req,
        "capacities_Nmm": candidates,
        "scores": scores,
        "hub_stiffness_factor": calculate_hub_stiffness_factor(d, DaA_mm),
        "feasible": True,
        "mu_used": mu,
        "surface_condition": request.surface_condition,  # 👈 add this
        "input_parameters": request.dict(),
        "details": {"press": pf, "key": key, "spline": spline},
    }


