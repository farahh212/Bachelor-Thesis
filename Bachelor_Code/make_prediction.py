# make_prediction.py
from fastapi import HTTPException
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import math
import numpy as np

# -----------------------
# Global settings
# -----------------------
MARGIN_TIE_BAND = 0.35
RNG_SEED_DEFAULT = 7

# -----------------------
# Materials & allowables
# -----------------------
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
        "sigma_yield": 165.0, "sigma_uts": 250.0,
        "ductile": False, "SF": 2.0, "SB": 3.0,
        "tau_allow_key": 30.0,
        "p_allow_key":   50.0,
        "p_allow_spline": 40.0,
        "category": "cast_iron"
    },
    "Cast Iron GGG40": {
        "E": 169000.0, "nu": 0.275,
        "sigma_yield": 250.0, "sigma_uts": 400.0,
        "ductile": True, "SF": 1.6, "SB": 2.5,
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
    # Exercise materials
    "Steel E360": {
        "E": 210000.0, "nu": 0.30,
        "sigma_yield": 355.0,
        "sigma_uts": 500.0,
        "ductile": True, "SF": 1.2, "SB": 2.5,
        "category": "steel",
        "tau_allow_key": 60.0,
        "p_allow_key":   333.0,
        "p_allow_spline": 319.5,
    },
    "Steel 16MnCr5": {
        "E": 210000.0, "nu": 0.30,
        "sigma_yield": 440.0,
        "sigma_uts": 650.0,
        "ductile": True, "SF": 1.2, "SB": 2.5,
        "category": "steel",
        "tau_allow_key": 60.0,
        "p_allow_key":   396.0,
        "p_allow_spline": 396.0,
    },
    "SteelC45E": {
        "E": 210000.0, "nu": 0.30,
        "sigma_yield": 370.0,
        "sigma_uts": 600.0,
        "ductile": True, "SF": 1.2, "SB": 2.5,
        "category": "steel",
        "tau_allow_key": 60.0,
        "p_allow_key":   333.0,
        "p_allow_spline": 333.0,
    },
}

# -----------------------
# Friction coefficients (DIN 7190-1 Table 1 conservative)
# -----------------------
# -----------------------
# Haftbeiwerte ν for torque capacity of Querpressverbände (DIN 7190-1 Table 4)
# Use in: Mt = (pi/2) * d^2 * L * ν * p_zul / Sr
#
# IMPORTANT:
# - These are "Haftbeiwerte ν" (DIN), not Poisson ratio μ.
# - DIN Table 4 gives values for specific pairings & assembly conditions.
# - For non-tabulated pairings, values below are conservative engineering defaults ("EST").
# -----------------------

FRICTION_TABLE_DIN_RANGES = {
    # ===== DIN Table 4 anchors (Querpressverbände) =====
    # Stahl–Stahl
    ("steel", "steel", "oiled"): (0.12, 0.12),  # Druckölverband mit Mineralöl :contentReference[oaicite:3]{index=3}
    ("steel", "steel", "dry"):   (0.14, 0.20),  # shrink fit normal (0.14) to degreased/heated (0.20) :contentReference[oaicite:4]{index=4}

    # Stahl–Gusseisen
    ("steel", "cast_iron", "oiled"): (0.10, 0.10),  # Druckölverband mit Mineralöl :contentReference[oaicite:5]{index=5}
    ("steel", "cast_iron", "dry"):   (0.10, 0.16),  # spans to "entfettete Pressflächen" :contentReference[oaicite:6]{index=6}

    # Stahl–MgAl (you map to "aluminum")
    ("steel", "aluminum", "dry"): (0.10, 0.15),  # trocken :contentReference[oaicite:7]{index=7}
    # not tabulated by DIN for lubricated; use conservative estimates:
    ("steel", "aluminum", "oiled"): (0.08, 0.10),  # EST

    # Stahl–CuZn (you map to "bronze" category; closest available in DIN)
    ("steel", "bronze", "dry"): (0.17, 0.25),  # trocken :contentReference[oaicite:8]{index=8}
    ("steel", "bronze", "oiled"): (0.12, 0.15),  # EST (lubricated Cu alloy drops a lot)

    # ===== Engineering estimates for missing pairings (DIN does not tabulate) =====
    # Same-material pairs (EST): conservative mid values
    ("cast_iron", "cast_iron", "dry"):   (0.10, 0.12),  # EST
    ("cast_iron", "cast_iron", "oiled"): (0.06, 0.08),  # EST

    ("aluminum", "aluminum", "dry"):   (0.10, 0.14),    # EST
    ("aluminum", "aluminum", "oiled"): (0.06, 0.09),    # EST

    ("bronze", "bronze", "dry"):   (0.14, 0.20),        # EST (Cu alloys can be “grabby” dry)
    ("bronze", "bronze", "oiled"): (0.08, 0.12),        # EST

    # Mixed non-steel pairs (EST)
    ("cast_iron", "aluminum", "dry"):   (0.08, 0.11),   # EST
    ("cast_iron", "aluminum", "oiled"): (0.05, 0.07),   # EST

    ("cast_iron", "bronze", "dry"):     (0.10, 0.14),   # EST
    ("cast_iron", "bronze", "oiled"):   (0.06, 0.09),   # EST

    ("aluminum", "bronze", "dry"):      (0.12, 0.17),   # EST
    ("aluminum", "bronze", "oiled"):    (0.07, 0.11),   # EST
}


