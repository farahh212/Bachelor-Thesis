"""Script to compare TAS Schafer shrink disc data with model predictions.

This script:
1. Loads TAS Schafer Excel data
2. Maps TAS parameters to model inputs (where possible)
3. Runs model predictions
4. Compares with TAS catalog torque ratings
5. Generates comparison report
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, Any, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from model_service import predict_connection
from make_prediction import select_shaft_connection
from main import ShaftConnectionRequest, UserPreferences

# Paths
EXCEL_PATH = Path(__file__).parent.parent / "Shrink disc 3-part (1).xlsx"
OUTPUT_DIR = Path(__file__).parent / "tas_analysis"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_tas_data() -> pd.DataFrame:
    """Load and clean TAS Schafer Excel data."""
    print("Loading TAS Schafer data...")
    
    # Read Excel - first row contains headers
    df_raw = pd.read_excel(EXCEL_PATH, header=None)
    
    # Extract headers from first row
    headers = df_raw.iloc[0].tolist()
    headers = [str(h).strip() if pd.notna(h) else f"col_{i}" for i, h in enumerate(headers)]
    
    # Use data from row 1 onwards
    df_tas = df_raw.iloc[1:].copy()
    df_tas.columns = headers
    df_tas = df_tas.reset_index(drop=True)
    
    # Convert numeric columns
    numeric_cols = ['d (mm)', 'dw  (mm)', 'M max (Nm)', 'D (mm)', 'I (mm)', 'e (mm)', 
                    'H (mm)', 'A (mm)', 'd1 (mm)', 'MA (Nm)', 'Z (Stk.)', 'nmax (min-1)', 
                    'pN  (N/mm²)', 'I (kgm²)', 'Gewicht (kg)']
    for col in numeric_cols:
        if col in df_tas.columns:
            df_tas[col] = pd.to_numeric(df_tas[col], errors='coerce')
    
    # Drop rows with missing critical data
    required_cols = ['d (mm)', 'M max (Nm)']
    df_tas = df_tas.dropna(subset=required_cols)
    
    print(f"Loaded {len(df_tas)} TAS samples")
    return df_tas


def map_tas_to_model_inputs(row: pd.Series) -> Optional[Dict[str, Any]]:
    """Map TAS Schafer parameters to model input features.
    
    Returns None if mapping is not possible.
    """
    try:
        # Direct mappings
        shaft_diameter = float(row.get('d (mm)', np.nan))
        hub_outer_diameter = float(row.get('D (mm)', np.nan))
        tas_max_torque = float(row.get('M max (Nm)', np.nan))
        
        # Check for required values
        if pd.isna(shaft_diameter) or pd.isna(tas_max_torque):
            return None
        
        # Estimate hub length from TAS data
        # If 'A (mm)' exists, use it; otherwise estimate from diameter
        if pd.notna(row.get('A (mm)')):
            hub_length = float(row['A (mm)'])
        else:
            # Estimate: typical hub length is 0.8-1.2 * diameter
            hub_length = float(shaft_diameter * 1.0)
        
        # Estimate shaft inner diameter (assume solid for most cases)
        # If 'd1 (mm)' exists and is smaller than 'd', use it
        if pd.notna(row.get('d1 (mm)')):
            d1 = float(row['d1 (mm)'])
            if d1 < shaft_diameter:
                shaft_inner_diameter = d1
                shaft_type = "hollow"
            else:
                shaft_inner_diameter = None
                shaft_type = "solid"
        else:
            shaft_inner_diameter = None
            shaft_type = "solid"
        
        # Default values for missing features
        # Material: Use common steel (most shrink discs are steel)
        shaft_material = "Steel E360"  # Default assumption
        hub_material = "Steel E360"
        
        # Surface condition: Assume oiled (common for shrink discs)
        surface_condition = "oiled"
        
        # Safety factor: Use 1.5 as default (typical for catalog ratings)
        safety_factor = 1.5
        
        # Has bending: Assume yes (common in applications)
        has_bending = True
        
        # User preferences: Use neutral values (0.5)
        prefs = UserPreferences(
            ease=0.5, movement=0.5, cost=0.5, vibration=0.5,
            speed=0.5, maintenance=0.5, bidirectional=0.5, durability=0.5
        )
        
        # Required torque: Use TAS max torque for comparison
        # Note: This is the catalog rating, not the required torque
        # We'll use it to see if model would recommend this connection
        required_torque = tas_max_torque * 1000  # Convert Nm to Nmm
        
        # Hub outer diameter: Use from TAS if available, otherwise estimate
        if pd.isna(hub_outer_diameter):
            hub_outer_diameter = float(shaft_diameter * 2.0)  # Default estimate
        
        return {
            "shaft_diameter": shaft_diameter,
            "hub_length": hub_length,
            "shaft_type": shaft_type,
            "shaft_material": shaft_material,
            "hub_material": hub_material,
            "has_bending": has_bending,
            "required_torque": required_torque,
            "user_preferences": prefs,
            "safety_factor": safety_factor,
            "surface_condition": surface_condition,
            "hub_outer_diameter": hub_outer_diameter,
            "shaft_inner_diameter": shaft_inner_diameter,
            "mu_override": None,
        }
    except Exception as e:
        print(f"Error mapping row: {e}")
        return None


def run_comparison():
    """Run comparison between TAS data and model predictions."""
    print("=" * 80)
    print("TAS SCHAFER vs MODEL COMPARISON")
    print("=" * 80)
    
    # Load TAS data
    df_tas = load_tas_data()
    
    if len(df_tas) == 0:
        print("ERROR: No TAS data loaded")
        return
    
    # Results storage
    results = []
    
    print("\nProcessing TAS samples...")
    for idx, row in df_tas.iterrows():
        # Map TAS parameters to model inputs
        model_inputs = map_tas_to_model_inputs(row)
        
        if model_inputs is None:
            continue
        
        # Create request object
        try:
            request = ShaftConnectionRequest(**model_inputs)
        except Exception as e:
            print(f"Error creating request for row {idx}: {e}")
            continue
        
        # Get TAS catalog values
        tas_diameter = model_inputs["shaft_diameter"]
        tas_max_torque_nm = model_inputs["required_torque"] / 1000  # Convert back to Nm
        tas_interference = row.get('I (mm)', np.nan)
        tas_pressure = row.get('pN  (N/mm²)', np.nan)
        tas_clamping_elements = row.get('Z (Stk.)', np.nan)
        
        # Run analytical prediction
        try:
            analytical_result = select_shaft_connection(request)
            analytical_label = analytical_result.get("recommended_connection", "none")
            analytical_feasible = analytical_result.get("feasible", False)
            
            # Get torque capacities
            press_capacity = analytical_result.get("capacities", {}).get("press", {}).get("Mt_from_pzul", 0) / 1000  # Nm
            key_capacity = analytical_result.get("capacities", {}).get("key", {}).get("Mt", 0) / 1000  # Nm
            spline_capacity = analytical_result.get("capacities", {}).get("spline", {}).get("Mt", 0) / 1000  # Nm
        except Exception as e:
            print(f"Error in analytical prediction for row {idx}: {e}")
            analytical_label = "error"
            analytical_feasible = False
            press_capacity = 0
            key_capacity = 0
            spline_capacity = 0
        
        # Run ML prediction
        try:
            ml_features = {
                "shaft_diameter": model_inputs["shaft_diameter"],
                "hub_length": model_inputs["hub_length"],
                "has_bending": float(model_inputs["has_bending"]),
                "safety_factor": model_inputs["safety_factor"],
                "hub_outer_diameter": model_inputs["hub_outer_diameter"],
                "shaft_inner_diameter": model_inputs["shaft_inner_diameter"] or 0.0,
                "required_torque": model_inputs["required_torque"],
                "pref_ease": model_inputs["user_preferences"].ease,
                "pref_movement": model_inputs["user_preferences"].movement,
                "pref_cost": model_inputs["user_preferences"].cost,
                "pref_vibration": model_inputs["user_preferences"].vibration,
                "pref_speed": model_inputs["user_preferences"].speed,
                "pref_bidirectional": model_inputs["user_preferences"].bidirectional,
                "pref_maintenance": model_inputs["user_preferences"].maintenance,
                "pref_durability": model_inputs["user_preferences"].durability,
                "shaft_type": model_inputs["shaft_type"],
                "shaft_material": model_inputs["shaft_material"],
                "surface_condition": model_inputs["surface_condition"],
            }
            ml_result = predict_connection(ml_features)
            ml_label = ml_result.get("label", "unknown") if ml_result else "error"
            ml_probs = ml_result.get("probs", {}) if ml_result else {}
        except Exception as e:
            print(f"Error in ML prediction for row {idx}: {e}")
            ml_label = "error"
            ml_probs = {}
        
        # Store results
        results.append({
            "tas_index": idx,
            "tas_diameter_mm": tas_diameter,
            "tas_max_torque_nm": tas_max_torque_nm,
            "tas_interference_mm": tas_interference if pd.notna(tas_interference) else None,
            "tas_pressure_mpa": tas_pressure / 1000 if pd.notna(tas_pressure) else None,  # Convert to MPa
            "tas_clamping_elements": tas_clamping_elements if pd.notna(tas_clamping_elements) else None,
            "analytical_label": analytical_label,
            "analytical_feasible": analytical_feasible,
            "analytical_press_capacity_nm": press_capacity,
            "analytical_key_capacity_nm": key_capacity,
            "analytical_spline_capacity_nm": spline_capacity,
            "ml_label": ml_label,
            "ml_probs": ml_probs,
            "model_inputs": {
                "hub_length": model_inputs["hub_length"],
                "shaft_type": model_inputs["shaft_type"],
                "material": model_inputs["shaft_material"],
            }
        })
        
        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/{len(df_tas)} samples...")
    
    # Create results DataFrame
    df_results = pd.DataFrame(results)
    
    # Save results
    output_file = OUTPUT_DIR / "tas_comparison_results.csv"
    df_results.to_csv(output_file, index=False)
    print(f"\nSaved results to {output_file}")
    
    # Generate summary statistics
    summary = {
        "total_samples": len(df_results),
        "analytical_predictions": {
            "press": len(df_results[df_results["analytical_label"] == "press"]),
            "key": len(df_results[df_results["analytical_label"] == "key"]),
            "spline": len(df_results[df_results["analytical_label"] == "spline"]),
            "none": len(df_results[df_results["analytical_label"] == "none"]),
        },
        "ml_predictions": {
            "press": len(df_results[df_results["ml_label"] == "press"]),
            "key": len(df_results[df_results["ml_label"] == "key"]),
            "spline": len(df_results[df_results["ml_label"] == "spline"]),
        },
        "capacity_comparison": {
            "tas_vs_press": {
                "tas_higher": len(df_results[df_results["tas_max_torque_nm"] > df_results["analytical_press_capacity_nm"]]),
                "press_higher": len(df_results[df_results["analytical_press_capacity_nm"] > df_results["tas_max_torque_nm"]]),
            },
            "tas_vs_key": {
                "tas_higher": len(df_results[df_results["tas_max_torque_nm"] > df_results["analytical_key_capacity_nm"]]),
                "key_higher": len(df_results[df_results["analytical_key_capacity_nm"] > df_results["tas_max_torque_nm"]]),
            },
            "tas_vs_spline": {
                "tas_higher": len(df_results[df_results["tas_max_torque_nm"] > df_results["analytical_spline_capacity_nm"]]),
                "spline_higher": len(df_results[df_results["analytical_spline_capacity_nm"] > df_results["tas_max_torque_nm"]]),
            },
        }
    }
    
    # Save summary
    summary_file = OUTPUT_DIR / "tas_comparison_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary to {summary_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal samples analyzed: {summary['total_samples']}")
    print(f"\nAnalytical predictions:")
    for label, count in summary["analytical_predictions"].items():
        print(f"  {label}: {count}")
    print(f"\nML predictions:")
    for label, count in summary["ml_predictions"].items():
        print(f"  {label}: {count}")
    print(f"\nCapacity comparison (TAS vs Model):")
    print(f"  TAS vs Press: TAS higher in {summary['capacity_comparison']['tas_vs_press']['tas_higher']} cases")
    print(f"  TAS vs Key: TAS higher in {summary['capacity_comparison']['tas_vs_key']['tas_higher']} cases")
    print(f"  TAS vs Spline: TAS higher in {summary['capacity_comparison']['tas_vs_spline']['tas_higher']} cases")
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print("  - tas_comparison_results.csv: Detailed comparison data")
    print("  - tas_comparison_summary.json: Summary statistics")


if __name__ == "__main__":
    run_comparison()


