# Backend Deployment Options for Vercel Frontend

Since Vercel is primarily for frontend, you need to deploy the FastAPI backend separately. Here are the best options:

## 🚀 Recommended: Heroku (Easiest)

### Pros
- ✅ Very easy setup
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Good documentation

### Setup

1. **Install Heroku CLI**:
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows: Download from heroku.com
```

2. **Login**:
```bash
heroku login
```

3. **Create app**:
```bash
cd Bachelor_Code
heroku create your-app-name-backend
```

4. **Create `Procfile`** (already exists):
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

5. **Deploy**:
```bash
git init  # if not already a git repo
git add .
git commit -m "Initial commit"
git push heroku main
```

6. **Set CORS**:
```bash
heroku config:set CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

7. **Your backend URL**: `https://your-app-name-backend.herokuapp.com`

---

## 🚂 Alternative: Railway (Modern & Simple)

### Pros
- ✅ Very modern interface
- ✅ $5 free credit/month
- ✅ Auto-deploys from GitHub
- ✅ Easy environment variables

### Setup

1. **Go to [railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. **Select your repository**
5. **Configure**:
   - Root Directory: `Bachelor_Code`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Add Environment Variable**:
   - `CORS_ORIGINS`: `https://your-frontend.vercel.app,http://localhost:3000`
7. **Deploy** - Railway auto-detects Python and installs dependencies

---

## 🎨 Alternative: Render (Free Tier)

### Pros
- ✅ Free tier available
- ✅ Auto-deploy from GitHub
- ✅ Simple setup

### Setup

1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub**
3. **New** → **Web Service**
4. **Connect your repository**
5. **Configure**:
   - Name: `shaft-selector-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Add Environment Variable**:
   - `CORS_ORIGINS`: `https://your-frontend.vercel.app`
7. **Create Web Service**

---

## ☁️ Alternative: AWS/Google Cloud/Azure

### Pros
- ✅ More control
- ✅ Better for production scale
- ✅ More configuration options

### Cons
- ❌ More complex setup
- ❌ Requires cloud knowledge
- ❌ May have costs

**Not recommended for quick deployment** - use one of the options above.

---

## 🔧 Quick Comparison

| Platform | Free Tier | Ease of Setup | Auto-Deploy | Best For |
|----------|-----------|---------------|-------------|----------|
| **Heroku** | ✅ Yes | ⭐⭐⭐⭐⭐ | ✅ Yes | Quick deployment |
| **Railway** | ✅ $5 credit | ⭐⭐⭐⭐⭐ | ✅ Yes | Modern interface |
| **Render** | ✅ Yes | ⭐⭐⭐⭐ | ✅ Yes | Free tier |
| **AWS/GCP** | ⚠️ Limited | ⭐⭐ | ❌ Manual | Production scale |

---

## 📝 After Backend Deployment

1. **Get your backend URL** (e.g., `https://your-app.herokuapp.com`)
2. **Test it**: Visit `https://your-app.herokuapp.com/docs`
3. **Update Vercel environment variable**:
   - `REACT_APP_API_URL` = your backend URL
4. **Update backend CORS** to allow Vercel domain

---

## 🎯 Recommendation

**For quick deployment**: Use **Heroku** - it's the easiest and most reliable.

**For modern experience**: Use **Railway** - great UI and free credit.

Both work perfectly with Vercel frontend!

