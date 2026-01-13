# 🚀 Deploy to Vercel - Quick Guide

## Prerequisites

1. ✅ Vercel account: [vercel.com](https://vercel.com) (free)
2. ✅ Backend deployed (Heroku, Railway, or Render)
3. ✅ Backend URL ready (e.g., `https://your-backend.herokuapp.com`)

## Step-by-Step Deployment

### Step 1: Deploy Backend to Railway ⚠️

**You MUST deploy the backend before the frontend!**

**Quick Railway Setup:**
1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository and `Bachelor_Code` directory
4. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `CORS_ORIGINS` = `http://localhost:3000`
6. Get your Railway URL: `https://your-app.up.railway.app`

**Detailed guide**: See `../RAILWAY_DEPLOYMENT.md` or `../RAILWAY_QUICK_START.md`

### Step 2: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 3: Login to Vercel

```bash
vercel login
```

### Step 4: Deploy Frontend

```bash
# Make sure you're in this directory
cd Bachelor_Code/shaft-connection-selector

# Deploy
vercel
```

**Follow the prompts:**
- Set up and deploy? → **Yes**
- Which scope? → **Your account**
- Link to existing project? → **No** (first time)
- Project name? → **shaft-connection-selector** (or your choice)
- Directory? → **./** (press Enter)
- Override settings? → **No**

### Step 5: Set Environment Variable

```bash
vercel env add REACT_APP_API_URL
```

**Enter your backend URL:**
```
https://your-app.up.railway.app
```
(Use your Railway URL from Step 1)

**Select environments:**
- Production: **Yes**
- Preview: **Yes**  
- Development: **Yes**

### Step 6: Deploy to Production

```bash
vercel --prod
```

### Step 7: Update Backend CORS

Update your Railway backend to allow your Vercel domain:

**In Railway Dashboard:**
1. Go to your service → **Variables** tab
2. Edit `CORS_ORIGINS` variable
3. Update value to: `https://your-app.vercel.app,https://your-app-git-main.vercel.app,http://localhost:3000`
4. Railway will auto-redeploy with new CORS settings

## ✅ Verify Deployment

1. **Visit your Vercel URL**: `https://your-app.vercel.app`
2. **Check materials load**: Open browser console (F12)
3. **Test form submission**: Fill form and submit
4. **Check backend**: `https://your-backend.herokuapp.com/docs`

## 🔄 Updating Your Deployment

### Update Frontend

```bash
# Make changes, then:
git add .
git commit -m "Update frontend"
git push

# If connected to GitHub, Vercel auto-deploys
# Or manually:
vercel --prod
```

### Update Backend

```bash
cd ../  # Go to Bachelor_Code
git push heroku main  # or your deployment method
```

## 🐛 Troubleshooting

### "Network Error" on Vercel

1. ✅ Check `REACT_APP_API_URL` in Vercel dashboard → Settings → Environment Variables
2. ✅ Verify backend is running: Visit backend URL + `/docs`
3. ✅ Check CORS allows Vercel domain
4. ✅ Rebuild: `vercel --prod`

### CORS Error

**Update backend CORS** to include your Vercel URL:
- Production: `https://your-app.vercel.app`
- Preview: `https://your-app-git-*.vercel.app`

### Environment Variable Not Working

1. ✅ Variable name must start with `REACT_APP_`
2. ✅ Rebuild after adding: `vercel --prod`
3. ✅ Check in Vercel dashboard → Settings → Environment Variables

## 📋 Quick Command Reference

```bash
# Deploy to Vercel
vercel

# Deploy to production
vercel --prod

# Add environment variable
vercel env add REACT_APP_API_URL

# View environment variables
vercel env ls

# View deployment logs
vercel logs
```

## 🎯 Your URLs

After deployment, you'll have:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.herokuapp.com` (or your platform)
- **API Docs**: `https://your-backend.herokuapp.com/docs`

---

**Need more help?** See `VERCEL_DEPLOYMENT.md` for detailed instructions.