def get_material_category(mat_name: str) -> str:
    if mat_name in materials:
        return materials[mat_name].get("category", "steel")
    return "steel"

def mu_for(
    rng,
    shaft_mat: str,
    hub_mat: str,
    surface_condition: str = "dry",
    override: float | None = None,
) -> float:
    """
    DIN 7190 Haftbeiwert ν_ru for torque (Querpressverband).
    """

    if override is not None:
        return max(0.05, min(0.25, float(override)))

    cat1 = get_material_category(shaft_mat)
    cat2 = get_material_category(hub_mat)

    key = (cat1, cat2, surface_condition)
    if key not in FRICTION_TABLE_DIN_RANGES:
        key = (cat2, cat1, surface_condition)

    if key in FRICTION_TABLE_DIN_RANGES:
        lo, hi = FRICTION_TABLE_DIN_RANGES[key]
        return round(float(rng.uniform(lo, hi)), 2)

    # conservative DIN fallback
    return 0.12


# -----------------------
# Tables: spline + key
# -----------------------
spline_table = [
    {"d_max": 11,  "D": 14,  "N": 6,  "B": 3},
    {"d_max": 13,  "D": 16,  "N": 6,  "B": 3},
    {"d_max": 16,  "D": 20,  "N": 6,  "B": 4},
    {"d_max": 18,  "D": 22,  "N": 6,  "B": 4},
    {"d_max": 21,  "D": 25,  "N": 6,  "B": 6},
    {"d_max": 23,  "D": 26,  "N": 6,  "B": 6},
    {"d_max": 26,  "D": 30,  "N": 6,  "B": 6},
    {"d_max": 28,  "D": 32,  "N": 6,  "B": 7},
    {"d_max": 32,  "D": 36,  "N": 8,  "B": 6},
    {"d_max": 36,  "D": 40,  "N": 8,  "B": 7},
    {"d_max": 42,  "D": 46,  "N": 8,  "B": 8},
    {"d_max": 46,  "D": 50,  "N": 8,  "B": 9},
    {"d_max": 52,  "D": 58,  "N": 8,  "B": 10},
    {"d_max": 56,  "D": 62,  "N": 8,  "B": 10},
    {"d_max": 62,  "D": 68,  "N": 8,  "B": 12},
    {"d_max": 72,  "D": 78,  "N": 10, "B": 12},
    {"d_max": 82,  "D": 88,  "N": 10, "B": 12},
    {"d_max": 92,  "D": 98,  "N": 10, "B": 14},
    {"d_max": 102, "D": 108, "N": 10, "B": 16},
    {"d_max": 112, "D": 120, "N": 10, "B": 18},
]

_DIN5480_MODULES = [
    0.5, 0.6, 0.75, 0.8, 1.0, 1.25, 1.5, 1.75,
    2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0,
]

def _choose_module_for_d(d_mm: float) -> float:
    m_target = max(0.5, min(10.0, d_mm / 35.0))
    best = min(_DIN5480_MODULES, key=lambda m: abs(m - m_target))
    return best

