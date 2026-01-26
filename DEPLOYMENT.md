# Deployment Guide

This guide provides instructions for deploying the Shaft–Hub Connection Selector application to various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Full-Stack Deployment](#full-stack-deployment)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.8+ installed
- Node.js 14+ and npm installed
- Trained ML model files in `Bachelor_Code/models/`
- Git repository access

## Backend Deployment

### Option 1: Heroku

1. **Install Heroku CLI** and login:
```bash
heroku login
```

2. **Create a new Heroku app**:
```bash
cd Bachelor_Code
heroku create your-app-name
```

3. **Create `Procfile`** in `Bachelor_Code/`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

4. **Create `runtime.txt`** (optional, specify Python version):
```
python-3.11.0
```

5. **Deploy**:
```bash
git add .
git commit -m "Deploy backend"
git push heroku main
```

6. **Verify deployment**:
```bash
heroku open
```

### Option 2: AWS EC2

1. **Launch an EC2 instance** (Ubuntu 22.04 recommended)

2. **SSH into the instance**:
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

4. **Clone and setup**:
```bash
git clone your-repo-url
cd Bachelor_Code
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Create systemd service** (`/etc/systemd/system/shaft-selector.service`):
```ini
[Unit]
Description=Shaft Connection Selector API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Bachelor_Code
Environment="PATH=/home/ubuntu/Bachelor_Code/venv/bin"
ExecStart=/home/ubuntu/Bachelor_Code/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

6. **Start service**:
```bash
sudo systemctl start shaft-selector
sudo systemctl enable shaft-selector
```

7. **Configure Nginx** (`/etc/nginx/sites-available/shaft-selector`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. **Enable and restart Nginx**:
```bash
sudo ln -s /etc/nginx/sites-available/shaft-selector /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Docker

1. **Create `Dockerfile`** in `Bachelor_Code/`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Create `.dockerignore`**:
```
__pycache__
*.pyc
venv/
.env
*.log
```

3. **Build and run**:
```bash
docker build -t shaft-selector-backend .
docker run -p 8000:8000 shaft-selector-backend
```

4. **Deploy to Docker Hub or container registry**:
```bash
docker tag shaft-selector-backend your-username/shaft-selector-backend
docker push your-username/shaft-selector-backend
```

## Frontend Deployment

### Option 1: Vercel

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
cd Bachelor_Code/shaft-connection-selector
vercel
```

3. **Update API URL**: Create `.env.production`:
```
REACT_APP_API_URL=https://your-backend-url.com
```

4. **Redeploy**:
```bash
vercel --prod
```

### Option 2: Netlify

1. **Build the app**:
```bash
cd Bachelor_Code/shaft-connection-selector
npm run build
```

2. **Drag and drop** the `build` folder to [Netlify Drop](https://app.netlify.com/drop)

3. **Or use Netlify CLI**:
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=build
```

4. **Set environment variable** in Netlify dashboard:
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-backend-url.com`

### Option 3: AWS S3 + CloudFront

1. **Build the app**:
```bash
cd Bachelor_Code/shaft-connection-selector
npm run build
```

2. **Upload to S3**:
```bash
aws s3 sync build/ s3://your-bucket-name --delete
```

3. **Configure CloudFront** to serve from S3 bucket

4. **Set environment variable** in build process or use CloudFront headers

### Option 4: GitHub Pages

1. **Install gh-pages**:
```bash
cd Bachelor_Code/shaft-connection-selector
npm install --save-dev gh-pages
```

2. **Update `package.json`**:
```json
{
  "homepage": "https://your-username.github.io/your-repo-name",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

3. **Deploy**:
```bash
npm run deploy
```

## Full-Stack Deployment

### Using Docker Compose

1. **Create `docker-compose.yml`** in root:
```yaml
version: '3.8'

services:
  backend:
    build: ./Bachelor_Code
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
    volumes:
      - ./Bachelor_Code/models:/app/models

  frontend:
    build: ./Bachelor_Code/shaft-connection-selector
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://backend:8000
    depends_on:
      - backend
```

2. **Create frontend `Dockerfile`** in `Bachelor_Code/shaft-connection-selector/`:
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

3. **Deploy**:
```bash
docker-compose up -d
```

## Environment Configuration

### Backend Environment Variables

Create `.env` file in `Bachelor_Code/`:
```env
# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

# API settings
API_HOST=0.0.0.0
API_PORT=8000

# Model path
MODEL_PATH=./models/connection_classifier.pkl
META_PATH=./models/connection_classifier_meta.pkl
```

Update `main.py` to read from environment:
```python
import os
from dotenv import load_dotenv

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    ...
)
```

### Frontend Environment Variables

Create `.env.production` in `Bachelor_Code/shaft-connection-selector/`:
```env
REACT_APP_API_URL=https://your-backend-api.com
```

Update `App.js`:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

## Troubleshooting

### Backend Issues

**Issue**: Model files not found
- **Solution**: Ensure `models/connection_classifier.pkl` and `models/connection_classifier_meta.pkl` are in the deployment directory

**Issue**: CORS errors
- **Solution**: Update `allow_origins` in `main.py` to include your frontend domain

**Issue**: Port already in use
- **Solution**: Change port in deployment configuration or kill process using the port

### Frontend Issues

**Issue**: API calls failing
- **Solution**: Check `REACT_APP_API_URL` environment variable is set correctly

**Issue**: Build fails
- **Solution**: Ensure all dependencies are installed and Node.js version is compatible

**Issue**: Blank page after deployment
- **Solution**: Check browser console for errors, verify API URL is correct

### General Issues

**Issue**: Slow response times
- **Solution**: Consider using a CDN for frontend, optimize model loading (lazy loading is already implemented)

**Issue**: Memory issues
- **Solution**: Increase server memory allocation, consider using model quantization

## Security Considerations

1. **API Rate Limiting**: Implement rate limiting to prevent abuse
2. **Input Validation**: Already implemented in FastAPI models
3. **HTTPS**: Always use HTTPS in production
4. **Environment Variables**: Never commit `.env` files
5. **CORS**: Restrict CORS origins to known domains only

## Monitoring and Logging

### Backend Logging

Add logging configuration:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Check Endpoint

Add to `main.py`:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

## Performance Optimization

1. **Model Caching**: Already implemented with lazy loading
2. **Response Caching**: Consider adding Redis for frequently requested configurations
3. **CDN**: Use CDN for frontend static assets
4. **Database**: Consider adding a database for logging/analytics if needed

---

For additional support, please open an issue on GitHub.


