# 🚀 Quick Start Guide

## Running the Application

You need **TWO terminals** - one for backend, one for frontend.

### Step 1: Start Backend (Terminal 1)

```bash
# Navigate to Bachelor_Code directory
cd ../

# Activate virtual environment (if using one)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the backend server
python main.py
```

✅ You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test it**: Open http://localhost:8000/docs in your browser

### Step 2: Start Frontend (Terminal 2)

```bash
# Make sure you're in shaft-connection-selector directory
# Install dependencies (first time only)
npm install

# Start the React app
npm start
```

✅ The app will automatically open at http://localhost:3000

## ✅ Verify Everything Works

1. **Backend is running**: http://localhost:8000/docs should show Swagger UI
2. **Frontend is running**: http://localhost:3000 should show the app
3. **Materials load**: Check browser console (F12) - should see materials list loaded
4. **API works**: Try submitting a form - should get recommendations

## 🔧 Troubleshooting

### "Network Error" or "Cannot GET /materials"

**Problem**: Frontend can't reach backend

**Solutions**:
1. ✅ Make sure backend is running (check Terminal 1)
2. ✅ Check backend URL: http://localhost:8000/docs should work
3. ✅ Check browser console for exact error message
4. ✅ Verify CORS is configured (backend allows localhost:3000)

### Backend won't start

**Problem**: Python errors or missing dependencies

**Solutions**:
1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Check Python version: `python --version` (need 3.8+)
3. ✅ Verify model files exist: `ls models/connection_classifier.pkl`
4. ✅ Check for port conflicts: Is port 8000 already in use?

### Frontend won't start

**Problem**: Node.js errors

**Solutions**:
1. ✅ Install dependencies: `npm install`
2. ✅ Check Node version: `node --version` (need 14+)
3. ✅ Clear cache: `rm -rf node_modules package-lock.json && npm install`
4. ✅ Check for port conflicts: Is port 3000 already in use?

## 📝 Current Configuration

- **Backend URL**: `http://localhost:8000`
- **Frontend URL**: `http://localhost:3000`
- **API Base**: Configured in `src/App.js` as `API_BASE`
- **CORS**: Backend allows `http://localhost:3000` by default

## 🎯 Next Steps

Once both are running:
1. Fill in the form with design parameters
2. Adjust preference sliders
3. Click "Find Optimal Connection"
4. View results!

---

**Need help?** Check `SETUP.md` for more detailed troubleshooting.


