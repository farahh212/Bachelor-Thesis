# generate_shc_dataset.py

import math
from pathlib import Path
from typing import List, Dict

# add imports at top
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PLOTS_DIR = Path(__file__).parent / "figures"
PLOTS_DIR.mkdir(exist_ok=True)


import numpy as np
import pandas as pd
from fastapi import HTTPException

from make_prediction import select_shaft_connection, materials, calculate_required_torque
from main import ShaftConnectionRequest, UserPreferences

OUTPUT_FILE = Path(__file__).parent / "synthetic_SHC_dataset.csv"

# Discrete diameters you actually care about (DIN-ish progression)
DIAMETER_OPTIONS = np.array([
    6, 8, 10, 12, 14, 16, 18, 20,
    25, 30, 35, 40, 45, 50, 60, 70,
    80, 90, 100, 110, 120, 130, 140, 150,
    170, 190, 210, 230
], dtype=float)

def random_user_prefs(rng: np.random.Generator) -> UserPreferences:
    def pref() -> float:
        return float(rng.integers(0, 11)) / 10.0  # 0.0..1.0 step 0.1

    return UserPreferences(
        ease=pref(), movement=pref(), cost=pref(), vibration=pref(),
        speed=pref(), maintenance=pref(), bidirectional=pref(), durability=pref(),
    )



def sample_required_torque(
    rng: np.random.Generator,
    d_mm: float,
    shaft_material: str,
    mode: str = "relative",
):
    if mode == "relative":
        ref_T = calculate_required_torque(d_mm, shaft_material)
        factor = float(rng.uniform(0.3, 1.4))
        return round(ref_T * factor, 0), factor

    coef = float(rng.uniform(70.0, 200.0))
    Wt = math.pi * (d_mm ** 3) / 16.0
    taper = 1.0 if d_mm <= 40 else 0.9 if d_mm <= 70 else 0.8
    T = round(0.05 * coef * Wt * taper, 0)
    return T, None


def sample_safety_factor_1dp(
    rng: np.random.Generator,
    has_bending: bool,
    surface_condition: str,
    mu_override,
    torque_factor: float | None,
    prefs: UserPreferences,
) -> float:
    # Baseline (most users hover around 1.4–1.6)
    sf = rng.normal(1.5, 0.12)

    # More demanding / uncertain situations -> higher SF
    if has_bending:
        sf += 0.10

    # "dry" tends to be less controlled; "oiled" implies more controlled assembly/conditions
    if surface_condition == "dry":
        sf += 0.05
    elif surface_condition == "oiled":
        sf -= 0.03

    # if user overrides μ, they’re “tuning” the model; treat as slightly more controlled
    if mu_override is not None:
        sf -= 0.05

    # torque_factor > 1 means you sampled "harder than reference" cases -> bump SF a bit
    if torque_factor is not None:
        sf += 0.20 * max(0.0, torque_factor - 1.0)

    # preferences: durability & bidirectional -> more conservative; cost -> less conservative
    sf += 0.20 * (prefs.durability - 0.5)
    sf += 0.10 * (prefs.bidirectional - 0.5)
    sf -= 0.15 * (prefs.cost - 0.5)

    # Frontend bounds and 1 decimal place output
    sf = min(max(sf, 1.0), 2.0)
    return round(float(sf), 1)


def sample_diameter_user_like(rng):
    typical = DIAMETER_OPTIONS[(DIAMETER_OPTIONS >= 20) & (DIAMETER_OPTIONS <= 60)]
    mid     = DIAMETER_OPTIONS[(DIAMETER_OPTIONS > 60) & (DIAMETER_OPTIONS <= 120)]
    tails   = DIAMETER_OPTIONS[(DIAMETER_OPTIONS < 20) | (DIAMETER_OPTIONS > 120)]

    u = rng.random()
    if u < 0.70:
        return float(rng.choice(typical))
    elif u < 0.95:
        return float(rng.choice(mid))
    return float(rng.choice(tails))


