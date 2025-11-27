# Deployment Guide

Complete guide to deploying the OCR Platform to production using Render (backend) and Vercel (frontend).

---

## Prerequisites

- ✅ GitHub account
- ✅ Render account (free): https://render.com
- ✅ Vercel account (free): https://vercel.com
- ✅ Code pushed to GitHub repository

---

## 🗂️ Step 1: Push to GitHub

### Initialize Git Repository

```bash
# Navigate to project root
cd ocr-platform

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: OCR Platform v1.0.0"

# Create main branch
git branch -M main
```

### Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ocr-platform` (or your preferred name)
3. Description: "AI-Powered OCR Platform with PaddleOCR & Tesseract"
4. **Keep it Public** (required for free Vercel/Render)
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### Push to GitHub

```bash
# Add remote origin (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/ocr-platform.git

# Push to GitHub
git push -u origin main
```

---

## 🚀 Step 2: Deploy Backend to Render

### Option A: Using render.yaml (Blueprint - Recommended)

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com

2. **Click "New +"**
   - Select "Blueprint"

3. **Connect Repository**
   - Connect your GitHub account
   - Select your `ocr-platform` repository
   - Click "Connect"

4. **Render will automatically detect `render.yaml`**
   - It will create all services:
     - Backend API (Web Service)
     - PostgreSQL Database
     - Redis Cache
     - Celery Worker

5. **Review & Deploy**
   - Review the configuration
   - Click "Apply"
   - Wait 5-10 minutes for deployment

### Option B: Manual Setup

If Blueprint doesn't work, deploy manually:

#### Deploy Backend API

1. **New Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select `ocr-platform` repository

2. **Configure Service**
   - **Name**: `ocr-platform-backend`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: Free

3. **Environment Variables**
   Add these in the "Environment" section:
   
   ```
   ENVIRONMENT=production
   DEBUG=False
   APP_NAME=OCR Platform
   APP_VERSION=1.0.0
   DATABASE_URL=(will auto-populate after creating database)
   REDIS_URL=(will auto-populate after creating redis)
   UPLOAD_DIR=/app/uploads
   MAX_UPLOAD_SIZE=20971520
   ALLOWED_EXTENSIONS=["jpg","jpeg","png","pdf","tiff","bmp"]
   DEFAULT_OCR_ENGINE=paddleocr
   OCR_LANGUAGE=en
   TESSERACT_ENABLED=True
   TESSERACT_CMD=/usr/bin/tesseract
   OCR_CONFIDENCE_THRESHOLD=0.7
   SECRET_KEY=(generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build (5-10 minutes)

#### Create PostgreSQL Database

1. **New PostgreSQL**
   - Click "New +" → "PostgreSQL"
   - **Name**: `ocr-platform-db`
   - **Database**: `ocr_db`
   - **User**: `ocr_user`
   - **Region**: Same as backend
   - **Plan**: Free

2. **Connect to Backend**
   - Copy the "Internal Database URL"
   - Add to backend's `DATABASE_URL` environment variable

3. **Run Migrations**
   - Once backend is deployed, run:
   ```bash
   # Using Render Shell
   # Go to backend service → Shell tab
   alembic upgrade head
   ```

#### Create Redis

1. **New Redis**
   - Click "New +" → "Redis"
   - **Name**: `ocr-platform-redis`
   - **Region**: Same as backend
   - **Plan**: Free
   - **Eviction Policy**: allkeys-lru

2. **Connect to Backend**
   - Copy the "Internal Redis URL"
   - Add to backend's `REDIS_URL` environment variable

#### Create Celery Worker (Optional)

1. **New Background Worker**
   - Click "New +" → "Background Worker"
   - Connect same repository
   - **Name**: `ocr-platform-worker`
   - **Root Directory**: `backend`
   - **Docker Command**: 
     ```
     celery -A app.workers.celery_app worker --loglevel=info --concurrency=2
     ```
   - Add same environment variables as backend
   - **Deploy**

### Verify Backend Deployment

Once deployed, you'll get a URL like: `https://ocr-platform-backend.onrender.com`

Test it:
```bash
curl https://ocr-platform-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production"
}
```

---

## 🎨 Step 3: Deploy Frontend to Vercel

### Deploy from Vercel Dashboard

1. **Go to Vercel**
   - Visit https://vercel.com/new

2. **Import Repository**
   - Click "Import Git Repository"
   - Connect GitHub account
   - Select `ocr-platform` repository
   - Click "Import"

3. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Environment Variables**
   Add this environment variable:
   
   ```
   VITE_API_URL=https://ocr-platform-backend.onrender.com
   ```
   
   *(Replace with your actual Render backend URL)*

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - You'll get a URL like: `https://ocr-platform.vercel.app`

### Update Frontend API URL

After deployment, update the frontend code:

**Edit `frontend/src/App.jsx`:**

