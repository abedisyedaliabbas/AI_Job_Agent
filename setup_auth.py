"""
Setup script for authentication - Run this to configure your .env file
"""
import os
import secrets

GOOGLE_CLIENT_ID = "805485432486-j0gii31sh12ql7ctq35kuqlorpkd3s0u.apps.googleusercontent.com"
GOOGLE_MAPS_API_KEY = "AIzaSyBNkR1BqLZN_n6xNhGUcvtzKlUoByY4zHQ"

def setup_env():
    """Create .env file with configuration"""
    secret_key = secrets.token_hex(32)
    
    env_content = f"""# Flask Secret Key (auto-generated)
SECRET_KEY={secret_key}

# Google OAuth Credentials
GOOGLE_CLIENT_ID={GOOGLE_CLIENT_ID}
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE

# Google Maps API Key (for future location features)
GOOGLE_MAPS_API_KEY={GOOGLE_MAPS_API_KEY}

# Instructions to get Client Secret:
# 1. Go to https://console.cloud.google.com/apis/credentials
# 2. Find your OAuth 2.0 Client ID: {GOOGLE_CLIENT_ID}
# 3. Click on it to view details
# 4. Copy the "Client secret" (looks like: GOCSPX-xxxxxxxxxxxxx)
# 5. Replace YOUR_CLIENT_SECRET_HERE above with your secret
# 6. Make sure authorized redirect URI is set to: http://localhost:5000/auth/google/callback
"""
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        backup_file = ".env.backup"
        if os.path.exists(backup_file):
            os.remove(backup_file)
        print(f"[WARNING] {env_file} already exists. Backing up to .env.backup")
        os.rename(env_file, backup_file)
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"[OK] Created {env_file} file")
    print(f"[OK] Generated SECRET_KEY: {secret_key[:20]}...")
    print(f"[OK] Added Google Client ID: {GOOGLE_CLIENT_ID}")
    print("\n[IMPORTANT] You still need to add your Google Client Secret!")
    print("   1. Go to: https://console.cloud.google.com/apis/credentials")
    print(f"   2. Find Client ID: {GOOGLE_CLIENT_ID}")
    print("   3. Click on it and copy the 'Client secret'")
    print("   4. Edit .env file and replace 'YOUR_CLIENT_SECRET_HERE' with your secret")
    print("   5. Make sure redirect URI is: http://localhost:5000/auth/google/callback")
    print("\n[OK] Setup complete! You can now run: python run_web.py")

if __name__ == "__main__":
    setup_env()
