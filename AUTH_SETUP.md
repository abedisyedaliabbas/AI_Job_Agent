# Authentication Setup Guide

## What's Been Added

✅ **Email/Password Authentication**
- Secure password hashing using Werkzeug
- User accounts stored in `data/users.json`
- Auto-signup on first login

✅ **Google OAuth Integration**
- Full Google OAuth 2.0 flow
- User profile extraction (email, name)
- Fallback demo mode if credentials not configured

✅ **Flask-Login Integration**
- Session management
- Protected routes
- Remember me functionality

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google OAuth Setup (Optional but Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API** and **People API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized redirect URIs: `http://localhost:5000/auth/google/callback` (for local)
   - For production: `https://yourdomain.com/auth/google/callback`
7. Copy **Client ID** and **Client Secret**

### 3. Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-random-secret-key-here
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**Generate SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### 4. Test Authentication

1. Start the server: `python run_web.py`
2. Go to `http://localhost:5000`
3. Click "Get Started"
4. Try:
   - **Email/Password**: Enter any email and password (auto-creates account)
   - **Google OAuth**: Click "Continue with Google" (works even without credentials in demo mode)

## How It Works

### Email/Password Flow
1. User enters email + password
2. If new user → creates account with hashed password
3. If existing user → verifies password
4. Logs in with Flask-Login
5. Redirects to dashboard

### Google OAuth Flow
1. User clicks "Continue with Google"
2. Redirects to Google login
3. User authorizes
4. Google redirects back with code
5. Exchange code for user info (email, name)
6. Create or login user
7. Redirects to dashboard

## User Storage

Users are stored in `data/users.json`:
```json
{
  "user@example.com": {
    "user_id": "uuid",
    "email": "user@example.com",
    "password_hash": "hashed_password",
    "auth_provider": "email",
    "created_at": "2024-01-20T10:00:00",
    "name": "User Name",
    "profile_loaded": false
  }
}
```

## Security Notes

- ✅ Passwords are hashed (never stored in plain text)
- ✅ Sessions use secure cookies
- ✅ CSRF protection (Flask-Login)
- ⚠️ For production: Use HTTPS, set strong SECRET_KEY, consider database instead of JSON

## Troubleshooting

**Google OAuth not working?**
- Check `.env` file has correct credentials
- Verify redirect URI matches in Google Console
- Check console for error messages
- Falls back to demo mode if credentials missing

**Can't login?**
- Check `data/users.json` exists and is readable
- Verify password is correct
- Try creating new account with different email
