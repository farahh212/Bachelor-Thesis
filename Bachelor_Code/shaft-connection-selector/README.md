# Shaft–Hub Connection Selector Frontend

React-based frontend for the Shaft–Hub Connection Selector application.

## Quick Start

### Prerequisites

1. **Backend must be running** on `http://localhost:8000`
   - Navigate to `../` (parent directory)
   - Run: `python main.py`

2. **Node.js 14+** installed

### Installation

```bash
npm install
```

### Development

```bash
npm start
```

The app will open at `http://localhost:3000` and automatically proxy API requests to the backend.

### Production Build

```bash
npm run build
```

This creates a `build/` folder with optimized production files.

## Configuration

### API Backend URL

The app automatically uses a proxy in development (configured in `package.json`).

For production, set the `REACT_APP_API_URL` environment variable:

```bash
# Linux/Mac
export REACT_APP_API_URL=http://your-backend-url.com
npm run build

# Windows
set REACT_APP_API_URL=http://your-backend-url.com
npm run build
```

Or create a `.env.production` file:
```
REACT_APP_API_URL=http://your-backend-url.com
```

## Backend Setup

The frontend requires the FastAPI backend to be running. 

### Option 1: Separate Backend (Recommended for Development)

1. **Start Backend** (in parent `Bachelor_Code/` directory):
```bash
cd ..
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

2. **Start Frontend** (in this directory):
```bash
npm start
```

The proxy in `package.json` will forward all `/api/*` requests to `http://localhost:8000`.

### Option 2: Backend Serves Frontend (Production)

For production, you can configure the FastAPI backend to serve the React build files. See the backend documentation for details.

## Troubleshooting

### "Cannot GET /materials" or API errors

**Problem**: Backend is not running or not accessible.

**Solution**: 
1. Ensure backend is running on `http://localhost:8000`
2. Test backend directly: `curl http://localhost:8000/materials`
3. Check browser console for CORS errors
4. Verify proxy configuration in `package.json`

### CORS Errors

**Problem**: Browser blocks requests due to CORS policy.

**Solution**: 
1. Ensure backend CORS is configured to allow `http://localhost:3000`
2. Check `main.py` CORS settings
3. In development, the proxy should handle this automatically

### Environment Variables Not Working

**Problem**: `REACT_APP_API_URL` not being used.

**Solution**:
- Environment variables must start with `REACT_APP_`
- Restart the dev server after changing `.env` files
- Rebuild for production after changing environment variables

## Project Structure

```
shaft-connection-selector/
├── public/          # Static files
├── src/
│   ├── App.js      # Main component
│   ├── App.css     # Styles
│   └── ...
├── package.json    # Dependencies and scripts
└── README.md       # This file
```

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (irreversible)

## Learn More

- [React Documentation](https://reactjs.org/)
- [Create React App Documentation](https://facebook.github.io/create-react-app/docs/getting-started)
