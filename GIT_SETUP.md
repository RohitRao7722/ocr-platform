# Git Setup & GitHub Push Guide

Quick guide to commit your code and push to GitHub before deploying.

---

## 🗂️ Step 1: Initialize Git

```bash
# Navigate to project root
cd e:\OCR\ocr-project

# Initialize Git repository
git init

# Check status
git status
```

---

## ✅ Step 2: Add All Files

```bash
# Add all files to staging
git add .

# Verify what will be committed
git status
```

You should see all your files listed in green (ready to commit).

---

## 💾 Step 3: Create First Commit

```bash
# Create commit with message
git commit -m "Initial commit: OCR Platform v1.0.0

- Complete backend API with FastAPI
- Frontend with React and Tailwind CSS
- Dual OCR engines (PaddleOCR + Tesseract)
- Batch processing support
- Document history and analytics
- Docker containerization
- Comprehensive documentation"
```

---

## 🌿 Step 4: Create Main Branch

```bash
# Rename branch to main
git branch -M main
```

---

## 📤 Step 5: Create GitHub Repository

### Option A: Using GitHub Website

1. **Go to GitHub**
   - Visit https://github.com/new

2. **Fill in details**:
   - **Repository name**: `ocr-platform` (or your choice)
   - **Description**: "AI-Powered OCR Platform with PaddleOCR & Tesseract"
   - **Visibility**: Public (required for free Vercel/Render deployment)
   - **Don't** initialize with README, .gitignore, or license (we have these)

3. **Click "Create repository"**

### Option B: Using GitHub CLI (Optional)

```bash
# If you have GitHub CLI installed
gh repo create ocr-platform --public --source=. --remote=origin --push
```

---

## 🔗 Step 6: Connect to GitHub

Copy the commands from GitHub's quick setup page, or use these:

```bash
# Add remote origin (REPLACE YOUR-USERNAME!)
git remote add origin https://github.com/YOUR-USERNAME/ocr-platform.git

# Verify remote was added
git remote -v
```

You should see:
```
origin  https://github.com/YOUR-USERNAME/ocr-platform.git (fetch)
origin  https://github.com/YOUR-USERNAME/ocr-platform.git (push)
```

---

## 🚀 Step 7: Push to GitHub

```bash
# Push to GitHub
git push -u origin main
```

Enter your GitHub credentials if prompted.

---

## ✅ Step 8: Verify on GitHub

1. Go to `https://github.com/YOUR-USERNAME/ocr-platform`
2. You should see all your files
3. README.md should display with screenshots

---

## 🎯 Next Steps

After successfully pushing to GitHub:

1. **Deploy Backend to Render**
   - See [DEPLOYMENT.md](docs/DEPLOYMENT.md#-step-2-deploy-backend-to-render)

2. **Deploy Frontend to Vercel**
   - See [DEPLOYMENT.md](docs/DEPLOYMENT.md#-step-3-deploy-frontend-to-vercel)

---

## 🔄 Future Updates

When you make changes:

```bash
# Check what changed
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push
```

Both Render and Vercel will automatically redeploy when you push to the `main` branch.

---

## 🚨 Common Issues

### "fatal: not a git repository"

**Solution**: Run `git init` first

### "Permission denied (publickey)"

**Solutions**:
1. Use HTTPS instead of SSH:
   ```bash
   git remote set-url origin https://github.com/YOUR-USERNAME/ocr-platform.git
   ```
2. Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### "Updates were rejected"

**Solution**: Pull first, then push:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

### Large files error

**Solution**: Check if you accidentally added node_modules or uploads:
```bash
# Remove from git cache
git rm -r --cached frontend/node_modules
git rm -r --cached backend/uploads

# Commit the removal
git commit -m "Remove large files"
git push
```

---

## 📝 Git Workflow

```
┌─────────────────────────────────────────┐
│  1. Make changes to code                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  2. git add .                           │
│     (Stage changes)                     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  3. git commit -m "message"             │
│     (Save changes locally)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  4. git push                            │
│     (Upload to GitHub)                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  5. Render & Vercel auto-deploy         │
│     (Wait 2-3 minutes)                  │
└─────────────────────────────────────────┘
```

---

## ✨ Best Practices

1. **Commit often** - Small, focused commits
2. **Write clear messages** - Describe what and why
3. **Test before committing** - Ensure code works
4. **Don't commit secrets** - Use .env files (already gitignored)
5. **Use .gitignore** - Already configured for you

---

**Ready to deploy? Follow the [DEPLOYMENT.md](docs/DEPLOYMENT.md) guide!**