```javascript
// Change this line:
const API_URL = 'http://localhost:8000'

// To this (use environment variable):
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

**Commit and push:**
```bash
git add frontend/src/App.jsx
git commit -m "Use environment variable for API URL"
git push
```

Vercel will auto-redeploy with the changes.

---

## 🔧 Step 4: Update Backend CORS

Update backend to allow frontend domain:

**Edit `backend/app/main.py`:**

```python
# Find CORS configuration and update:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ocr-platform.vercel.app",  # Your Vercel URL
        "http://localhost:5173",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and push:**
```bash
git add backend/app/main.py
git commit -m "Update CORS for production frontend"
git push
```

Render will auto-redeploy.

---

## ✅ Step 5: Verify Deployment

### Test Backend
```bash
# Health check
curl https://your-backend.onrender.com/health

# API documentation
open https://your-backend.onrender.com/docs
```

### Test Frontend
1. Open `https://your-frontend.vercel.app`
2. Upload a test image
3. Click "Run Extraction"
4. Verify results appear

---

## 🎯 Production Checklist

- [ ] Backend deployed and healthy
- [ ] Database migrations run
- [ ] Redis connected
- [ ] Frontend deployed
- [ ] API URL configured in frontend
- [ ] CORS updated in backend
- [ ] Test file upload works
- [ ] Test batch upload works
- [ ] Test export functionality
- [ ] Check document history loads

---

## 🚨 Troubleshooting

### Backend Issues

**Problem**: 500 Internal Server Error

**Solutions**:
1. Check Render logs: Dashboard → Service → Logs
2. Verify environment variables are set
3. Check DATABASE_URL is correct
4. Ensure migrations ran: `alembic upgrade head`

**Problem**: Database connection error

**Solution**:
- Use **Internal Database URL** from Render (not external)
- Format: `postgresql://user:pass@hostname/database`

### Frontend Issues

**Problem**: API calls failing (CORS error)

**Solutions**:
1. Check browser console for exact error
2. Verify VITE_API_URL is set in Vercel
3. Update CORS origins in backend
4. Ensure backend URL has no trailing slash

**Problem**: White screen / Build failed

**Solutions**:
1. Check Vercel build logs
2. Verify `frontend` is set as root directory
3. Test build locally: `npm run build`

### Render Free Tier Spin-Down

**Problem**: First request takes 50+ seconds

**Explanation**: Free tier services spin down after 15 minutes of inactivity

**Solutions**:
1. **Upgrade to Starter plan** ($7/month) for always-on
2. **Use UptimeRobot** (free) to ping every 14 minutes:
   - Sign up at https://uptimerobot.com
   - Add monitor: `https://your-backend.onrender.com/health`
   - Check interval: Every 5 minutes
3. **Add loading message** in frontend:
   ```javascript
   if (response.status === 503) {
     setError("Server is waking up, please wait 30 seconds and try again");
   }
   ```

---

## 💰 Cost Breakdown

### Free Tier (Total: $0/month)

| Service | Provider | Limit | Cost |
|---------|----------|-------|------|
| Frontend | Vercel | Unlimited bandwidth | $0 |
| Backend API | Render | Spins down after 15min | $0 |
| PostgreSQL | Render | 90 days free trial | $0 |
| Redis | Render | 90 days free trial | $0 |

**After 90 days**: Database & Redis expire. You'll need to upgrade or migrate.

### Paid Tier (Total: $32/month)

| Service | Provider | Plan | Cost |
|---------|----------|------|------|
| Frontend | Vercel | Hobby (always-on) | $0 |
| Backend API | Render | Starter (always-on) | $7 |
| PostgreSQL | Render | Starter | $7 |
| Redis | Render | Starter | $7 |
| Celery Worker | Render | Starter | $7 |

---

## 🔄 Auto-Deployment

Both Render and Vercel support auto-deployment:

- **Main Branch**: Push to `main` → Auto-deploys to production
- **Other Branches**: Create PR → Auto-creates preview deployment

To deploy:
```bash
git add .
git commit -m "Your changes"
git push
```

Wait 2-3 minutes for automatic deployment.

---

## 📊 Monitoring

### Render
- Dashboard → Service → Metrics
- View CPU, Memory, Request count
- Check logs in real-time

### Vercel
- Dashboard → Project → Analytics
- View page views, load times
- Function invocations

---

## 🔐 Custom Domain (Optional)

### Add Custom Domain to Vercel

1. Vercel Dashboard → Project → Settings → Domains
2. Add your domain: `ocr.yourdomain.com`
3. Configure DNS:
   - Type: CNAME
   - Name: ocr
   - Value: cname.vercel-dns.com

### Add Custom Domain to Render

1. Render Dashboard → Service → Settings → Custom Domain
2. Add: `api.yourdomain.com`
3. Configure DNS:
   - Type: CNAME
   - Name: api
   - Value: [Render provides this]

---

## 📧 Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Issues**: Open an issue on GitHub

---

**Congratulations! Your OCR Platform is now live! 🎉**
