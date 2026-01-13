# Fix CORS Errors Between Vercel Frontend and Railway Backend

## Problem

You're getting CORS errors when the Vercel frontend tries to access the Railway backend.

## Solution: Update CORS_ORIGINS in Railway

### Step 1: Get Your Vercel URL

Your Vercel frontend URL should be something like:
- `https://your-app.vercel.app` (production)
- `https://your-app-git-main.vercel.app` (preview)

### Step 2: Update Railway Environment Variable

1. **Go to Railway Dashboard**: [railway.app](https://railway.app)
2. **Select your backend service**
3. **Go to "Variables" tab**
4. **Find or create `CORS_ORIGINS` variable**:
   - If it exists: Click **"Edit"**
   - If it doesn't exist: Click **"New Variable"**
5. **Set the value** to include your Vercel URL(s):
   ```
   https://your-app.vercel.app,https://your-app-git-main.vercel.app,http://localhost:3000
   ```
   Replace `your-app` with your actual Vercel app name.

6. **Save** - Railway will automatically redeploy with the new CORS settings

### Step 3: Verify CORS is Working

1. **Wait for Railway to redeploy** (check deployment status)
2. **Open your Vercel app** in browser
3. **Open browser console** (F12)
4. **Check Network tab** - API calls should work without CORS errors
5. **Test the app** - materials should load, form submission should work

## Example CORS_ORIGINS Value

If your Vercel app is `shaft-connection-selector.vercel.app`, set:

```
https://shaft-connection-selector.vercel.app,https://shaft-connection-selector-git-main.vercel.app,http://localhost:3000
```

This allows:
- ✅ Production Vercel URL
- ✅ Preview Vercel URLs (for PRs)
- ✅ Local development

## Troubleshooting

### Still Getting CORS Errors?

1. **Check the exact error** in browser console:
   - Look for "CORS policy" or "Access-Control-Allow-Origin" errors
   - Note the exact origin that's being blocked

2. **Verify CORS_ORIGINS format**:
   - ✅ Correct: `https://app.vercel.app,http://localhost:3000` (comma-separated, no spaces)
   - ❌ Wrong: `https://app.vercel.app, http://localhost:3000` (spaces cause issues)
   - ❌ Wrong: `["https://app.vercel.app"]` (don't use brackets)

3. **Check Railway deployment logs**:
   - Verify the environment variable was set correctly
   - Check if the app restarted after setting the variable

4. **Verify Vercel URL**:
   - Make sure you're using the exact URL from Vercel dashboard
   - Include `https://` prefix
   - Don't include trailing `/`

5. **Clear browser cache**:
   - Sometimes old CORS errors are cached
   - Try incognito/private window

### CORS_ORIGINS Not Working?

If setting the environment variable doesn't work:

1. **Check main.py** - Make sure it's using `cors_origins` variable (already fixed)
2. **Redeploy manually**:
   - In Railway → Deployments → Click "Redeploy"
3. **Check logs**:
   - Railway → Your Service → Logs
   - Look for any errors during startup

## Quick Fix Command (Railway CLI)

If you have Railway CLI installed:

```bash
railway variables set CORS_ORIGINS="https://your-app.vercel.app,http://localhost:3000"
```

## Testing CORS Locally

To test if CORS is working:

```bash
# Test from command line
curl -H "Origin: https://your-app.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-railway-app.up.railway.app/select-connection

# Should return headers with Access-Control-Allow-Origin
```

## Summary

1. ✅ Get your Vercel URL
2. ✅ Set `CORS_ORIGINS` in Railway with your Vercel URL
3. ✅ Wait for Railway to redeploy
4. ✅ Test your Vercel app - CORS errors should be gone!

---

**The code is already fixed** - you just need to set the environment variable in Railway!

