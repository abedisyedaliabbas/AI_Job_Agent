# Environment Variables for Railway Deployment

Copy these to **Railway → Your Project → Variables** tab:

```
SECRET_KEY=f2b3d949f6b0faacc83a7a2d41d56baa2f1c166c76a16eb01c988b6149d43a4d
GOOGLE_CLIENT_ID=1086565305948-198mgintlu4aksgd21h4r25um90e1lfp.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_MAPS_API_KEY=AIzaSyCzd7IgzkShBRykHxBkpxZe8n2Eb2JSdDo
FLASK_ENV=production
```

## How to Get Each Variable

### 1. SECRET_KEY ✅ (Already Generated)
```
f2b3d949f6b0faacc83a7a2d41d56baa2f1c166c76a16eb01c988b6149d43a4d
```
**Already provided above!** If you need a new one:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET

**See detailed guide:** `HOW_TO_GET_GOOGLE_CREDENTIALS.md`

**Quick steps:**
1. Go to https://console.cloud.google.com/
2. Create/Select a project
3. Enable "Google+ API" or "People API"
4. Go to "APIs & Services" → "Credentials"
5. Create OAuth 2.0 Client ID (Web application)
6. Add redirect URI: `https://your-app.railway.app/auth/google/callback`
7. Copy Client ID and Client Secret

**OR** Skip Google OAuth (optional):
- Leave `GOOGLE_CLIENT_ID` empty
- Leave `GOOGLE_CLIENT_SECRET` empty
- Users can still sign in with email/password

### 3. FLASK_ENV
```
production
```
**Just set to:** `production`

## Notes

- `SECRET_KEY` is **REQUIRED** - Flask uses this for session security
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are **OPTIONAL** - only needed for Google Sign-in
- `FLASK_ENV=production` enables production mode
- `PORT` is automatically set by Railway