def _din5480_like_geometry(d_mm: float) -> tuple[int, float, float, float]:
    m = _choose_module_for_d(d_mm)
    z = int(max(18, min(80, round(d_mm / m))))
    h_proj = 2.25 * m
    D = d_mm + 2.0 * h_proj
    b = max(16.0, min(0.25 * d_mm, 60.0))
    return z, h_proj, D, b

def spline_geometry_from_d_lookup(d_mm: float) -> tuple[int, float, float, float]:
    for row in spline_table:
        if d_mm <= row["d_max"]:
            D, z, b = row["D"], row["N"], row["B"]
            h_proj = 0.5 * (D - d_mm)
            return z, h_proj, D, b
    return _din5480_like_geometry(d_mm)

def _spline_geometry_from_override(
    d_mm: float,
    D_override: float,
    z_override: Optional[int] = None
) -> tuple[int, float, float, float, bool]:
    D_mm = float(D_override)
    if D_mm <= d_mm:
        raise ValueError("Spline major diameter override must be greater than minor diameter d_mm.")

    base_z, _, _, base_b = spline_geometry_from_d_lookup(d_mm)
    h_proj = 0.5 * (D_mm - float(d_mm))
    h_proj = max(h_proj, 0.1)

    if z_override is not None:
        z = int(round(z_override))
        z = max(6, z)
        z_is_estimated = False
    else:
        z = base_z
        z_is_estimated = True

    return z, h_proj, D_mm, base_b, z_is_estimated

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
        if row["d_min"] <= d_mm <= row["d_max"]:
            return float(row["b"]), float(row["h"])
    last = key_table[-1]
    return float(last["b"]), float(last["h"])

# -----------------------
# User preferences (8 criteria)
# -----------------------
@dataclass
class UserPrefs:
    ease: float
    movement: float
    cost: float
    bidirectional: float
    vibration: float
    speed: float
    maintenance: float
    durability: float

CONN_PROFILE = {
    "press": {
        "assembly/disassembly_ease": 0.20,
        "manufacturing_cost":        0.85,
        "movement_ease":             0.00,
        "bidirectional":             0.80,
        "vibration_resistance":      0.85,
        "high_speed_suitability":    0.90,
        "maintenance_ease":          0.55,
        "durability":                0.55,
    },
    "key": {
        "assembly/disassembly_ease": 0.75,
        "manufacturing_cost":        0.50,
        "movement_ease":             0.45,
        "bidirectional":             0.70,
        "vibration_resistance":      0.45,
        "high_speed_suitability":    0.50,
        "maintenance_ease":          0.55,
        "durability":                0.40,
    },
    "spline": {
        "assembly/disassembly_ease": 0.85,
        "manufacturing_cost":        0.20,
        "movement_ease":             0.95,
        "bidirectional":             0.90,
        "vibration_resistance":      0.75,
        "high_speed_suitability":    0.85,
        "maintenance_ease":          0.30,
        "durability":                0.85,
    },
}

# -----------------------
# Press-fit equations
# -----------------------
def p_allow_pressfit(
    shaft_type: str,
    shaft_mat: Dict[str, Any],
    hub_mat: Dict[str, Any],
    dF_mm: float,
    DiI_mm: Optional[float],
    DaA_mm: Optional[float]
) -> float:
    d = float(dF_mm)
    if d <= 0:
        raise ValueError("shaft_diameter must be > 0")

    D = float(DaA_mm) if DaA_mm is not None else 2.0 * d
    if D <= d:
        raise ValueError("hub_outer_diameter must be > shaft_diameter")

    QA = d / D

    QI = 0.0
    if shaft_type == "hollow":
        if DiI_mm is None:
            raise ValueError("Hollow shaft requires shaft_inner_diameter.")
        Di = float(DiI_mm)
        if not (0.0 < Di < d):
            raise ValueError("shaft_inner_diameter must be in (0, shaft_diameter)")
        QI = Di / d

    def sigma_zul(mat: Dict[str, Any]) -> float:
        if mat.get("ductile", True):
            return float(mat["sigma_yield"]) / float(mat.get("SF", 1.2))
        return float(mat["sigma_uts"]) / float(mat.get("SB", 2.5))

    sigma_zulW = sigma_zul(shaft_mat)
    sigma_zulN = sigma_zul(hub_mat)

    p_hub = ((1.0 - QA**2) / math.sqrt(3.0)) * sigma_zulN
    p_shaft = (2.0 / math.sqrt(3.0)) * sigma_zulW

    if shaft_type == "hollow":
        p_shaft *= (1.0 - QI**2)

    return min(p_shaft, p_hub)

