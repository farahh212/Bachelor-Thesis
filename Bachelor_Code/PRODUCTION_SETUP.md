# Production Setup: Vercel + Railway

## Frontend (Vercel) Configuration

### Environment Variable

In Vercel Dashboard → Your Project → Settings → Environment Variables:

**Add:**
- **Name**: `REACT_APP_API_URL`
- **Value**: `https://your-railway-app.up.railway.app` (your Railway backend URL)
- **Apply to**: Production, Preview, Development

**Example:**
```
REACT_APP_API_URL=https://bachelor-thesis-production-141f.up.railway.app
```

### After Setting Environment Variable

1. **Redeploy** your Vercel app:
   - Go to Deployments
   - Click "Redeploy" on the latest deployment
   - Or push a new commit to trigger auto-deploy

2. **Verify**:
   - Open your Vercel app
   - Check browser console (F12)
   - API calls should go to Railway URL, not localhost

## Backend (Railway) Configuration

### CORS Environment Variable

In Railway Dashboard → Your Service → Variables:

**Add or Edit:**
- **Key**: `CORS_ORIGINS`
- **Value**: `https://bachelorthesis.vercel.app,https://bachelorthesis-git-main.vercel.app,http://localhost:3000`
- (Replace `bachelorthesis` with your actual Vercel app name)

**Note**: The code already includes `https://bachelorthesis.vercel.app` by default, but you can override with the environment variable.

### Railway URL

Your Railway backend URL should be something like:
```
https://your-app-name.up.railway.app
```

## Code Changes Made

### Frontend (`App.js`)
- ✅ Uses `REACT_APP_API_URL` environment variable
- ✅ Falls back to `http://localhost:8000` for local development
- ✅ No hardcoded localhost in production

### Backend (`main.py`)
- ✅ Includes `https://bachelorthesis.vercel.app` in default CORS origins
- ✅ Still reads from `CORS_ORIGINS` environment variable
- ✅ Supports multiple origins (comma-separated)

## Testing

### Local Development
1. **Backend**: `python main.py` (runs on http://localhost:8000)
2. **Frontend**: `npm start` (runs on http://localhost:3000)
3. **CORS**: Works automatically (localhost:3000 is in allowed origins)

### Production
1. **Backend**: Railway (e.g., https://your-app.up.railway.app)
2. **Frontend**: Vercel (e.g., https://bachelorthesis.vercel.app)
3. **CORS**: Configured to allow Vercel domain

## Troubleshooting

### Frontend still calling localhost

**Problem**: `REACT_APP_API_URL` not set in Vercel

**Solution**:
1. ✅ Check Vercel → Settings → Environment Variables
2. ✅ Verify variable name is exactly `REACT_APP_API_URL`
3. ✅ Redeploy after setting variable
4. ✅ Check browser console - should see Railway URL, not localhost

### CORS errors in production

**Problem**: Backend not allowing Vercel domain

**Solution**:
1. ✅ Check Railway → Variables → `CORS_ORIGINS`
2. ✅ Verify Vercel URL is included (exact match, including https://)
3. ✅ Code already includes `https://bachelorthesis.vercel.app` by default
4. ✅ Redeploy Railway after changing environment variables

### API calls failing

**Problem**: Wrong API URL or backend not accessible

**Solution**:
1. ✅ Test Railway backend directly: `https://your-app.up.railway.app/docs`
2. ✅ Check `REACT_APP_API_URL` in Vercel matches Railway URL
3. ✅ Verify Railway service is running (check logs)
4. ✅ Check browser Network tab for actual API calls

## Quick Checklist

- [ ] `REACT_APP_API_URL` set in Vercel with Railway URL
- [ ] Vercel app redeployed after setting environment variable
- [ ] `CORS_ORIGINS` set in Railway (optional - code has defaults)
- [ ] Railway backend is running and accessible
- [ ] Test production: Frontend → Backend communication works
- [ ] Test local: Still works for development

---

**Your code is now production-ready!** Just set the environment variables and redeploy.


