# Railway Deployment Guide

Quick guide to deploy AI Job Agent on Railway.

## Step 1: Prepare Repository

1. Ensure all sensitive files are in `.gitignore`
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Production ready: AI Job Agent"
git push origin main
```

## Step 2: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"

## Step 3: Deploy from GitHub

1. Select "Deploy from GitHub repo"
2. Choose your repository: `AI_Job_Agent`
3. Railway will auto-detect:
   - Python runtime (from `runtime.txt`)
   - Start command (from `Procfile`)
   - Dependencies (from `requirements.txt`)

## Step 4: Configure Environment Variables

In Railway dashboard → Variables tab, add:

```
SECRET_KEY=your_generated_secret_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FLASK_ENV=production
PORT=5000
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 5: Update Google OAuth Redirect URI

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services → Credentials
3. Edit your OAuth 2.0 Client
4. Add Authorized Redirect URI:
   ```
   https://your-app-name.railway.app/auth/google/callback
   ```

## Step 6: Deploy

Railway will automatically:
- Install dependencies
- Build the application
- Start Gunicorn server
- Your app will be live at: `https://your-app-name.railway.app`

## Step 7: Verify Deployment

1. Visit your Railway URL
2. Test authentication (email/password or Google)
3. Upload a resume
4. Test AI agent job search

## Troubleshooting

### Build Fails
- Check `requirements.txt` for all dependencies
- Ensure Python 3.12 is specified in `runtime.txt`

### App Crashes
- Check Railway logs: Dashboard → Deployments → View Logs
- Verify all environment variables are set
- Check `gunicorn_config.py` settings

### OAuth Not Working
- Verify redirect URI matches exactly
- Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Ensure HTTPS is used (Railway provides this automatically)

## Custom Domain (Optional)

1. In Railway → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update Google OAuth redirect URI to match

## Monitoring

- View logs in Railway dashboard
- Check metrics (CPU, Memory, Requests)
- Set up alerts for errors

---

**Your app is now live on Railway! 🚀**