def p_required_pressfit(M_req_Nmm: float, d_mm: float, L_mm: float, mu: float, S_R: float) -> float:
    d = float(d_mm)
    L = float(L_mm)
    if d <= 0 or L <= 0:
        raise ValueError("d_mm and L_mm must be > 0.")
    if mu <= 0:
        raise ValueError("mu must be > 0.")
    if S_R <= 0:
        raise ValueError("S_R must be > 0.")
    return (2.0 * float(M_req_Nmm) * float(S_R)) / (math.pi * float(mu) * (d ** 2) * L)

def elastic_interference(
    dF_mm: float,
    p_MPa: float,
    E_I: float, nu_I: float, QI: float,
    E_A: float, nu_A: float, QA: float
) -> float:
    return p_MPa * dF_mm * (((1.0 + nu_I) / E_I) / (1.0 - QI**2) + ((1.0 + nu_A) / E_A) / (1.0 - QA**2))

def smoothing_G(RzI_um: float, RzA_um: float) -> float:
    return 0.4 * (RzI_um + RzA_um) / 1000.0

def pressfit_interference_check(
    d_mm: float,
    p_erf_MPa: float,
    shaft_type: str,
    shaft_mat_name: str,
    hub_mat_name: str,
    DiI_mm: Optional[float],
    DaA_mm: Optional[float],
    Rz_shaft_um: float = 12.0,
    Rz_hub_um: float = 12.0,
) -> Dict[str, Any]:
    shaft_mat = materials[shaft_mat_name]
    hub_mat = materials[hub_mat_name]

    d = float(d_mm)
    if d <= 0:
        return {"ok": False, "reason": "invalid shaft diameter"}

    # QI
    QI = 0.0
    if shaft_type == "hollow":
        if DiI_mm is None:
            return {"ok": False, "reason": "missing shaft_inner_diameter"}
        Di = float(DiI_mm)
        if not (0.0 < Di < d):
            return {"ok": False, "reason": "shaft_inner_diameter out of range"}
        QI = Di / d

    # QA
    D = float(DaA_mm) if DaA_mm is not None else 2.0 * d
    if D <= d:
        return {"ok": False, "reason": "hub_outer_diameter must be > d"}
    QA = d / D

    Ue_mm = elastic_interference(
        dF_mm=d,
        p_MPa=float(p_erf_MPa),
        E_I=float(shaft_mat["E"]), nu_I=float(shaft_mat["nu"]), QI=float(QI),
        E_A=float(hub_mat["E"]),   nu_A=float(hub_mat["nu"]),   QA=float(QA),
    )

    G_mm = smoothing_G(RzI_um=float(Rz_shaft_um), RzA_um=float(Rz_hub_um))
    Uw_mm = Ue_mm - G_mm

    limit_mm = 0.02 if d <= 50.0 else 0.05

    ok = True
    reason = None
    if Uw_mm <= 0.0:
        ok = False
        reason = "Uw <= 0 (roughness consumes interference)"
    elif Uw_mm > limit_mm:
        ok = False
        reason = f"Uw too large (Uw={Uw_mm:.4f} mm > {limit_mm:.3f} mm)"

    return {
        "ok": bool(ok),
        "reason": reason,
        "Ue_mm": float(Ue_mm),
        "G_mm": float(G_mm),
        "Uw_mm": float(Uw_mm),
        "Uw_limit_mm": float(limit_mm),
        "QA": float(QA),
        "QI": float(QI),
        "Rz_shaft_um": float(Rz_shaft_um),
        "Rz_hub_um": float(Rz_hub_um),
    }

