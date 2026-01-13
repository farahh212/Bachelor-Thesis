# Setup Guide - Running Frontend and Backend

This guide explains how to run the React frontend and FastAPI backend together.

## Quick Start

### Option 1: Using Proxy (Recommended for Development)

The `package.json` already has a proxy configured to `http://localhost:8000`.

1. **Start the Backend** (Terminal 1):
```bash
cd ../  # Go to Bachelor_Code directory
python main.py
```
Backend will run on: http://localhost:8000

2. **Start the Frontend** (Terminal 2):
```bash
# You should already be in shaft-connection-selector directory
npm start
```
Frontend will run on: http://localhost:3000

The proxy automatically forwards API requests from the frontend to the backend.

### Option 2: Direct API Calls (Current Setup)

If you want to use direct API calls (current App.js setup):

1. **Start the Backend** (Terminal 1):
```bash
cd ../  # Go to Bachelor_Code directory
python main.py
```

2. **Start the Frontend** (Terminal 2):
```bash
npm start
```

3. **Verify CORS is working**: The backend should allow `http://localhost:3000` by default.

## Troubleshooting

### Issue: "Network Error" or CORS errors

**Solution 1**: Make sure backend is running on port 8000
```bash
# Check if backend is running
curl http://localhost:8000/docs
```

**Solution 2**: Update CORS in backend if needed
Edit `Bachelor_Code/main.py`:
```python
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
```

**Solution 3**: Use the proxy instead
Update `App.js` to use relative URLs:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || '';
```

### Issue: "Cannot GET /materials"

**Solution**: Make sure you're calling the correct endpoint:
- Backend endpoint: `GET /materials`
- Full URL: `http://localhost:8000/materials`
- With proxy: `/materials` (relative URL)

### Issue: Backend not starting

**Solution**: 
1. Check if port 8000 is already in use
2. Install dependencies: `pip install -r requirements.txt`
3. Verify model files exist: `ls models/connection_classifier.pkl`

## Testing the Connection

1. **Test Backend directly**:
```bash
curl http://localhost:8000/materials
```

2. **Test from browser**:
Open: http://localhost:8000/docs (Swagger UI)

3. **Test from Frontend**:
Open browser console and check Network tab when loading materials.

## Production Setup

For production, set environment variable:
```bash
REACT_APP_API_URL=https://your-backend-domain.com
npm run build
```