def sample_request(rng: np.random.Generator) -> ShaftConnectionRequest:
    d = sample_diameter_user_like(rng)

    # 70% with bending → hub length ~ D, others ~ 0.5–0.8 D
    has_bending = bool(rng.random() < 0.7)
    if has_bending:
        hub_length = float(d * rng.uniform(0.9, 1.3))
    else:
        hub_length = float(d * rng.uniform(0.4, 0.8))

    shaft_type = "hollow" if rng.random() < 0.2 else "solid"
    material = rng.choice(list(materials.keys()))
    # safety_factor = round(float(rng.uniform(1.0, 2.0)), 2)

    

    # Surface condition and possible μ override
    surface_condition = rng.choice(["dry", "oiled"])
    mu_override = None
    if rng.random() < 0.15:
        mu_override = round(float(rng.uniform(0.05, 0.25)), 2)

    # Geometry: outer diameter for hubs, inner for hollow shafts
    if shaft_type == "hollow":
        shaft_inner = round(float(d * rng.uniform(0.3, 0.6)), 0)
        hub_outer = round(float(d * rng.uniform(1.8, 2.6)), 0)
        if has_bending:
            hub_outer = round(hub_outer * rng.uniform(1.05, 1.15), 0)

    else:
        shaft_inner = None
        hub_outer = float(d * rng.uniform(1.8, 2.6))
        if has_bending:
            hub_outer *= rng.uniform(1.05, 1.15)
        hub_outer = round(hub_outer, 0)

    prefs = random_user_prefs(rng)
    req_torque, torque_factor = sample_required_torque(rng, d, material, mode="relative")

    # after surface_condition + mu_override are set:
    safety_factor = sample_safety_factor_1dp(
        rng=rng,
        has_bending=has_bending,
        surface_condition=surface_condition,
        mu_override=mu_override,
        torque_factor=torque_factor,
        prefs=prefs,
    )

    request = ShaftConnectionRequest(
        shaft_diameter=d,
        hub_length=round(hub_length, 0),
        shaft_material=material,
        hub_material=material,
        shaft_type=shaft_type,
        has_bending=has_bending,
        required_torque=req_torque,
        user_preferences=prefs,
        safety_factor=safety_factor,
        surface_condition=surface_condition,
        hub_outer_diameter=hub_outer,
        shaft_inner_diameter=shaft_inner,
        mu_override=mu_override,
    )
    return request

