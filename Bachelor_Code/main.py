# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from make_prediction import select_shaft_connection

app = FastAPI(title="Shaft Connection Selector API")

# CORS middleware to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Pydantic models for request/response
# -----------------------
class UserPreferences(BaseModel):
    ease: float = 0.5
    movement: float = 0.5
    cost: float = 0.5
    vibration: float = 0.5
    speed: float = 0.5
    bidirectional: float = 0.5

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

class ConnectionResult(BaseModel):
    recommended_connection: str
    required_torque_Nmm: float
    capacities_Nmm: Dict[str, float]
    scores: Optional[Dict[str, float]]
    feasible: bool
    reason: Optional[str] = None
    input_parameters: Dict[str, Any]
    details: Dict[str, Any]

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

@app.post("/select-connection", response_model=ConnectionResult)
async def select_connection(request: ShaftConnectionRequest):
    try:
        result = select_shaft_connection(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)