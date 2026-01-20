# How to Get Your Google OAuth Client Secret

## Your Credentials
- **Client ID**: `805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u.apps.googleusercontent.com`
- **Maps API Key**: `AIzaSyBNkR1BqLZN_n6xNhGUcvtzKlUoByY4zHQ` ✅ (Already added)

## Step-by-Step to Get Client Secret

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/apis/credentials

### 2. Find Your OAuth Client
- Look for the Client ID: `805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u`
- It should be listed under "OAuth 2.0 Client IDs"
- Click on the Client ID name (not the ID itself)

### 3. View Client Secret
- In the details page, you'll see a section called "Client secret"
- It will show: `GOCSPX-xxxxxxxxxxxxxxxxxxxxx` (or similar)
- Click the "Show" button or copy icon to reveal it
- **IMPORTANT**: Copy it immediately - it's only shown once!

### 4. Update .env File
1. Open the `.env` file in your project root
2. Find the line: `GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE`
3. Replace `YOUR_CLIENT_SECRET_HERE` with your actual secret
4. Save the file

### 5. Verify Redirect URI
In the same OAuth client details page:
- Scroll to "Authorized redirect URIs"
- Make sure this is listed: `http://localhost:5000/auth/google/callback`
- If not, click "Add URI" and add it
- For production, also add: `https://yourdomain.com/auth/google/callback`

## Example .env File (After Adding Secret)

```env
SECRET_KEY=your-generated-secret-key
GOOGLE_CLIENT_ID=805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-secret-here
GOOGLE_MAPS_API_KEY=AIzaSyBNkR1BqLZN_n6xNhGUcvtzKlUoByY4zHQ
```

## Troubleshooting

**Can't find Client Secret?**
- Some OAuth clients don't show secrets after initial creation
- You may need to create a new OAuth 2.0 Client ID
- Or reset the existing one (this will generate a new secret)

**Secret looks different?**
- Client secrets can have different formats
- Common formats: `GOCSPX-...`, `GOCSPX-...`, or just a long string
- All formats work, just copy exactly as shown

**Still having issues?**
- Check that you're in the correct Google Cloud project
- Verify the Client ID matches exactly
- Make sure OAuth consent screen is configured
