# Railway Quick Start 🚀

## 1. Push to GitHub ✅
Already done! Your code is on GitHub.

## 2. Deploy on Railway

### Step 1: Create Railway Account
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

### Step 2: New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose: `abedisyedaliabbas/AI_Job_Agent`

### Step 3: Add Environment Variables
In Railway → Your Project → Variables, add:

```
SECRET_KEY=generate_with_python_-c_"import_secrets;_print(secrets.token_hex(32))"
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FLASK_ENV=production
```

### Step 4: Update Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → Credentials
3. Edit OAuth 2.0 Client
4. Add Redirect URI:
   ```
   https://your-app-name.railway.app/auth/google/callback
   ```

### Step 5: Deploy
Railway auto-deploys! Your app will be live at:
```
https://your-app-name.railway.app
```

## Done! 🎉

Your AI Job Agent is now live on Railway!
