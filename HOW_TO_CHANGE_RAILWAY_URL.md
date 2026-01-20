# How to Change Railway URL

Your current URL: `web-production-1cb51.up.railway.app` is auto-generated. Here's how to change it:

## Option 1: Generate a New Service (Easiest)

Railway generates new URLs when you create a new service. However, this requires redeploying.

## Option 2: Use Custom Domain (Recommended)

### Step 1: Add Custom Domain in Railway

1. Go to Railway → Your Project → Settings
2. Scroll to "Domains" section
3. Click "Generate Domain" or "Add Domain"
4. Enter a custom name (e.g., `ai-job-agent`)
5. Railway will generate: `ai-job-agent.up.railway.app`

### Step 3: Update Google OAuth Redirect URI

After getting your new domain:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your OAuth 2.0 Client ID
3. Update "Authorized redirect URIs":
   - Remove: `https://web-production-1cb51.up.railway.app/auth/google/callback`
   - Add: `https://your-new-domain.up.railway.app/auth/google/callback`
4. Click "Save"

## Option 3: Use Your Own Domain

If you have your own domain (e.g., `yourdomain.com`):

1. In Railway → Settings → Domains
2. Click "Add Custom Domain"
3. Enter your domain: `yourdomain.com` or `app.yourdomain.com`
4. Railway will provide DNS records to add:
   - CNAME record pointing to Railway
5. Add the DNS records to your domain registrar
6. Wait for DNS propagation (5-60 minutes)
7. Railway will automatically provision SSL certificate

## Quick Steps (Recommended)

1. **Railway Dashboard** → Your Project → **Settings**
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Enter a name like: `ai-job-agent` or `job-agent` or `my-job-app`
5. You'll get: `ai-job-agent.up.railway.app`
6. **Update Google OAuth** with the new URL
7. Done! Your new URL is live immediately

## Note

- Railway URLs are permanent once generated
- You can have multiple domains pointing to the same service
- Custom domains are free on Railway
- SSL certificates are automatically provisioned
