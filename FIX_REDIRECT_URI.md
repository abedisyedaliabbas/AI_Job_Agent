# Fix Google OAuth Redirect URI Error

## Error: `redirect_uri_mismatch`

This means the redirect URI in Google Cloud Console doesn't match what the app is sending.

## Quick Fix

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/apis/credentials
2. Find your OAuth Client ID: `805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u`
3. **Click on the Client ID name** (not just view it)

### Step 2: Add Redirect URI
In the OAuth client details page:

1. Scroll to **"Authorized redirect URIs"** section
2. Click **"+ ADD URI"** button
3. Add this EXACT URI (copy-paste):
   ```
   http://localhost:5000/auth/google/callback
   ```
4. **IMPORTANT**: Make sure there's NO trailing slash
5. Click **"SAVE"**

### Step 3: Verify
The redirect URI must match EXACTLY:
- ✅ Correct: `http://localhost:5000/auth/google/callback`
- ❌ Wrong: `http://localhost:5000/auth/google/callback/` (trailing slash)
- ❌ Wrong: `https://localhost:5000/auth/google/callback` (https instead of http)
- ❌ Wrong: `http://127.0.0.1:5000/auth/google/callback` (different host)

### Step 4: Test Again
1. Wait 1-2 minutes for changes to propagate
2. Try Google sign-in again
3. It should work now!

## For Production

When deploying, also add your production URL:
```
https://yourdomain.com/auth/google/callback
```

## Current App Configuration

The app is configured to use:
- **Redirect URI**: `http://localhost:5000/auth/google/callback`
- **Port**: 5000 (default Flask port)

If you're running on a different port, update both:
1. The redirect URI in Google Console
2. The port in `run_web.py` or when starting Flask
