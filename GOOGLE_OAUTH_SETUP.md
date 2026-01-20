# Google OAuth Setup - Quick Guide

## Your Client ID
```
805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u.apps.googleusercontent.com
```

## Steps to Get Client Secret

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Make sure you're in the correct project

2. **Find Your OAuth Client**
   - Look for Client ID: `805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u`
   - Click on it to view details

3. **Get Client Secret**
   - In the details page, you'll see "Client secret"
   - Click "Show" or copy the secret
   - It looks like: `GOCSPX-xxxxxxxxxxxxxxxxxxxxx`

4. **Update .env File**
   - Open `.env` file in the project root
   - Replace `YOUR_CLIENT_SECRET_HERE` with your actual secret
   - Save the file

5. **Verify Redirect URI**
   - In the same OAuth client details page
   - Under "Authorized redirect URIs"
   - Make sure this is added: `http://localhost:5000/auth/google/callback`
   - For production, also add: `https://yourdomain.com/auth/google/callback`

## Test It

1. Start the server: `python run_web.py`
2. Go to: http://localhost:5000
3. Click "Get Started"
4. Click "Continue with Google"
5. You should be redirected to Google login

## Troubleshooting

**"redirect_uri_mismatch" error?**
- Check that redirect URI in Google Console matches exactly: `http://localhost:5000/auth/google/callback`
- Make sure there's no trailing slash

**"invalid_client" error?**
- Verify Client ID and Secret are correct in `.env`
- Make sure there are no extra spaces

**Can't find Client Secret?**
- Some OAuth clients don't show secrets after creation
- You may need to create a new OAuth 2.0 Client ID
- Make sure to copy the secret immediately (it's only shown once)
