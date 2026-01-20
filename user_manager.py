"""
User Management - Handles user authentication and storage
"""
import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict
from werkzeug.security import generate_password_hash, check_password_hash


class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self, users_file: str = "data/users.json"):
        self.users_file = users_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
    
    def create_user(self, email: str, password: str = None, auth_provider: str = 'email', 
                   google_id: str = None, name: str = None) -> Dict:
        """Create a new user account"""
        email = email.lower().strip()
        user_id = str(uuid.uuid4())
        
        user_data = {
            'user_id': user_id,
            'email': email,
            'auth_provider': auth_provider,
            'created_at': datetime.now().isoformat(),
            'name': name or email.split('@')[0],
            'profile_loaded': False
        }
        
        if password:
            user_data['password_hash'] = generate_password_hash(password)
        
        if google_id:
            user_data['google_id'] = google_id
        
        self.users[email] = user_data
        self._save_users()
        
        return user_data
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        email = email.lower().strip()
        return self.users.get(email)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id"""
        for user in self.users.values():
            if user.get('user_id') == user_id:
                return user
        return None
    
    def verify_password(self, email: str, password: str) -> bool:
        """Verify user password"""
        user = self.get_user_by_email(email)
        if not user or 'password_hash' not in user:
            return False
        return check_password_hash(user['password_hash'], password)
    
    def update_user(self, email: str, **updates):
        """Update user data"""
        email = email.lower().strip()
        if email in self.users:
            self.users[email].update(updates)
            self.users[email]['updated_at'] = datetime.now().isoformat()
            self._save_users()
            return True
        return False
    
    def user_exists(self, email: str) -> bool:
        """Check if user exists"""
        return email.lower().strip() in self.users
