"""
Verify the redirect URI being used by the app
"""
from flask import Flask, request

app = Flask(__name__)

# Simulate what the app does
test_url_root = "http://localhost:5000"
redirect_uri = test_url_root.rstrip('/') + '/auth/google/callback'

print("=" * 60)
print("REDIRECT URI VERIFICATION")
print("=" * 60)
print(f"\nApp is using this redirect URI:")
print(f"  {redirect_uri}")
print(f"\nThis EXACT URI must be in Google Cloud Console:")
print(f"  Authorized redirect URIs section")
print(f"\nMake sure:")
print(f"  [OK] No trailing slash")
print(f"  [OK] Uses 'http' (not 'https')")
print(f"  [OK] Uses 'localhost' (not '127.0.0.1')")
print(f"  [OK] Port is 5000")
print("=" * 60)
