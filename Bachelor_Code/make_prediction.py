# make_prediction.py
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
import math
import numpy as np

#add more criteria according to book:
#maintenance(repair), durability
#press fit is easier for repair compared to keys and splines
#hub outer diameter: stiff/fleixible
#reduce torque margin dominance
#for friction lookup, add more materials:
#use DIN table and consider the following factors:
#machining: rough, fine
#hardness
#material
#treatment
#lubrication
#choose smaller value
#add steel, cast iron

# -----------------------
# Global settings
# -----------------------
MARGIN_TIE_BAND = 0.35
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
    ("Steel C45", "Steel C45"): 0.18,   # default mid-conservative for steel–steel
    ("Aluminum 6061", "Aluminum 6061"): 0.22,  # default for Al–Al
}
#machining: rough, fine
#hardness
#material
#treatment
#lubrication
#choose smaller value
#add steel, cast iron

def mu_for(a: str, b: str, override: float | None = None) -> float:
    """
    Return μ. If 'override' is provided, clamp to a sane range [0.05, 0.5] and use it.
    Otherwise fall back to the pair lookup (symmetric), and if missing -> 0.18.
    """
    if override is not None:
        return max(0.05, min(0.50, float(override)))
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
    ease: float
    movement: float
    cost: float
    bidirectional: float

# reward not cost
# CONN_PROFILE = {
#     "press":  {"assembly/disassembly_ease": 0.25, "manufacturing_cost": 0.60, "movement_ease": 0.05, "bidirectional": 0.10},
#     "key":    {"assembly/disassembly_ease": 0.70, "manufacturing_cost": 0.25, "movement_ease": 0.20, "bidirectional": 0.20},
#     "spline": {"assembly/disassembly_ease": 0.90, "manufacturing_cost": 0.15, "movement_ease": 0.75, "bidirectional": 0.70},
# }

CONN_PROFILE = {
    # Press fit: cheapest, compact, but poor for repeated dis/assembly or sliding motion
    "press": {
        "assembly/disassembly_ease": 0.20,  # heat/press needed; not service-friendly
        "manufacturing_cost":        0.75,  # turning + bore tolerance only (cheapest)
        "movement_ease":             0.05,  # not suited to frequent axial movement
        "bidirectional":             0.60,  # symmetric torque, but micro-slip risk under reversals
    },

    # Keyed: very serviceable, moderate cost, okay for occasional movement, some backlash
    "key": {
        "assembly/disassembly_ease": 0.65,  # quick install/remove 
        "manufacturing_cost":        0.45,  # broach + keyway in hub (medium)
        "movement_ease":             0.35,  # can slide with clearance; not ideal for constant motion
        "bidirectional":             0.55,  # works both ways, but fretting/backlash can appear
    },

    # Spline: best for frequent movement & high cyclic/bidirectional torque; expensive
    "spline": {
        "assembly/disassembly_ease": 0.85,  # easy axial slide/locate, but alignment needed
        "manufacturing_cost":        0.20,  # spline cutting/grinding (expensive/inspection-heavy)
        "movement_ease":             0.85,  # designed for frequent sliding/locational accuracy
        "bidirectional":             0.90,  # excellent for reversing & high-cycle loads
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
# Scoring (feasible-only)
# -----------------------
def score_candidate(conn: str, Mt_cap: float, M_req: float,
                    d_mm: float, L_mm: float, prefs: UserPrefs,
                    weights = {
                        "margin":   0.30,   # reward for useful safety margin
                        "prefs":    0.70,   # user intent drives choice  
                        "overkill": 0.10,   # SMALL penalty for excessive overdesign
                    },
                    margin_cap: float = 0.35  # +35% surplus capacity treated as fully useful
                    ) -> float:
    """
    User-preference-first scoring with minimal overkill penalty.
    Strong user preferences can overcome moderate overdesign penalties.
    """
    
    # 1) Margin with diminishing returns
    margin_raw = max(0.0, (Mt_cap - M_req) / max(M_req, 1e-6))
    
    # Useful margin (0-35%) gets full reward
    margin_useful = min(margin_raw, margin_cap) / margin_cap
    s_margin = weights["margin"] * margin_useful

    # SMALL overkill penalty (>35%) - just enough to nudge away from extreme overdesign
    overkill = max(0.0, margin_raw - margin_cap)
    s_overkill = -weights["overkill"] * overkill

    # 2) User preferences (dominant factor)
    prof = CONN_PROFILE[conn]
    pref_util = (
        prefs.ease          * prof.get("assembly/disassembly_ease", 0.0) +
        prefs.movement      * prof.get("movement_ease", 0.0) +
        prefs.cost          * prof.get("manufacturing_cost", 0.0) +
        prefs.bidirectional * prof.get("bidirectional", 0.0)
    )
    s_prefs = weights["prefs"] * pref_util

    return s_margin + s_overkill + s_prefs
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

    # User preferences (only axes present in CONN_PROFILE will be used in scoring)
    prefs = UserPrefs(
        ease=request.user_preferences.ease,
        movement=request.user_preferences.movement,
        cost=request.user_preferences.cost,
        bidirectional=request.user_preferences.bidirectional
    )

    # Friction μ (allow override)
    mu = mu_for(
        request.shaft_material,
        request.hub_material,
        getattr(request, "mu_override", None)
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
            "input_parameters": request.dict(),
            "details": {"press": pf, "key": key, "spline": spline}
        }

    # Score only feasible candidates (your scoring already ignores non-profile axes)
    scores = {k: score_candidate(k, v, M_req, d, request.hub_length, prefs) for k, v in feasible.items()}
    best_connection = max(scores.items(), key=lambda x: x[1])[0]

    return {
        "recommended_connection": best_connection,
        "required_torque_Nmm": M_req,
        "capacities_Nmm": candidates,
        "scores": scores,
        "feasible": True,
        "mu_used": mu,
        "input_parameters": request.dict(),
        "details": {"press": pf, "key": key, "spline": spline}
    }
