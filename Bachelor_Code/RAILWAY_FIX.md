# Fixing Railway "pip: not found" Error

If you're getting `pip: not found` error on Railway, try these solutions:

## Solution 1: Use Python Module Syntax (Recommended)

The `nixpacks.toml` has been updated to use `python -m pip` instead of just `pip`. This ensures Python's pip module is used correctly.

**Current configuration:**
```toml
[phases.install]
cmds = ["python -m pip install --upgrade pip", "python -m pip install -r requirements.txt"]
```

## Solution 2: Specify Python Version Explicitly

Add `runtime.txt` with Python version (already created):
```
python-3.11.0
```

## Solution 3: Use Railway Settings

In Railway dashboard:
1. Go to your service → **Settings**
2. Under **Build & Deploy**:
   - **Build Command**: `python -m pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

## Solution 4: Alternative nixpacks.toml

If the above doesn't work, try this minimal version:

```toml
providers = ["python"]

[phases.install]
cmds = ["pip3 install -r requirements.txt"]

[start]
cmd = "python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT"
```

## Solution 5: Use Docker Instead

If Nixpacks continues to have issues, you can use the Dockerfile:

1. In Railway → Settings → **Deploy**
2. Change **Builder** from "Nixpacks" to "Dockerfile"
3. Railway will use the `Dockerfile` instead

## Verify the Fix

After updating:
1. **Commit and push** your changes
2. Railway will **auto-redeploy**
3. Check **deployment logs** - should see pip installing packages
4. Verify app starts: Visit `/docs` endpoint

## Common Issues

### Still getting "pip: not found"
- ✅ Check `nixpacks.toml` uses `python -m pip`
- ✅ Verify `requirements.txt` exists
- ✅ Check Railway logs for Python version detection

### Build succeeds but app won't start
- ✅ Verify start command: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- ✅ Check model files exist in `models/` directory
- ✅ Review Railway logs for startup errors

---

The updated `nixpacks.toml` should fix the issue. If not, try Solution 5 (Docker) which is more reliable.

