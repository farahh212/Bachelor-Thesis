"""
Model Service for ML Prediction

This module loads the trained connection classifier model and provides
prediction functionality for the FastAPI backend.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "connection_classifier.pkl"
META_PATH = MODEL_DIR / "connection_classifier_meta.pkl"

# Global variables for lazy loading
_model = None
_metadata = None


def _load_model():
    """Lazy load the model and metadata."""
    global _model, _metadata
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        if not META_PATH.exists():
            raise FileNotFoundError(f"Metadata file not found: {META_PATH}")
        
        _model = joblib.load(MODEL_PATH)
        _metadata = joblib.load(META_PATH)
    return _model, _metadata


def predict_connection(features: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Predict the recommended shaft-hub connection type using the trained ML model.
    
    Args:
        features: Dictionary containing input features:
            - shaft_diameter: float
            - hub_length: float
            - has_bending: float (0.0 or 1.0)
            - safety_factor: float
            - hub_outer_diameter: float (0.0 if not provided)
            - shaft_inner_diameter: float (0.0 for solid shafts)
            - required_torque: float
            - pref_ease: float (0.0-1.0)
            - pref_movement: float (0.0-1.0)
            - pref_cost: float (0.0-1.0)
            - pref_vibration: float (0.0-1.0)
            - pref_speed: float (0.0-1.0)
            - pref_bidirectional: float (0.0-1.0)
            - pref_maintenance: float (0.0-1.0)
            - pref_durability: float (0.0-1.0)
            - shaft_type: str ("solid" or "hollow")
            - shaft_material: str (material name)
            - surface_condition: str ("dry" or "oiled")
    
    Returns:
        Dictionary with:
            - label: str (predicted connection type: "press", "key", or "spline")
            - probs: dict mapping connection types to probabilities
        Returns None if model cannot be loaded or prediction fails.
    """
    try:
        model, metadata = _load_model()
        
        # Extract feature order from metadata
        feature_list = metadata.get("features", [])
        numeric_features = metadata.get("numeric", [])
        categorical_features = metadata.get("categorical", [])
        
        # Build feature vector in the correct order
        feature_vector = []
        for feat_name in feature_list:
            if feat_name in features:
                feature_vector.append(features[feat_name])
            else:
                # Handle missing features with defaults
                if feat_name in numeric_features:
                    feature_vector.append(0.0)
                else:
                    feature_vector.append("unknown")
        
        # Create DataFrame for prediction
        X = pd.DataFrame([feature_vector], columns=feature_list)
        
        # Ensure numeric features are numeric
        for feat in numeric_features:
            if feat in X.columns:
                X[feat] = pd.to_numeric(X[feat], errors='coerce').fillna(0.0)
        
        # Predict
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # Map prediction index to label
        classes = metadata.get("classes", ["press", "key", "spline"])
        label_mapping = metadata.get("label_mapping", {})
        
        # Convert prediction index to label
        # Handle numpy integers and regular integers
        if isinstance(prediction, (int, np.integer, np.ndarray)):
            pred_idx = int(prediction) if not isinstance(prediction, np.ndarray) else int(prediction.item())
            if 0 <= pred_idx < len(classes):
                pred_label = classes[pred_idx]
            else:
                # Fallback: try to use label_mapping or default to first class
                pred_label = label_mapping.get(pred_idx, classes[0] if classes else "press")
        elif isinstance(prediction, str) and prediction in classes:
            # Already a valid label string
            pred_label = prediction
        else:
            # Last resort: convert to string, but log a warning
            print(f"Warning: Unexpected prediction type/value: {prediction} (type: {type(prediction)})")
            pred_label = str(prediction)
        
        # Build probability dictionary
        prob_dict = {}
        for idx, class_name in enumerate(classes):
            if idx < len(probabilities):
                prob_dict[class_name] = float(probabilities[idx])
        
        return {
            "label": pred_label,
            "probs": prob_dict
        }
    
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error in predict_connection: {e}")
        return None