def pressfit_capacity(
    M_req_Nmm: float,
    d_mm: float, L_mm: float,
    shaft_type: str,
    shaft_mat_name: str, hub_mat_name: str,
    mu: float, S_R: float,
    DiI_mm: Optional[float], DaA_mm: Optional[float],
    Rz_shaft_um: float = 12.0,
    Rz_hub_um: float = 12.0,
) -> Dict[str, Any]:
    shaft_mat, hub_mat = materials[shaft_mat_name], materials[hub_mat_name]

    d = float(d_mm)
    L = float(L_mm)
    mu = float(mu)
    S_R = float(S_R)

    p_erf = p_required_pressfit(M_req_Nmm, d, L, mu, S_R)
    p_zul = p_allow_pressfit(shaft_type, shaft_mat, hub_mat, d, DiI_mm, DaA_mm)

    # Capacity from allowable pressure
    Mt_from_pzul = (math.pi * mu * p_zul * L * (d ** 2)) / 2.0
    Fu = (2.0 * float(M_req_Nmm)) / d

    intr = pressfit_interference_check(
        d_mm=d,
        p_erf_MPa=p_erf,
        shaft_type=shaft_type,
        shaft_mat_name=shaft_mat_name,
        hub_mat_name=hub_mat_name,
        DiI_mm=DiI_mm,
        DaA_mm=DaA_mm,
        Rz_shaft_um=Rz_shaft_um,
        Rz_hub_um=Rz_hub_um,
    )

    return {
        "Fu": Fu,
        "p_erf": p_erf,
        "p_zul": p_zul,
        "Mt_from_pzul": Mt_from_pzul,
        "interference": intr,
    }

# -----------------------
# Keys & splines capacity (NOW use both materials)
# -----------------------
def key_capacity(
    d_mm: float,
    l_key_mm: float,
    shaft_mat_name: str,
    hub_mat_name: str,
) -> Dict[str, Any]:
    b_mm, h_mm = key_geometry_from_d(d_mm)

    mat_shaft = materials[shaft_mat_name]
    mat_hub = materials[hub_mat_name]

    tau_allow = float(mat_shaft["tau_allow_key"])
    p_allow_effective = min(float(mat_shaft["p_allow_key"]), float(mat_hub["p_allow_key"]))

    A_shear = b_mm * l_key_mm
    A_bear = (h_mm / 2.0) * l_key_mm
    r = 0.5 * d_mm

    T_tau = tau_allow * A_shear * r
    T_p = p_allow_effective * A_bear * r

    return {
        "Mt": min(T_tau, T_p),
        "b_mm": b_mm,
        "h_mm": h_mm,
        "l_mm": l_key_mm,
        "tau_allow": tau_allow,
        "p_allow_effective": p_allow_effective,
        "p_allow_shaft": float(mat_shaft["p_allow_key"]),
        "p_allow_hub": float(mat_hub["p_allow_key"]),
    }

def spline_capacity(
    d_mm: float,
    L_mm: float,
    shaft_mat_name: str,
    hub_mat_name: str,
    major_d_override: Optional[float] = None,
    tooth_count_override: Optional[int] = None
) -> Dict[str, Any]:
    if major_d_override is not None:
        z, h_proj_mm, D_mm, b_table_mm, _ = _spline_geometry_from_override(
            d_mm, major_d_override, tooth_count_override
        )
        override_used = True
    else:
        z, h_proj_mm, D_mm, b_table_mm = spline_geometry_from_d_lookup(d_mm)
        override_used = False

    mat_shaft = materials[shaft_mat_name]
    mat_hub = materials[hub_mat_name]

    p_allow_effective = min(float(mat_shaft["p_allow_spline"]), float(mat_hub["p_allow_spline"]))

    L = float(L_mm)
    r_m = 0.25 * (float(d_mm) + float(D_mm))
    # Effective flank height: 80% of projected height to account for non-uniform load sharing
    # This conservative reduction reflects that not all teeth share load equally
    h_eff = float(h_proj_mm)
    K = 0.75
    Mt = K * L * z * h_eff * r_m * p_allow_effective

    return {
        "Mt": Mt,
        "z": z,
        "L_mm": L,
        "b_table_mm": b_table_mm,
        "h_proj_mm": h_proj_mm,
        "h_eff_mm": h_eff,
        "D_mm": D_mm,
        "r_m_mm": r_m,
        "p_allow_effective": p_allow_effective,
        "p_allow_shaft": float(mat_shaft["p_allow_spline"]),
        "p_allow_hub": float(mat_hub["p_allow_spline"]),
        "K": K,
        "override_used": override_used,
    }

