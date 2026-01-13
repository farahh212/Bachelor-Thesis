# Railway Deployment Checklist

Use this checklist to ensure your backend is ready for Railway deployment.

## Pre-Deployment Checklist

### Code Preparation
- [ ] Code is pushed to GitHub repository
- [ ] `requirements.txt` exists and is up-to-date
- [ ] `main.py` is the entry point
- [ ] Model files exist: `models/connection_classifier.pkl` and `models/connection_classifier_meta.pkl`
- [ ] Model files are committed to git (or uploaded separately)
- [ ] `railway.json` is created (optional but recommended)

### Railway Account
- [ ] Railway account created: [railway.app](https://railway.app)
- [ ] GitHub account connected to Railway
- [ ] Repository is accessible to Railway

## Deployment Steps

### Step 1: Create Project
- [ ] Click "New Project" in Railway
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your repository
- [ ] Select `Bachelor_Code` as root directory (or adjust if different)

### Step 2: Configure Service
- [ ] Railway auto-detected Python (verify in settings)
- [ ] Start command set: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Build command: `pip install -r requirements.txt` (auto-detected)

### Step 3: Environment Variables
- [ ] `CORS_ORIGINS` variable added
- [ ] Value set to: `http://localhost:3000` (update with Vercel URL later)
- [ ] `PORT` variable (Railway sets automatically, don't override)

### Step 4: Deploy
- [ ] Deployment started (check logs)
- [ ] Build completed successfully
- [ ] Application started successfully
- [ ] No errors in deployment logs

### Step 5: Get URL
- [ ] Domain generated in Railway
- [ ] URL copied: `https://your-app.up.railway.app`
- [ ] URL tested: Visit `/docs` endpoint

## Verification

### Test Endpoints
- [ ] Root endpoint works: `GET /` returns `{"message": "Shaft Connection Selector API"}`
- [ ] Materials endpoint works: `GET /materials` returns materials list
- [ ] API docs accessible: `GET /docs` shows Swagger UI
- [ ] Connection selection works: `POST /select-connection` with test data

### CORS Configuration
- [ ] CORS allows `http://localhost:3000` (for local testing)
- [ ] CORS will be updated with Vercel URL after frontend deployment

## Post-Deployment

### After Frontend Deployment
- [ ] Get Vercel frontend URL
- [ ] Update `CORS_ORIGINS` in Railway to include Vercel URL
- [ ] Test frontend → backend connection
- [ ] Verify materials load in frontend
- [ ] Test form submission end-to-end

### Monitoring
- [ ] Check Railway dashboard for deployment status
- [ ] Review logs for any errors
- [ ] Monitor resource usage (CPU, memory)

## Troubleshooting Checklist

If something doesn't work:

- [ ] Check Railway deployment logs
- [ ] Verify all dependencies in `requirements.txt`
- [ ] Confirm model files are accessible
- [ ] Test endpoints directly (curl or browser)
- [ ] Verify environment variables are set
- [ ] Check CORS configuration
- [ ] Review Railway documentation

## Quick Reference

**Railway Dashboard**: https://railway.app
**Your Service URL**: `https://your-app.up.railway.app`
**API Docs**: `https://your-app.up.railway.app/docs`
**Materials Endpoint**: `https://your-app.up.railway.app/materials`

---

**Status**: Ready for Railway deployment! 🚂

