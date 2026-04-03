# Finance Management System - Deployment Guide

## 🚀 Deploy Backend to Render.com (FREE)

### Step 1: Prepare Backend Files
✅ Already done - Procfile and requirements.txt created

### Step 2: Push to GitHub
```bash
# Initialize git repo
git init
git add .
git commit -m "Finance Management System - Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/financial-management-system.git
git push -u origin main
```

### Step 3: Deploy on Render.com
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Fill in:
   - **Name:** financial-management-system
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
6. Click "Deploy"

### Step 4: Get Backend URL
- After deployment, you'll get a URL like: `https://financial-management-system.onrender.com`
- This is your new API_BASE_URL

### Step 5: Update Frontend API Endpoint
In Netlify Functions or environment variable, set:
```
FMS_API_BASE = "https://financial-management-system.onrender.com"
```

Or update in browser console temporarily:
```javascript
window.FMS_API_BASE = "https://financial-management-system.onrender.com"
```

### Step 6: Restart Netlify Frontend Build
- Push changes to GitHub
- Netlify will auto-redeploy
- Your friend should now be able to sign up! ✅

---

## ⚡ Alternative: Use ngrok (Temporary Quick Fix)

If you want to test quickly without deploying:

```bash
# Install ngrok
# Download from https://ngrok.com

# Start backend
python main.py

# In another terminal, start ngrok
ngrok http 8000
```

You'll get a URL like: `https://abc123xyz.ngrok.io`

Use this URL in your frontend temporarily.

---

## 📝 Environment Variables (Optional)

Create a `.env` file in Render deployment:
```
DATABASE_URL=sqlite:///./fms.db
MODEL_PATH=./risk_model.pkl
```

---

## ✅ Troubleshooting

**Issue: "Failed to fetch"**
- Verify backend URL is correct in api.js
- Check CORS settings in main.py (already updated ✅)
- Verify backend is running

**Issue: 502 Bad Gateway on Render**
- Check that Procfile is correct
- Verify all dependencies in requirements.txt
- Check backend logs in Render dashboard

**Issue: Database not persisting**
- Use PostgreSQL on Render instead of SQLite
- Or use a cloud database service

---

## 🎯 Quick Summary

1. ✅ Backend CORS updated for Netlify
2. 📦 Deployment files created (Procfile, requirements.txt)
3. 🚀 Deploy to Render.com
4. 🔗 Update frontend with new backend URL
5. ✨ Share with your friend!

**Your friend's issue will be SOLVED when backend is deployed!** 🎉
