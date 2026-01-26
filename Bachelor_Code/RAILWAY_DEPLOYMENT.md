# Deploying Backend to Railway

This guide covers deploying the FastAPI backend to Railway, a modern platform that's perfect for Python applications.

## Prerequisites

1. GitHub account (Railway uses GitHub for deployment)
2. Railway account: [railway.app](https://railway.app) (free signup)
3. Your code pushed to a GitHub repository

## Step 1: Prepare Your Repository

Make sure your code is on GitHub:

```bash
# If not already a git repo
cd Bachelor_Code
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
# (Do this on GitHub website or use GitHub CLI)
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

## Step 2: Deploy to Railway

### Method 1: Using Railway Dashboard (Recommended)

1. **Go to [railway.app](https://railway.app)**
2. **Sign up/Login** (use GitHub to sign in)
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Select your repository**
6. **Railway will auto-detect** it's a Python project

### Method 2: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd Bachelor_Code
railway init

# Deploy
railway up
```

## Step 3: Configure Railway

### Automatic Configuration

Railway should auto-detect:
- **Language**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: Needs to be set manually (see below)

### Manual Configuration

1. **Go to your project** in Railway dashboard
2. **Click on your service**
3. **Go to "Settings" tab**

**Set Start Command:**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Or create `railway.json`** in `Bachelor_Code/`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Step 4: Set Environment Variables

In Railway dashboard → Your Service → Variables:

1. **Click "New Variable"**
2. **Add CORS_ORIGINS**:
   - Key: `CORS_ORIGINS`
   - Value: `https://your-frontend.vercel.app,http://localhost:3000`
   - (Update with your actual Vercel URL after frontend deployment)

**Optional Variables:**
- `PORT`: Railway sets this automatically, but you can override if needed
- `PYTHON_VERSION`: `3.11` (if you want to specify)

## Step 5: Deploy

Railway will automatically:
1. Detect Python
2. Install dependencies from `requirements.txt`
3. Start your application

**Check deployment logs** in Railway dashboard to see progress.

## Step 6: Get Your Backend URL

1. **Go to your service** in Railway dashboard
2. **Click "Settings"** tab
3. **Find "Domains"** section
4. **Click "Generate Domain"** (if not auto-generated)
5. **Copy your Railway URL**: `https://your-app.up.railway.app`

## Step 7: Verify Deployment

1. **Test root endpoint**: `https://your-app.up.railway.app/`
   - Should return: `{"message": "Shaft Connection Selector API"}`

2. **Test materials endpoint**: `https://your-app.up.railway.app/materials`
   - Should return: `{"materials": [...]}`

3. **Test API docs**: `https://your-app.up.railway.app/docs`
   - Should show Swagger UI

## Step 8: Update CORS for Vercel

After deploying your frontend to Vercel:

1. **Get your Vercel URL**: `https://your-app.vercel.app`
2. **Update Railway environment variable**:
   - Go to Railway → Your Service → Variables
   - Edit `CORS_ORIGINS`
   - Add your Vercel URL: `https://your-app.vercel.app,http://localhost:3000`
3. **Redeploy** (Railway auto-redeploys when env vars change)

## Troubleshooting

### Issue: Build Fails

**Problem**: Dependencies not installing

**Solutions**:
1. ✅ Check `requirements.txt` exists and is correct
2. ✅ Check Railway logs for specific error
3. ✅ Verify Python version compatibility
4. ✅ Ensure all dependencies are listed in `requirements.txt`

### Issue: Application Won't Start

**Problem**: Start command incorrect

**Solutions**:
1. ✅ Verify start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. ✅ Check Railway logs for errors
3. ✅ Ensure `main.py` is in root of `Bachelor_Code/`
4. ✅ Verify model files exist (they should be in repo or uploaded)

### Issue: Model Files Not Found

**Problem**: `connection_classifier.pkl` not found

**Solutions**:
1. ✅ Ensure model files are committed to git:
   ```bash
   git add models/connection_classifier.pkl
   git add models/connection_classifier_meta.pkl
   git commit -m "Add model files"
   git push
   ```
2. ✅ Check file paths in `model_service.py` are relative
3. ✅ Verify files are in `models/` directory

### Issue: CORS Errors

**Problem**: Frontend can't access backend

**Solutions**:
1. ✅ Check `CORS_ORIGINS` environment variable includes frontend URL
2. ✅ Verify format: `https://your-app.vercel.app,http://localhost:3000` (comma-separated, no spaces)
3. ✅ Redeploy after changing environment variables

### Issue: Port Already in Use

**Problem**: Railway port configuration

**Solutions**:
1. ✅ Use `$PORT` environment variable (Railway provides this)
2. ✅ Don't hardcode port number
3. ✅ Start command should use: `--port $PORT`

## Railway-Specific Tips

### Custom Domain (Optional)

1. **Go to Settings** → **Domains**
2. **Add Custom Domain**
3. **Follow DNS configuration instructions**
4. **Update CORS** to include custom domain

### Monitoring

Railway provides:
- **Deployment logs**: Real-time build and runtime logs
- **Metrics**: CPU, memory usage
- **Deployments**: History of all deployments

### Auto-Deploy

Railway automatically deploys when you push to GitHub:
- Push to `main` branch → Production deployment
- Create PR → Preview deployment

### Environment Variables

Railway supports:
- **Service-level variables**: For this service only
- **Project-level variables**: Shared across services
- **Secrets**: Encrypted variables (for sensitive data)

## Cost

Railway offers:
- **Free tier**: $5 credit/month
- **Pay-as-you-go**: After free credit
- **Estimated cost**: ~$5-10/month for this app (depending on usage)

## Quick Commands (Railway CLI)

```bash
# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Open in browser
railway open

# Set environment variable
railway variables set CORS_ORIGINS="https://your-app.vercel.app"

# Deploy
railway up
```

## File Structure for Railway

Railway expects:
```
Bachelor_Code/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── models/              # Model files (must be in repo)
│   ├── connection_classifier.pkl
│   └── connection_classifier_meta.pkl
├── make_prediction.py
├── model_service.py
└── railway.json         # Optional config
```

## Next Steps

After Railway deployment:

1. ✅ **Get your Railway URL**: `https://your-app.up.railway.app`
2. ✅ **Test endpoints**: Visit `/docs` to verify
3. ✅ **Deploy frontend to Vercel**: Use Railway URL as `REACT_APP_API_URL`
4. ✅ **Update CORS**: Add Vercel URL to `CORS_ORIGINS`

---

**Need help?** Check Railway docs: https://docs.railway.app


