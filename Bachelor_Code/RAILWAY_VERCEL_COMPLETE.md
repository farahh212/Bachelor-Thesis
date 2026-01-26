# Complete Deployment Guide: Railway Backend + Vercel Frontend

This is your complete step-by-step guide to deploy both backend (Railway) and frontend (Vercel).

## 🎯 Overview

- **Backend**: Railway (FastAPI)
- **Frontend**: Vercel (React)
- **Total Time**: ~15 minutes

## Part 1: Deploy Backend to Railway

### Step 1: Prepare GitHub Repository

```bash
# Make sure your code is on GitHub
cd Bachelor_Code
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (recommended)

### Step 3: Deploy to Railway

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Choose your repository**
4. **Select `Bachelor_Code` as root directory**
   - If Railway shows the whole repo, you can set root directory in settings later

### Step 4: Configure Railway

1. **Click on your service** (the deployed app)
2. **Go to "Settings" tab**
3. **Set Start Command**:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
4. **Verify Build Command** (should be auto-detected):
   ```
   pip install -r requirements.txt
   ```

### Step 5: Add Environment Variable

1. **Go to "Variables" tab**
2. **Click "New Variable"**
3. **Add**:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `http://localhost:3000`
   - (We'll update this with Vercel URL later)

### Step 6: Get Your Railway URL

1. **Go to "Settings" → "Domains"**
2. **Click "Generate Domain"** (if not auto-generated)
3. **Copy your URL**: `https://your-app.up.railway.app`

### Step 7: Test Backend

1. **Visit**: `https://your-app.up.railway.app/docs`
2. **Should see**: Swagger UI with API documentation
3. **Test materials**: `https://your-app.up.railway.app/materials`
4. **Should return**: `{"materials": [...]}`

✅ **Backend is live!** Note your Railway URL.

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy Frontend

```bash
# Navigate to frontend directory
cd Bachelor_Code/shaft-connection-selector

# Deploy
vercel
```

**Follow prompts:**
- Set up and deploy? → **Yes**
- Which scope? → **Your account**
- Link to existing project? → **No** (first time)
- Project name? → **shaft-connection-selector**
- Directory? → **./** (press Enter)
- Override settings? → **No**

### Step 4: Set Environment Variable

```bash
vercel env add REACT_APP_API_URL
```

**Enter your Railway backend URL:**
```
https://your-app.up.railway.app
```

**Select environments:**
- Production: **Yes**
- Preview: **Yes**
- Development: **Yes**

### Step 5: Deploy to Production

```bash
vercel --prod
```

### Step 6: Get Your Vercel URL

After deployment, Vercel will show:
- **Production URL**: `https://your-app.vercel.app`
- **Preview URLs**: `https://your-app-git-*.vercel.app`

✅ **Frontend is live!** Note your Vercel URL.

---

## Part 3: Connect Frontend and Backend

### Step 1: Update Railway CORS

1. **Go to Railway dashboard** → Your service → **Variables**
2. **Edit `CORS_ORIGINS` variable**
3. **Update value to**:
   ```
   https://your-app.vercel.app,https://your-app-git-main.vercel.app,http://localhost:3000
   ```
   (Replace `your-app` with your actual Vercel app name)
4. **Save** - Railway will auto-redeploy

### Step 2: Verify Connection

1. **Visit your Vercel URL**: `https://your-app.vercel.app`
2. **Open browser console** (F12)
3. **Check Network tab**:
   - Materials should load from Railway backend
   - No CORS errors
4. **Test form submission**:
   - Fill in the form
   - Submit
   - Should get recommendations from Railway backend

---

## ✅ Final Checklist

- [ ] Backend deployed to Railway
- [ ] Backend URL works: `https://your-app.up.railway.app/docs`
- [ ] Frontend deployed to Vercel
- [ ] Frontend URL works: `https://your-app.vercel.app`
- [ ] `REACT_APP_API_URL` set in Vercel
- [ ] `CORS_ORIGINS` updated in Railway with Vercel URL
- [ ] Materials load in frontend
- [ ] Form submission works end-to-end

---

## 🔗 Your URLs

After deployment:

- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-app.up.railway.app`
- **API Docs**: `https://your-app.up.railway.app/docs`
- **Materials**: `https://your-app.up.railway.app/materials`

---

## 🐛 Troubleshooting

### Frontend can't reach backend

1. ✅ Check `REACT_APP_API_URL` in Vercel dashboard
2. ✅ Verify Railway backend is running
3. ✅ Check CORS includes Vercel URL
4. ✅ Test backend directly: Visit Railway URL + `/docs`

### CORS errors

1. ✅ Update `CORS_ORIGINS` in Railway with exact Vercel URL
2. ✅ Include both production and preview URLs
3. ✅ Wait for Railway to redeploy after changing env vars

### Materials not loading

1. ✅ Check browser console for errors
2. ✅ Verify backend `/materials` endpoint works
3. ✅ Check Network tab in browser dev tools

---

## 📝 Updating Your Deployment

### Update Backend

```bash
cd Bachelor_Code
# Make changes
git add .
git commit -m "Update backend"
git push
# Railway auto-deploys from GitHub
```

### Update Frontend

```bash
cd Bachelor_Code/shaft-connection-selector
# Make changes
git add .
git commit -m "Update frontend"
git push
# Vercel auto-deploys from GitHub (if connected)
# Or manually: vercel --prod
```

---

## 💰 Cost

- **Railway**: $5 free credit/month, then pay-as-you-go (~$5-10/month)
- **Vercel**: Free tier (unlimited deployments, 100GB bandwidth)

**Total estimated cost**: ~$5-10/month (mostly Railway)

---

**Congratulations!** Your application is now live! 🎉


