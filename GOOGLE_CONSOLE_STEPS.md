# Step-by-Step: Add Redirect URI in Google Cloud Console

## The Exact URI You Need to Add

```
http://localhost:5000/auth/google/callback
```

## Detailed Steps

### Step 1: Open Google Cloud Console
1. Go to: https://console.cloud.google.com/apis/credentials
2. Make sure you're in the correct project (the one with your OAuth Client ID)

### Step 2: Find Your OAuth Client
1. Look for your OAuth 2.0 Client ID
2. The Client ID should be: `805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u`
3. **Click on the Client ID NAME** (the blue link, not just the ID number)

### Step 3: Add Redirect URI
1. Scroll down to **"Authorized redirect URIs"** section
2. Click the **"+ ADD URI"** button
3. In the text field, paste EXACTLY:
   ```
   http://localhost:5000/auth/google/callback
   ```
4. **CRITICAL**: Make sure:
   - No trailing slash at the end
   - Uses `http` (not `https`)
   - Uses `localhost` (not `127.0.0.1`)
   - Port is `5000`
5. Click **"SAVE"** button at the bottom

### Step 4: Wait and Test
1. Wait 1-2 minutes for changes to propagate
2. Restart your Flask server (if running)
3. Try Google sign-in again

## Common Mistakes to Avoid

❌ **WRONG**: `http://localhost:5000/auth/google/callback/` (trailing slash)
❌ **WRONG**: `https://localhost:5000/auth/google/callback` (https instead of http)
❌ **WRONG**: `http://127.0.0.1:5000/auth/google/callback` (127.0.0.1 instead of localhost)
❌ **WRONG**: `http://localhost:8000/auth/google/callback` (wrong port)

✅ **CORRECT**: `http://localhost:5000/auth/google/callback`

## Visual Guide

After clicking your OAuth Client ID, you should see:

```
OAuth client
┌─────────────────────────────────────────┐
│ Name: [Your Client Name]                │
│ Client ID: 805485432486-...             │
│ Client secret: [Hidden]                 │
│                                         │
│ Authorized JavaScript origins           │
│   http://localhost:5000                 │
│                                         │
│ Authorized redirect URIs                │
│   [Empty or missing]                    │
│   + ADD URI                             │
└─────────────────────────────────────────┘
```

Click **"+ ADD URI"** and add: `http://localhost:5000/auth/google/callback`

## Still Not Working?

1. **Double-check the URI**: Copy-paste from this document
2. **Check for typos**: Extra spaces, wrong characters
3. **Wait longer**: Sometimes takes 2-3 minutes to propagate
4. **Clear browser cache**: Try incognito/private window
5. **Check the port**: Make sure Flask is running on port 5000
