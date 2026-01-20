# Quick Start - Authentication Setup ✅

## ✅ What's Done

1. **Created `.env` file** with:
   - Auto-generated SECRET_KEY
   - Your Google Client ID: `805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u.apps.googleusercontent.com`
   - Placeholder for Client Secret

2. **Installed authentication system**:
   - Email/Password auth (ready to use)
   - Google OAuth (needs Client Secret)

## 🔑 Final Step: Get Google Client Secret

### Option 1: Quick Setup (Recommended)
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth Client ID: `805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u`
3. Click on it → Copy the "Client secret"
4. Open `.env` file → Replace `YOUR_CLIENT_SECRET_HERE` with your secret
5. Save the file

### Option 2: Test Without Google (Email Only)
- You can use email/password authentication immediately
- Google OAuth will work in demo mode (creates test accounts)
- Add Client Secret later for real Google login

## 🚀 Start the Server

```bash
# Install packages (if not done)
pip install -r requirements.txt

# Start server
python run_web.py
```

## 🧪 Test Authentication

1. Go to: http://localhost:5000
2. Click "Get Started"
3. Try:
   - **Email/Password**: Enter any email + password (auto-creates account)
   - **Google OAuth**: Click "Continue with Google" (works even without secret in demo mode)

## 📝 Important Notes

- **SECRET_KEY**: Already generated and saved in `.env`
- **Google Client ID**: Already configured
- **Google Client Secret**: You need to add this from Google Console
- **Redirect URI**: Make sure it's set to `http://localhost:5000/auth/google/callback` in Google Console

## ✅ You're Ready!

The authentication system is fully set up. Just add your Google Client Secret to `.env` and you're good to go!
