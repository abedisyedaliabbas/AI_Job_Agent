"""
Update .env file with Google Client Secret
"""
import os
import re

CLIENT_SECRET = "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"

def update_env_secret():
    """Update .env file with Client Secret"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"[ERROR] {env_file} file not found. Run setup_auth.py first.")
        return
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace the placeholder with actual secret
    updated_content = re.sub(
        r'GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE',
        f'GOOGLE_CLIENT_SECRET={CLIENT_SECRET}',
        content
    )
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print(f"[OK] Updated {env_file} with Google Client Secret")
    print(f"[OK] Client Secret: {CLIENT_SECRET[:10]}...")
    print("\n[SUCCESS] Authentication setup is now 100% complete!")
    print("You can now run: python run_web.py")

if __name__ == "__main__":
    update_env_secret()
