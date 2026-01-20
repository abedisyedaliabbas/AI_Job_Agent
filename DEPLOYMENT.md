# Deployment Guide - AI Job Agent

This guide will help you deploy the AI Job Agent web application so your friends can use it.

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)
**Best for:** Quick deployment, free tier available, easy setup

1. **Sign up at [Railway.app](https://railway.app)**
2. **Create New Project** → "Deploy from GitHub repo"
3. **Connect your GitHub repository**
4. **Configure Environment Variables:**
   - `SECRET_KEY` - Generate a random secret key (use: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `GOOGLE_CLIENT_ID` - Your Google OAuth Client ID (optional)
   - `GOOGLE_CLIENT_SECRET` - Your Google OAuth Client Secret (optional)
   - `PORT` - Railway sets this automatically
5. **Railway will auto-detect Python and deploy!**

**Railway automatically:**
- Detects `Procfile` and runs gunicorn
- Sets up HTTPS
- Provides a public URL
- Handles restarts

---

### Option 2: Render (Free Tier Available)
**Best for:** Free hosting, easy setup, good for testing

1. **Sign up at [Render.com](https://render.com)**
2. **New → Web Service**
3. **Connect GitHub repository**
4. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment:** Python 3
5. **Add Environment Variables:**
   - `SECRET_KEY`
   - `GOOGLE_CLIENT_ID` (optional)
   - `GOOGLE_CLIENT_SECRET` (optional)
6. **Deploy!**

**Render provides:**
- Free tier (spins down after inactivity)
- Automatic HTTPS
- Public URL

---

### Option 3: Heroku (Paid, but reliable)
**Best for:** Production apps, reliable hosting

1. **Install Heroku CLI:** `heroku login`
2. **Create app:** `heroku create your-app-name`
3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set GOOGLE_CLIENT_ID=your-client-id
   heroku config:set GOOGLE_CLIENT_SECRET=your-secret
   ```
4. **Deploy:** `git push heroku main`

---

### Option 4: DigitalOcean App Platform
**Best for:** Production apps, scalable

1. **Sign up at [DigitalOcean](https://www.digitalocean.com)**
2. **Create App → GitHub**
3. **Configure build and run commands**
4. **Add environment variables**
5. **Deploy!**

---

## 📋 Pre-Deployment Checklist

### 1. Environment Variables
Create a `.env.example` file (already in `.gitignore`):
```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_MAPS_API_KEY=your-maps-api-key
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Update Google OAuth Redirect URIs
After deployment, update your Google OAuth settings:
- Add your production URL: `https://your-app.railway.app/auth/google/callback`
- Or: `https://your-app.onrender.com/auth/google/callback`

### 3. Required Directories
The app needs these directories (create if missing):
- `uploads/` - For resume uploads
- `static/cover_letters/` - For generated cover letters
- `data/` - For user data

### 4. Database (Optional)
Currently uses JSON files. For production, consider:
- PostgreSQL (via Railway/Render add-ons)
- SQLite (simple, but not recommended for multiple users)

---

## 🔧 Production Configuration

### Update `app.py` for Production

The app already uses environment variables. Make sure:
- `debug=False` in production (already handled via `os.environ.get('FLASK_ENV')`)
- `SECRET_KEY` is set
- HTTPS is enabled (handled by platform)

### Update `run_web.py` (Optional)

For production, you can create a separate production runner:
```python
# run_production.py
from app import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

---

## 🐳 Docker Deployment (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads static/cover_letters data

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "4"]
```

Then deploy to:
- Railway (supports Docker)
- Render (supports Docker)
- DigitalOcean (supports Docker)
- AWS ECS / Google Cloud Run

---

## 📝 Post-Deployment

### 1. Test the Application
- Visit your deployed URL
- Test resume upload
- Test job search
- Test authentication

### 2. Monitor Logs
- Railway: Dashboard → Logs
- Render: Dashboard → Logs
- Heroku: `heroku logs --tail`

### 3. Share with Friends
Send them:
- Your app URL: `https://your-app.railway.app`
- Brief instructions on how to use it

---

## 🚨 Important Notes

### Selenium/Browser Automation
- **Railway/Render/Heroku don't support GUI browsers**
- Auto-apply feature (Selenium) **won't work** on these platforms
- Consider using headless Chrome with `playwright` or `selenium-wire`
- Or disable auto-apply and only use manual application

### File Storage
- Uploaded files are stored locally (ephemeral on free tiers)
- Consider using:
  - AWS S3
  - Google Cloud Storage
  - Cloudinary (for images)
  - Railway/Render persistent volumes

### Rate Limiting
- Job board scraping may be rate-limited
- Consider adding delays between requests
- Use job board APIs when available

---

## 🆘 Troubleshooting

### "Application Error" on Railway/Render
- Check logs for errors
- Verify environment variables are set
- Ensure `Procfile` is correct

### "Module not found"
- Check `requirements.txt` includes all dependencies
- Rebuild the application

### "Port already in use"
- Platform sets `PORT` automatically
- Don't hardcode port numbers

### Google OAuth not working
- Verify redirect URI matches production URL
- Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set

---

## 📊 Recommended Setup for Friends

**For sharing with friends, I recommend:**

1. **Railway** (easiest, free tier)
   - Quick setup
   - Automatic HTTPS
   - Good free tier
   - Easy to share URL

2. **Render** (free tier, spins down)
   - Free tier available
   - Easy setup
   - Good for testing

3. **DigitalOcean** ($5/month)
   - More reliable
   - Better for production
   - Persistent storage

---

## 🎯 Quick Start Commands

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Test locally with production settings
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
gunicorn app:app --bind 0.0.0.0:5000

# Test with Docker (if using)
docker build -t ai-job-agent .
docker run -p 5000:5000 -e SECRET_KEY=your-key ai-job-agent
```

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)

---

**Ready to deploy? Choose a platform above and follow the steps!** 🚀
