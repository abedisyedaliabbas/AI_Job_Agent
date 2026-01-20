# How to Get Google OAuth Credentials

## Step 1: Go to Google Cloud Console

1. Visit: https://console.cloud.google.com/
2. Sign in with your Google account

## Step 2: Create a New Project (or Select Existing)

1. Click the project dropdown at the top
2. Click "New Project"
3. Enter project name: "AI Job Agent" (or any name)
4. Click "Create"
5. Wait for project creation, then select it

## Step 3: Enable Google+ API

1. Go to "APIs & Services" → "Library"
2. Search for "Google+ API" or "People API"
3. Click on it and click "Enable"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen first:
   - User Type: External (unless you have Google Workspace)
   - App name: "AI Job Agent"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Click "Save and Continue" (default is fine)
   - Test users: Add your email, click "Save and Continue"
   - Click "Back to Dashboard"

4. Now create OAuth client ID:
   - Application type: "Web application"
   - Name: "AI Job Agent Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:5000` (for local testing)
     - `https://your-app-name.railway.app` (after Railway deployment)
   - Authorized redirect URIs:
     - `http://localhost:5000/auth/google/callback` (for local)
     - `https://your-app-name.railway.app/auth/google/callback` (for Railway)
   - Click "Create"

## Step 5: Copy Your Credentials

After creation, you'll see:
- **Client ID**: Copy this → `GOOGLE_CLIENT_ID`
  - ✅ Your Client ID: `1086565305948-198mgintlu4aksgd21h4r25um90e1lfp.apps.googleusercontent.com`
- **Client Secret**: Click "Show" and copy → `GOOGLE_CLIENT_SECRET`
  - ⚠️ **You still need to get this!** Go back to Google Cloud Console → Credentials → Your OAuth Client → Click "Show" next to Client Secret

## Step 6: Add to Railway

1. Go to Railway → Your Project → Variables
2. Add:
   ```
   GOOGLE_CLIENT_ID=paste_your_client_id_here
   GOOGLE_CLIENT_SECRET=paste_your_client_secret_here
   ```

## Important Notes

⚠️ **After deploying to Railway:**
1. Go back to Google Cloud Console
2. Edit your OAuth client
3. Add Railway URL to:
   - Authorized JavaScript origins: `https://your-app-name.railway.app`
   - Authorized redirect URIs: `https://your-app-name.railway.app/auth/google/callback`
4. Save changes

## Quick Reference

- **SECRET_KEY**: Already generated: `f2b3d949f6b0faacc83a7a2d41d56baa2f1c166c76a16eb01c988b6149d43a4d`
- **GOOGLE_CLIENT_ID**: Get from Google Cloud Console (Step 5)
- **GOOGLE_CLIENT_SECRET**: Get from Google Cloud Console (Step 5)
- **FLASK_ENV**: Set to `production`

## Alternative: Skip Google OAuth (Optional)

If you don't want Google Sign-in, you can skip these:
- Leave `GOOGLE_CLIENT_ID` empty
- Leave `GOOGLE_CLIENT_SECRET` empty
- Users can still sign in with email/password
