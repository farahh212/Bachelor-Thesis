# 🚂 Railway Quick Start - 5 Minutes

## Prerequisites

- ✅ GitHub account
- ✅ Code pushed to GitHub
- ✅ Railway account: [railway.app](https://railway.app)

## Step-by-Step

### 1. Sign Up for Railway

Go to [railway.app](https://railway.app) and sign up with GitHub.

### 2. Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Select **`Bachelor_Code`** as the root directory

### 3. Configure Start Command

Railway should auto-detect Python, but verify:

1. Click on your service
2. Go to **Settings** tab
3. Set **Start Command**:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### 4. Add Environment Variable

1. Go to **Variables** tab
2. Click **"New Variable"**
3. Add:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `http://localhost:3000` (update with Vercel URL later)

### 5. Get Your URL

1. Go to **Settings** → **Domains**
2. Click **"Generate Domain"** (if needed)
3. Copy your URL: `https://your-app.up.railway.app`

### 6. Test It

Visit: `https://your-app.up.railway.app/docs`

You should see the Swagger UI! 🎉

## ✅ Done!

Your backend is now live on Railway!

**Next**: Deploy frontend to Vercel using this Railway URL.

---

**Troubleshooting?** See `RAILWAY_DEPLOYMENT.md` for detailed help.