def save_dataset_distribution_plots(df: pd.DataFrame, out_dir: Path) -> None:
    """Generate publication-quality distribution plots for the synthetic dataset."""
    out_dir.mkdir(exist_ok=True)
    
    # Set style for publication-quality plots
    plt.style.use('seaborn-v0_8-whitegrid')
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    
    # 1) Shaft diameter histogram
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(df["shaft_diameter"].dropna(), bins=20, color=colors[0], edgecolor='black', alpha=0.7)
    ax.set_xlabel("Shaft diameter [mm]", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_title("Distribution of Shaft Diameters", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_dir / "dataset_diameter_hist.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 2) Required torque histogram (log scale)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    torque = df["required_torque"].dropna()
    ax.hist(torque, bins=30, color=colors[1], edgecolor='black', alpha=0.7)
    ax.set_yscale("linear")
    ax.set_xscale("log")
    ax.set_xlabel("Required torque [N⋅m] (log scale)", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_title("Distribution of Required Torque", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_dir / "dataset_required_torque_hist_logx.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 3) Class distribution bar chart
    fig, ax = plt.subplots(figsize=(7, 4.5))
    counts = df["label"].value_counts()
    # Order: press, key, spline for consistency
    order = ['press', 'key', 'spline']
    ordered_counts = [counts.get(label, 0) for label in order if label in counts.index]
    ordered_labels = [label for label in order if label in counts.index]
    bars = ax.bar(ordered_labels, ordered_counts, color=[colors[2], colors[3], colors[4]], 
                  edgecolor='black', alpha=0.7)
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}\n({height/len(df)*100:.1f}%)',
                ha='center', va='bottom', fontsize=10)
    ax.set_xlabel("Connection Type", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_title("Class Distribution in Synthetic Dataset", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_dir / "dataset_class_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 4) Material distribution bar chart (shaft_material)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    mcounts = df["shaft_material"].value_counts().head(15)
    bars = ax.bar(range(len(mcounts)), mcounts.values, color=colors[0], edgecolor='black', alpha=0.7)
    ax.set_xticks(range(len(mcounts)))
    ax.set_xticklabels(mcounts.index.astype(str), rotation=45, ha='right', fontsize=9)
    ax.set_xlabel("Shaft Material", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_title("Top 15 Material Distribution", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_dir / "dataset_material_distribution_top15.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 5) Safety factor histogram
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(df["safety_factor"].dropna(), bins=15, color=colors[2], edgecolor='black', alpha=0.7)
    ax.set_xlabel("Safety Factor [-]", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_title("Distribution of Safety Factors", fontsize=12, fontweight='bold')
    # Add mean line
    mean_sf = df["safety_factor"].mean()
    ax.axvline(mean_sf, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_sf:.2f}')
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(out_dir / "dataset_safety_factor_hist.png", dpi=300, bbox_inches='tight')
    plt.close()


def generate_dataset(
    n_samples: int = 5000,
    seed: int = 42,
    keep_infeasible: bool = False,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: List[Dict] = []

    for _ in range(n_samples):
        req = sample_request(rng)

        try:
            result = select_shaft_connection(req)
        except HTTPException:
            # something invalid in the geometry; skip sample
            continue

        label = result["recommended_connection"]
        feasible = bool(result.get("feasible", label != "none"))

        if not feasible and not keep_infeasible:
            # skip impossible designs for training, unless you explicitly
            # want a "none" class
            continue

        prefs = req.user_preferences

        rows.append(
            {
                # geometry / operating conditions
                "shaft_diameter": req.shaft_diameter,
                "hub_length": req.hub_length,
                "shaft_type": req.shaft_type,
                "shaft_material": req.shaft_material,
                "has_bending": float(req.has_bending),
                "safety_factor": req.safety_factor,
                "surface_condition": req.surface_condition,
                "mu_override": req.mu_override,
                "hub_outer_diameter": req.hub_outer_diameter,
                "shaft_inner_diameter": req.shaft_inner_diameter,
                "required_torque": req.required_torque,
                # prefs
                "pref_ease": prefs.ease,
                "pref_movement": prefs.movement,
                "pref_cost": prefs.cost,
                "pref_vibration": prefs.vibration,
                "pref_speed": prefs.speed,
                "pref_bidirectional": prefs.bidirectional,
                "pref_maintenance": prefs.maintenance,
                "pref_durability": prefs.durability,
                # labels
                "label": label,
                "analytical_label": label,
                "feasible": float(feasible),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")

        # Save distribution figures for thesis (Figure 4.4)
    save_dataset_distribution_plots(df, PLOTS_DIR)

    # Save a compact stats JSON (good for thesis reproducibility)
    stats = {
        "n_rows": int(len(df)),
        "label_distribution": df["label"].value_counts().to_dict(),
        "shaft_diameter_mm": {
            "min": float(df["shaft_diameter"].min()),
            "max": float(df["shaft_diameter"].max()),
            "mean": float(df["shaft_diameter"].mean()),
        },
        "required_torque_Nm": {
            "min": float(df["required_torque"].min()),
            "max": float(df["required_torque"].max()),
            "mean": float(df["required_torque"].mean()),
        },
    }
    with open(PLOTS_DIR / "dataset_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)



    return df


if __name__ == "__main__":
    generate_dataset()
