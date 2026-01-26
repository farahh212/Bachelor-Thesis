# Hybrid Analytical–Machine Learning Framework for Shaft–Hub Connection Selection

A comprehensive decision-support system that combines physics-based analytical models with machine learning to recommend optimal shaft–hub connection types (press fits, keys, and splines) based on mechanical requirements and user preferences.

## 🎯 Overview

This system addresses the challenge of selecting appropriate shaft–hub connections in mechanical engineering by:

- **Analytical Engine**: Implements DIN 7190, DIN 6885, and DIN 5480 standards for torque capacity calculations
- **Machine Learning Model**: Trained on synthetically generated data to provide rapid probabilistic predictions
- **Preference-Weighted Scoring**: Incorporates user priorities across 8 application dimensions
- **Web Application**: Interactive React frontend with FastAPI backend for real-time recommendations

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Three Connection Types**: Press fits (friction closure), parallel keys, and splines (form closure)
- **DIN Standards Compliance**: Based on DIN 7190, DIN 6885, and DIN 5480
- **Hybrid Approach**: Combines analytical feasibility checks with ML predictions
- **Preference-Based Selection**: 8-dimensional preference weighting system
- **Real-Time Recommendations**: Fast API responses with detailed capacity analysis
- **Transparent Outputs**: Shows both analytical and ML recommendations with confidence scores

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend│
│  (Port 8000)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Analytical│ │ ML Model │
│ Engine   │ │ (CatBoost)│
└─────────┘ └──────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd Bachelor_Code
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure the trained model files exist:
   - `models/connection_classifier.pkl`
   - `models/connection_classifier_meta.pkl`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd Bachelor_Code/shaft-connection-selector
```

2. Install Node.js dependencies:
```bash
npm install
```

## 💻 Usage

### Running the Development Server

1. **Start the backend** (from `Bachelor_Code/`):
```bash
python main.py
```
The API will be available at `http://localhost:8000`

2. **Start the frontend** (from `Bachelor_Code/shaft-connection-selector/`):
```bash
npm start
```
The application will open at `http://localhost:3000`

### Using the API Directly

```python
import requests

response = requests.post('http://localhost:8000/select-connection', json={
    "shaft_diameter": 45,
    "hub_length": 50,
    "shaft_material": "Steel C45",
    "hub_material": "Steel C45",
    "shaft_type": "solid",
    "has_bending": True,
    "required_torque": 50000,
    "safety_factor": 1.5,
    "surface_condition": "dry",
    "user_preferences": {
        "ease": 0.5,
        "movement": 0.5,
        "cost": 0.5,
        "bidirectional": 0.5,
        "vibration": 0.5,
        "speed": 0.5,
        "maintenance": 0.5,
        "durability": 0.5
    }
})

print(response.json())
```

## 📁 Project Structure

```
Bachelor_Code/
├── main.py                      # FastAPI backend server
├── make_prediction.py           # Analytical selector engine
├── model_service.py             # ML model loading and prediction
├── generate_dataset.py          # Synthetic dataset generation
├── train_connection_classifier.py  # ML model training
├── requirements.txt             # Python dependencies
├── models/                      # Trained ML models
│   ├── connection_classifier.pkl
│   └── connection_classifier_meta.pkl
├── figures/                     # Dataset visualization figures
├── synthetic_SHC_dataset.csv    # Generated training dataset
└── shaft-connection-selector/   # React frontend
    ├── src/
    │   ├── App.js              # Main React component
    │   └── ...
    └── package.json

thesis/                          # LaTeX thesis document
├── bachelor.tex
├── sections/
└── figures/
```

## 📚 API Documentation

### Endpoints

#### `POST /select-connection`

Main endpoint for connection selection.

**Request Body:**
```json
{
  "shaft_diameter": 45.0,
  "hub_length": 50.0,
  "shaft_material": "Steel C45",
  "hub_material": "Steel C45",
  "shaft_type": "solid",
  "has_bending": true,
  "required_torque": 50000.0,
  "safety_factor": 1.5,
  "surface_condition": "dry",
  "user_preferences": {
    "ease": 0.5,
    "movement": 0.5,
    "cost": 0.5,
    "bidirectional": 0.5,
    "vibration": 0.5,
    "speed": 0.5,
    "maintenance": 0.5,
    "durability": 0.5
  }
}
```

**Response:**
```json
{
  "recommended_connection": "press",
  "feasible_connections": ["press", "spline"],
  "capacities_Nmm": {
    "press": 2200000,
    "key": 1800000,
    "spline": 5000000
  },
  "scores": {
    "press": 0.65,
    "spline": 0.58
  },
  "ml_recommendation": "press",
  "ml_probabilities": {
    "press": 0.75,
    "key": 0.05,
    "spline": 0.20
  }
}
```

#### `GET /materials`

Returns list of available materials.

**Response:**
```json
{
  "materials": [
    "Steel S235",
    "Steel C45",
    "Steel 42CrMo4",
    ...
  ]
}
```

### Interactive API Documentation

When the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 Development

### Generating the Synthetic Dataset

```bash
cd Bachelor_Code
python generate_dataset.py
```

This will create `synthetic_SHC_dataset.csv` with approximately 5,000 samples.

### Training the ML Model

```bash
cd Bachelor_Code
python train_connection_classifier.py
```

This will:
- Load the synthetic dataset
- Train multiple models (Random Forest, XGBoost, LightGBM, CatBoost)
- Select the best model based on macro F1-score
- Save the model and metadata to `models/`

### Running Tests

```bash
# Backend tests (if available)
pytest

# Frontend tests
cd Bachelor_Code/shaft-connection-selector
npm test
```

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deployment

1. **Backend**: Deploy to any Python hosting (Heroku, AWS, Azure, etc.)
2. **Frontend**: Build and deploy static files:
```bash
cd Bachelor_Code/shaft-connection-selector
npm run build
# Deploy the 'build' folder to a static hosting service
```

3. **Update CORS**: Modify `main.py` to allow your frontend domain:
```python
allow_origins=["https://your-frontend-domain.com"]
```

## 📊 Model Performance

The selected CatBoost model achieves:
- **Macro F1-Score**: 0.7986
- **Accuracy**: 0.8458
- **Per-Class Performance**:
  - Press Fit: F1 = 0.6774
  - Key: F1 = 0.8057
  - Spline: F1 = 0.9127

## 🎓 Academic Context

This project was developed as part of a Bachelor's thesis on hybrid analytical–machine learning frameworks for engineering design automation. The thesis document is available in the `thesis/` directory.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- DIN standards (DIN 7190, DIN 6885, DIN 5480) for mechanical design rules
- FastAPI and React communities for excellent frameworks
- CatBoost team for the gradient boosting library

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: This system is intended for preliminary design evaluation and educational purposes. For final design decisions, consult with qualified engineers and perform detailed analysis as appropriate for your application.