# -----------------------
# Hub stiffness evaluation (press-fit penalty)
# -----------------------
def calculate_hub_stiffness_factor(d_mm: float, DaA_mm: Optional[float]) -> float:
    if DaA_mm is None or DaA_mm <= d_mm:
        return 0.5
    QA = d_mm / DaA_mm
    if QA < 0.5:
        return 1.0
    elif QA < 0.6:
        return 0.85
    elif QA < 0.7:
        return 0.60
    elif QA < 0.8:
        return 0.30
    else:
        return 0.10

# -----------------------
# Scoring
# -----------------------
def score_candidate(
    conn: str,
    Mt_cap: float,
    M_req: float,
    d_mm: float,
    L_mm: float,
    prefs: UserPrefs,
    DaA_mm: Optional[float] = None,
    weights = {
        "margin":       0.10,
        "prefs":        0.70,
        "overkill":     0.10,
        "hub_stiffness": 0.10,
    },
    margin_cap: float = 0.35
) -> float:
    # 1) Margin reward (diminishing)
    margin_raw = max(0.0, (Mt_cap - M_req) / max(M_req, 1e-6))
    margin_useful = min(margin_raw, margin_cap) / margin_cap
    s_margin = weights["margin"] * margin_useful

    # Overkill penalty
    overkill = max(0.0, margin_raw - margin_cap)
    overkill_capped = min(overkill, 0.5)
    s_overkill = -weights["overkill"] * overkill_capped

    # 2) Preferences
    prof = CONN_PROFILE[conn]
    pref_sum = (
        prefs.ease + prefs.movement + prefs.cost + prefs.bidirectional +
        prefs.vibration + prefs.speed + prefs.maintenance + prefs.durability
    )
    norm = pref_sum if pref_sum > 1e-9 else 1.0

    pref_util = (
        prefs.ease          * prof.get("assembly/disassembly_ease", 0.0) +
        prefs.movement      * prof.get("movement_ease", 0.0) +
        prefs.cost          * prof.get("manufacturing_cost", 0.0) +
        prefs.bidirectional * prof.get("bidirectional", 0.0) +
        prefs.vibration     * prof.get("vibration_resistance", 0.0) +
        prefs.speed         * prof.get("high_speed_suitability", 0.0) +
        prefs.maintenance   * prof.get("maintenance_ease", 0.0) +
        prefs.durability    * prof.get("durability", 0.0)
    ) / norm
    s_prefs = weights["prefs"] * pref_util

    # 3) Hub stiffness penalty (press only)
    s_hub_stiffness = 0.0
    if conn == "press" and DaA_mm is not None:
        hub_factor = calculate_hub_stiffness_factor(d_mm, DaA_mm)
        s_hub_stiffness = weights["hub_stiffness"] * (hub_factor - 1.0)

    # 4) Spline practicality penalty when user doesn't care about spline strengths
    spline_practicality = 0.0
    if conn == "spline":
        spline_pref_intensity = (prefs.movement + prefs.bidirectional + prefs.durability) / 3.0
        spline_practicality = -0.2 * max(0.0, 1.0 - spline_pref_intensity)

    raw_score = s_margin + s_overkill + s_prefs + s_hub_stiffness + spline_practicality
    return max(raw_score, -0.15)

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

    # REQUIRED torque
    if request.required_torque is None:
        raise HTTPException(status_code=400, detail="required_torque is mandatory")
    M_req = float(request.required_torque)

    # User preferences
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

    # Clean mu override (FastAPI might pass "" from UI)
    mu_override = getattr(request, "mu_override", None)
    if isinstance(mu_override, str) and mu_override.strip() == "":
        mu_override = None

    rng = np.random.default_rng(RNG_SEED_DEFAULT)

    mu = mu_for(
        rng,
        request.shaft_material,
        request.hub_material,
        surface_condition=getattr(request, "surface_condition", "dry"),
        override=mu_override,
    )

    # Geometry
    d = float(request.shaft_diameter)
    L_press = float(request.hub_length) if request.hub_length is not None else 1.5 * d

    DiI_mm = float(request.shaft_inner_diameter) if request.shaft_type == "hollow" else None
    DaA_mm = float(request.hub_outer_diameter) if request.hub_outer_diameter is not None else 2.0 * d
    L_hub = float(request.hub_length) if request.hub_length is not None else 1.5 * d

    # Surface roughness from main.py fields
    Rz_shaft = float(getattr(request, "surface_roughness_shaft", 12.0))
    Rz_hub = float(getattr(request, "surface_roughness_hub", 12.0))

    # Capacities
    try:
        pf = pressfit_capacity(
            M_req_Nmm=M_req,
            d_mm=d,
            L_mm=L_press,
            shaft_type=request.shaft_type,
            shaft_mat_name=request.shaft_material,
            hub_mat_name=request.hub_material,
            mu=mu,
            S_R=float(request.safety_factor),
            DiI_mm=DiI_mm,
            DaA_mm=DaA_mm,
            Rz_shaft_um=Rz_shaft,
            Rz_hub_um=Rz_hub,
        )
        Mt_press = float(pf["Mt_from_pzul"])
        press_practical_ok = bool(pf.get("interference", {}).get("ok", True))
    except Exception as e:
        pf = {"error": str(e)}
        Mt_press = 0.0
        press_practical_ok = False

    key = key_capacity(
        d_mm=d,
        l_key_mm=L_hub,
        shaft_mat_name=request.shaft_material,
        hub_mat_name=request.hub_material,
    )

    spline = spline_capacity(
        d_mm=d,
        L_mm=L_hub,
        shaft_mat_name=request.shaft_material,
        hub_mat_name=request.hub_material,
        major_d_override=getattr(request, "spline_major_diameter_override", None),
        tooth_count_override=getattr(request, "spline_tooth_count_override", None),
    )

    candidates = {"press": Mt_press, "key": float(key["Mt"]), "spline": float(spline["Mt"])}

    # Design torque
    M_design = M_req * float(request.safety_factor)

    # Feasibility: include press-fit practicality (interference sanity)
    feasible_flags = {
        "press": (candidates["press"] >= M_design) and press_practical_ok,
        "key": candidates["key"] >= M_design,
        "spline": candidates["spline"] >= M_design,
    }
    feasible = {k: candidates[k] for k, ok in feasible_flags.items() if ok}

    if not feasible:
        reason = "No connection type can safely transmit the required torque"
        # If press was torque-feasible but interference failed, make that explicit
        press_torque_ok = (candidates["press"] >= M_design)
        if press_torque_ok and not press_practical_ok:
            intr = pf.get("interference", {})
            reason = f"Press-fit torque OK but rejected by interference check: {intr.get('reason', 'unknown')}"

        return {
            "recommended_connection": "none",
            "feasible_connections": list(sorted(feasible.keys())),
            "feasible_connections_count": len(feasible),
            "M_design_Nmm": M_design,
            "reason": reason,
            "required_torque_Nmm": M_req,
            "capacities_Nmm": candidates,
            "feasible": False,
            "mu_used": mu,
            "scores": None,
            "surface_condition": getattr(request, "surface_condition", "dry"),
            "hub_stiffness_factor": calculate_hub_stiffness_factor(d, DaA_mm),
            "input_parameters": request.dict(),
            "details": {"press": pf, "key": key, "spline": spline, "feasible_flags": feasible_flags},
        }

    # Score feasible candidates (compare to design torque)
    scores = {
        k: score_candidate(
            conn=k,
            Mt_cap=feasible[k],
            M_req=M_design,
            d_mm=d,
            L_mm=L_hub,
            prefs=prefs,
            DaA_mm=DaA_mm
        )
        for k in feasible
    }

    best_connection = max(scores.items(), key=lambda x: x[1])[0]

    return {
        "recommended_connection": best_connection,
        "required_torque_Nmm": M_req,
        "capacities_Nmm": candidates,
        "scores": scores,
        "feasible_connections": list(sorted(feasible.keys())),
        "feasible_connections_count": len(feasible),
        "M_design_Nmm": M_design,
        "hub_stiffness_factor": calculate_hub_stiffness_factor(d, DaA_mm),
        "feasible": True,
        "mu_used": mu,
        "surface_condition": getattr(request, "surface_condition", "dry"),
        "input_parameters": request.dict(),
        "details": {"press": pf, "key": key, "spline": spline, "feasible_flags": feasible_flags},
    }
