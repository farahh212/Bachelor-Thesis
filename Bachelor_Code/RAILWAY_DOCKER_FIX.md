# Fixing Railway Docker Build Error

## Problem

Railway is trying to run `npm install` even though this is a Python backend project.

## Solution 1: Force Railway to Use Dockerfile

1. **In Railway Dashboard**:
   - Go to your service → **Settings**
   - Under **Deploy** section
   - Set **Builder** to **"Dockerfile"** (not "Nixpacks" or "Auto")
   - This forces Railway to use only the Dockerfile

2. **Clear build cache** (if needed):
   - In Railway → Your service → **Deployments**
   - Click on failed deployment
   - Click **"Redeploy"** or **"Clear Cache and Redeploy"**

## Solution 2: Verify Dockerfile Location

Make sure Railway is using the correct Dockerfile:

1. **Check root directory** in Railway:
   - Settings → **Root Directory** should be `Bachelor_Code` (or `.` if repo root)
   - If Railway is looking at repo root, it might find the frontend `package.json`

2. **Verify Dockerfile exists** in the correct location:
   - Should be at: `Bachelor_Code/Dockerfile`
   - Not at: `Bachelor_Code/shaft-connection-selector/Dockerfile`

## Solution 3: Update Railway Configuration

If Railway is auto-detecting Node.js:

1. **Disable auto-detection**:
   - In Railway → Settings → **Build & Deploy**
   - Uncheck "Auto-detect build settings"
   - Set explicitly: **Builder = Dockerfile**

2. **Or use railway.json** to force Docker:
   ```json
   {
     "build": {
       "builder": "DOCKERFILE"
     }
   }
   ```

## Solution 4: Check for package.json in Root

If there's a `package.json` in `Bachelor_Code/` directory, Railway might be confused:

```bash
# Check if package.json exists in Bachelor_Code
ls Bachelor_Code/package.json

# If it exists, either:
# 1. Delete it (if not needed)
# 2. Or add to .dockerignore
```

## Solution 5: Use Explicit Docker Build

In Railway CLI:

```bash
railway up --dockerfile Bachelor_Code/Dockerfile
```

## Verification

After fixing, the build should show:
```
Step 1/7 : FROM python:3.11-slim
Step 2/7 : WORKDIR /app
Step 3/7 : COPY requirements.txt .
Step 4/7 : RUN pip install ...
```

**NOT**:
```
Step X : RUN npm install  ← This should NOT appear
```

## Current Dockerfile (Correct)

The Dockerfile in `Bachelor_Code/` is correct:
- Uses `python:3.11-slim` base image
- Only installs Python packages via `pip`
- No npm/node commands
- Excludes frontend via `.dockerignore`

## If Still Failing

1. **Check Railway logs** for the exact error
2. **Verify root directory** is set correctly
3. **Try deleting and recreating** the service in Railway
4. **Use Nixpacks instead** (see `RAILWAY_FIX.md`)

---

The Dockerfile is correct. The issue is Railway's build detection. Force it to use Dockerfile explicitly.

