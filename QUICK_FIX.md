# 🔧 QUICK TEMPORARY FIX (5 minutes) - Tell Your Friend!

## ⚡ Method 1: Using ngrok (Works RIGHT NOW)

### Step 1: Download ngrok
- Go to https://ngrok.com/download
- Download for your OS
- Extract it

### Step 2: Start Your Backend
```powershell
cd "d:\Financial Management System"
python main.py
```
Your backend runs on: `http://127.0.0.1:8000`

### Step 3: Expose with ngrok
Open another terminal:
```bash
cd path/to/ngrok
./ngrok http 8000
```

**You'll see:**
```
Session Status            online
Account                   xxxxxxx
Version                   3.x.x
Region                    United States
Forwarding                https://abc123xyz.ngrok.io -> http://localhost:8000
Web Interface             http://127.0.0.1:4040
```

**Copy the URL:** `https://abc123xyz.ngrok.io`

### Step 4: Tell Your Friend to Use This URL

**Send your friend this JavaScript command to run in browser console:**

```javascript
// Paste this in browser console (F12 → Console tab)
window.FMS_API_BASE = "https://abc123xyz.ngrok.io"
```

**Then refresh the page and sign up!**

---

## 🚀 Method 2: Deploy Properly (Permanent Solution)

See `DEPLOYMENT_GUIDE.md` for Render.com deployment (5-10 minutes setup).

---

## 🎯 Summary

**RIGHT NOW:** Use ngrok to get your friend testing  
**LATER:** Deploy to Render for permanent solution

**Your Netlify URL works, backend just needs to be accessible!** ✅
