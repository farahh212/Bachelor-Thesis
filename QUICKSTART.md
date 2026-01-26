# Quick Start Guide

Get the Shaft–Hub Connection Selector running in 5 minutes!

## Prerequisites Check

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 14+ installed (`node --version`)
- [ ] npm installed (`npm --version`)

## Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd Bachelor-Thesis
```

## Step 2: Setup Backend

```bash
cd Bachelor_Code

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Verify Model Files

Ensure these files exist:
- `models/connection_classifier.pkl`
- `models/connection_classifier_meta.pkl`

If missing, you'll need to train the model first (see [Training the Model](#training-the-model)).

## Step 4: Start Backend

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it: Open http://localhost:8000/docs in your browser.

## Step 5: Setup Frontend

Open a new terminal:

```bash
cd Bachelor_Code/shaft-connection-selector

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3000

## Step 6: Use the Application

1. Fill in the form with your design parameters
2. Adjust preference sliders
3. Click "Find Optimal Connection"
4. View both analytical and ML recommendations!

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError`
- **Solution**: Make sure virtual environment is activated and dependencies are installed

**Error**: Model files not found
- **Solution**: Train the model first (see below) or ensure model files are in `models/` directory

### Frontend won't connect to backend

**Error**: CORS error
- **Solution**: Check that backend is running on port 8000 and frontend is on port 3000

**Error**: Network error
- **Solution**: Verify `API_BASE` in `App.js` points to `http://localhost:8000`

## Training the Model (Optional)

If you want to regenerate the dataset and retrain:

```bash
cd Bachelor_Code

# Generate synthetic dataset
python generate_dataset.py

# Train the model
python train_connection_classifier.py
```

This will:
1. Generate ~5,000 synthetic samples
2. Train multiple ML models
3. Select the best model (CatBoost)
4. Save to `models/` directory

**Note**: This process takes several minutes.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Explore the API at http://localhost:8000/docs

## Need Help?

- Check the [README.md](README.md) for detailed information
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
- Open an issue on GitHub

---

Happy designing! 🚀


