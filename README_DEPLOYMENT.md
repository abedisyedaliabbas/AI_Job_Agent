# 🚀 Quick Deployment Guide

## Deploy to Railway (Recommended - 5 minutes)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Go to [Railway.app](https://railway.app)**
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Add Environment Variables:**
   - Click on your project → Variables
   - Add:
     - `SECRET_KEY` = (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
     - `GOOGLE_CLIENT_ID` = (your Google OAuth ID)
     - `GOOGLE_CLIENT_SECRET` = (your Google OAuth secret)

4. **Deploy!**
   - Railway auto-detects Python
   - Uses `Procfile` to run gunicorn
   - Provides HTTPS URL automatically

5. **Update Google OAuth:**
   - Go to Google Cloud Console
   - Add redirect URI: `https://your-app.railway.app/auth/google/callback`

6. **Share with friends:**
   - Send them: `https://your-app.railway.app`

---

## Deploy to Render (Free Tier)

1. **Go to [Render.com](https://render.com)**
   - Sign up with GitHub
   - New → Web Service
   - Connect your repo

2. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

3. **Add Environment Variables:**
   - `SECRET_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

4. **Deploy!**

---

## What Gets Deployed?

✅ **Frontend:** All HTML/CSS/JS templates  
✅ **Backend:** Flask API with all routes  
✅ **Features:** Resume parsing, job search, auto-apply, cover letters  
✅ **Authentication:** Email/Password + Google OAuth  

⚠️ **Note:** Selenium auto-apply won't work on free tiers (no GUI browsers)

---

## Need Help?

See `DEPLOYMENT.md` for detailed instructions!
