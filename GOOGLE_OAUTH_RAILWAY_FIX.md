# Fix Google OAuth Redirect URI for Railway

## Problem
Error: `redirect_uri_mismatch` when signing in with Google on Railway.

## Solution

You need to add your Railway URL to Google Cloud Console's authorized redirect URIs.

### Step 1: Get Your Railway URL

Your Railway URL is: **`https://aijobagent.up.railway.app`** (or check your Railway dashboard for the exact URL)

The redirect URI will be: **`https://aijobagent.up.railway.app/auth/google/callback`**

### Step 2: Add Redirect URI to Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create one if needed)
3. Navigate to **APIs & Services** → **Credentials**
4. Find your OAuth 2.0 Client ID (or create one if you don't have it)
5. Click **Edit** (pencil icon)
6. Under **Authorized redirect URIs**, click **+ ADD URI**
7. Add these URIs:
   - `https://aijobagent.up.railway.app/auth/google/callback` (Production)
   - `http://localhost:5000/auth/google/callback` (Local development - if you still need it)
8. Click **SAVE**

### Step 3: Verify Railway Environment Variables

Make sure these are set in Railway:
- `GOOGLE_CLIENT_ID` - Your OAuth 2.0 Client ID
- `GOOGLE_CLIENT_SECRET` - Your OAuth 2.0 Client Secret

### Step 4: Test

1. Go to your Railway app: `https://aijobagent.up.railway.app`
2. Click "Sign in with Google"
3. It should work now!

## Important Notes

- The redirect URI must match **exactly** (including `https://` and trailing paths)
- Changes in Google Cloud Console can take a few minutes to propagate
- If your Railway URL changes, you'll need to update the redirect URI in Google Console

## Troubleshooting

If it still doesn't work:
1. Double-check the Railway URL matches exactly
2. Wait 2-3 minutes after saving in Google Console
3. Clear browser cache/cookies
4. Check Railway logs for any errors
