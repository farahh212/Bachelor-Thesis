# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from make_prediction import select_shaft_connection
from model_service import predict_connection

app = FastAPI(title="Shaft Connection Selector API")

# CORS middleware to allow React frontend to connect
# Can be configured via environment variable CORS_ORIGINS (comma-separated)
import os
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Pydantic models for request/response
# -----------------------
class UserPreferences(BaseModel):
    """8 criteria for connection selection scoring."""
    ease: float = 0.5           # Assembly/disassembly ease importance
    movement: float = 0.5       # Frequent axial movement importance
    cost: float = 0.5           # Low manufacturing cost importance
    bidirectional: float = 0.5  # Bidirectional torque importance
    vibration: float = 0.5      # Vibration resistance importance
    speed: float = 0.5          # High-speed suitability importance
    maintenance: float = 0.5    # Easy maintenance/repair importance
    durability: float = 0.5     # Fatigue life / durability importance

class ShaftConnectionRequest(BaseModel):
    shaft_diameter: float
    hub_length: float
    shaft_material: str
    hub_material: str
    shaft_type: str = "solid"
    has_bending: bool = True
    required_torque: Optional[float] = None
    user_preferences: UserPreferences
    # Advanced parameters (all optional)
    safety_factor: float = 1.5
    surface_roughness_shaft: float = 12.0
    surface_roughness_hub: float = 12.0
    hub_outer_diameter: Optional[float] = None
    shaft_inner_diameter: Optional[float] = None
    assembly_method: str = "heat_hub"
    torque_coefficient: float = 135.0
    # New: surface condition for friction coefficient (DIN 7190)
    surface_condition: str = "dry"  # "dry", "oiled", or "greased"
    mu_override: Optional[float] = None  # Manual friction coefficient override
    spline_major_diameter_override: Optional[float] = None
    spline_tooth_count_override: Optional[int] = None

class ConnectionResult(BaseModel):
    recommended_connection: str
    required_torque_Nmm: float
    capacities_Nmm: Dict[str, float]
    scores: Optional[Dict[str, float]]
    feasible: bool
    reason: Optional[str] = None
    mu_used: Optional[float] = None
    surface_condition: Optional[str] = None
    hub_stiffness_factor: Optional[float] = None
    input_parameters: Dict[str, Any]
    details: Dict[str, Any]
    ml_recommendation: Optional[str] = None
    ml_probabilities: Optional[Dict[str, float]] = None

    feasible_connections_count: Optional[int] = None
    M_design_Nmm: Optional[float] = None

# -----------------------
# API Endpoints
# -----------------------
@app.get("/")
async def root():
    return {"message": "Shaft Connection Selector API"}

@app.get("/materials")
async def get_materials():
    from make_prediction import materials
    return {"materials": list(materials.keys())}

def _assemble_ml_features(request: ShaftConnectionRequest) -> Dict[str, Any]:
    prefs = request.user_preferences
    return {
        "shaft_diameter": request.shaft_diameter,
        "hub_length": request.hub_length,
        "has_bending": float(request.has_bending),
        "safety_factor": request.safety_factor,
        "hub_outer_diameter": request.hub_outer_diameter or 0.0,
        "shaft_inner_diameter": request.shaft_inner_diameter or 0.0,
        "required_torque": request.required_torque or 0.0,
        "pref_ease": prefs.ease,
        "pref_movement": prefs.movement,
        "pref_cost": prefs.cost,
        "pref_vibration": prefs.vibration,
        "pref_speed": prefs.speed,
        "pref_bidirectional": prefs.bidirectional,
        "pref_maintenance": prefs.maintenance,
        "pref_durability": prefs.durability,
        "shaft_type": request.shaft_type,
        "shaft_material": request.shaft_material,
        "surface_condition": request.surface_condition,
    }


@app.post("/select-connection", response_model=ConnectionResult)
async def select_connection(request: ShaftConnectionRequest):
    try:
        result = select_shaft_connection(request)
        ml_prediction = predict_connection(_assemble_ml_features(request))
        if ml_prediction:
            # Ensure label is a valid connection type string
            label = ml_prediction.get("label")
            if label and isinstance(label, str) and label in ["press", "key", "spline"]:
                result["ml_recommendation"] = label
            else:
                # Fallback: try to convert or use None
                print(f"Warning: Invalid ML label: {label} (type: {type(label)})")
                result["ml_recommendation"] = None
            result["ml_probabilities"] = ml_prediction.get("probs")
        else:
            result["ml_recommendation"] = None
            result["ml_probabilities"] = None
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)