# Deploying to Vercel

This guide covers deploying the React frontend to Vercel and setting up the backend separately.

## Overview

- **Frontend**: Deploy to Vercel (React app)
- **Backend**: Deploy separately (see options below)

## Prerequisites

1. Vercel account (free tier works)
2. Vercel CLI installed: `npm i -g vercel`
3. Backend deployed somewhere (Heroku, Railway, Render, etc.)

## Step 1: Deploy Backend First

You need the backend URL before deploying the frontend.

### Option A: Deploy Backend to Heroku (Recommended)

1. **Install Heroku CLI** and login:
```bash
heroku login
```

2. **Create Heroku app**:
```bash
cd Bachelor_Code
heroku create your-app-name-backend
```

3. **Deploy**:
```bash
git add .
git commit -m "Deploy backend"
git push heroku main
```

4. **Get your backend URL**: `https://your-app-name-backend.herokuapp.com`

### Option B: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repo, choose `Bachelor_Code` directory
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Get your backend URL from Railway dashboard

### Option C: Deploy Backend to Render

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Get your backend URL from Render dashboard

### Update Backend CORS

After deploying backend, update CORS to allow your Vercel domain:

**For Heroku**, set environment variable:
```bash
heroku config:set CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

**Or update `main.py`** to allow all origins (for testing):
```python
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
# Add your Vercel URL here or use environment variable
```

## Step 2: Deploy Frontend to Vercel

### Method 1: Using Vercel CLI (Recommended)

1. **Navigate to frontend directory**:
```bash
cd Bachelor_Code/shaft-connection-selector
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy**:
```bash
vercel
```

4. **Follow prompts**:
   - Set up and deploy? **Yes**
   - Which scope? **Your account**
   - Link to existing project? **No** (first time)
   - Project name? **shaft-connection-selector** (or your choice)
   - Directory? **./** (current directory)
   - Override settings? **No**

5. **Set environment variable**:
```bash
vercel env add REACT_APP_API_URL
# Enter your backend URL: https://your-backend.herokuapp.com
# Select: Production, Preview, Development
```

6. **Redeploy with environment variable**:
```bash
vercel --prod
```

### Method 2: Using Vercel Dashboard (GitHub Integration)

1. **Go to [vercel.com](https://vercel.com)**
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure project**:
   - Framework Preset: **Create React App**
   - Root Directory: `Bachelor_Code/shaft-connection-selector`
   - Build Command: `npm run build`
   - Output Directory: `build`

5. **Add Environment Variable**:
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-backend.herokuapp.com`
   - Apply to: Production, Preview, Development

6. **Click "Deploy"**

## Step 3: Update Frontend Code for Production

The frontend should already work, but verify `App.js` uses the environment variable:

```javascript
const API_BASE = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000');
```

This will use `REACT_APP_API_URL` in production.

## Step 4: Verify Deployment

1. **Check frontend**: Visit your Vercel URL
2. **Check backend**: Visit `https://your-backend.herokuapp.com/docs`
3. **Test connection**: 
   - Open browser console on Vercel site
   - Check if materials load
   - Try submitting a form

## Troubleshooting

### Issue: "Network Error" on Vercel

**Problem**: Frontend can't reach backend

**Solutions**:
1. ✅ Verify backend is deployed and accessible
2. ✅ Check `REACT_APP_API_URL` environment variable in Vercel dashboard
3. ✅ Verify CORS allows your Vercel domain
4. ✅ Check browser console for exact error

### Issue: CORS Error

**Problem**: Backend blocks requests from Vercel

**Solution**: Update backend CORS:
```python
# In main.py or via environment variable
cors_origins = [
    "http://localhost:3000",
    "https://your-app.vercel.app",
    "https://your-app-git-main.vercel.app"  # Preview URLs
]
```

Or set environment variable on backend:
```bash
# Heroku
heroku config:set CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### Issue: Environment Variable Not Working

**Problem**: `REACT_APP_API_URL` not being used

**Solutions**:
1. ✅ Rebuild after setting environment variable: `vercel --prod`
2. ✅ Check variable name starts with `REACT_APP_`
3. ✅ Verify in Vercel dashboard → Settings → Environment Variables
4. ✅ Clear browser cache

### Issue: Build Fails on Vercel

**Problem**: Build errors during deployment

**Solutions**:
1. ✅ Check build logs in Vercel dashboard
2. ✅ Ensure `package.json` has correct build script
3. ✅ Verify all dependencies are in `package.json`
4. ✅ Check Node.js version compatibility

## Updating Your Deployment

### Update Frontend

```bash
cd Bachelor_Code/shaft-connection-selector
# Make your changes
git add .
git commit -m "Update frontend"
git push
# Vercel will auto-deploy if connected to GitHub
```

### Update Backend

```bash
cd Bachelor_Code
# Make your changes
git add .
git commit -m "Update backend"
git push heroku main  # or your deployment method
```

## Custom Domain (Optional)

1. **In Vercel Dashboard**:
   - Go to your project → Settings → Domains
   - Add your custom domain
   - Follow DNS configuration instructions

2. **Update Backend CORS**:
   - Add your custom domain to allowed origins

## Environment Variables Reference

### Frontend (Vercel)
- `REACT_APP_API_URL`: Backend API URL (e.g., `https://your-backend.herokuapp.com`)

### Backend (Heroku/Railway/Render)
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `PORT`: Server port (usually auto-set by platform)

## Quick Deploy Commands

```bash
# Deploy frontend to Vercel
cd Bachelor_Code/shaft-connection-selector
vercel --prod

# Deploy backend to Heroku
cd Bachelor_Code
git push heroku main

# Set environment variable
vercel env add REACT_APP_API_URL
```

## Cost

- **Vercel**: Free tier includes:
  - Unlimited deployments
  - 100GB bandwidth/month
  - Custom domains
- **Heroku**: Free tier available (with limitations) or paid plans
- **Railway**: Free tier with $5 credit/month
- **Render**: Free tier available

---

**Need help?** Check Vercel docs: https://vercel.com/docs


