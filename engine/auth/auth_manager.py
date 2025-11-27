import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict
import mysql.connector
import os

class AuthManager:
    """Production Authentication Manager"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'tera_user'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'tera_engine')
        }
        self.admin_email = 'reponsekdz06@gmail.com'
        self.admin_password = '2025'
    
    def _get_connection(self):
        return mysql.connector.connect(**self.db_config)
    
    def register_user(self, email: str, password: str, full_name: str) -> Dict:
        """Register new user"""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return {'success': False, 'error': 'Email already registered'}
            
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, full_name, role, subscription_tier)
                VALUES (%s, %s, %s, %s, 'user', 'free')
            """, (user_id, email, password_hash, full_name))
            
            cursor.execute("""
                INSERT INTO usage_limits (id, user_id, subscription_tier, generations_limit, downloads_limit, storage_limit_gb, api_calls_limit)
                VALUES (%s, %s, 'free', 10, 0, 1, 100)
            """, (str(uuid.uuid4()), user_id))
            
            conn.commit()
            token = self._generate_token(user_id, email, 'user', 'free')
            
            return {'success': True, 'user_id': user_id, 'email': email, 'token': token, 'subscription_tier': 'free'}
        finally:
            cursor.close()
            conn.close()
    
    def login(self, email: str, password: str) -> Dict:
        """Login user"""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            if email == self.admin_email and password == self.admin_password:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                if not user:
                    user_id = str(uuid.uuid4())
                    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                    cursor.execute("""
                        INSERT INTO users (id, email, password_hash, full_name, role, subscription_tier, subscription_status)
                        VALUES (%s, %s, %s, 'Admin User', 'admin', 'pro', 'active')
                    """, (user_id, email, password_hash))
                    conn.commit()
                    user = {'id': user_id, 'email': email, 'role': 'admin', 'subscription_tier': 'pro'}
                
                token = self._generate_token(user['id'], email, 'admin', 'pro')
                return {'success': True, 'user_id': user['id'], 'email': email, 'role': 'admin', 'subscription_tier': 'pro', 'token': token}
            
            cursor.execute("SELECT * FROM users WHERE email = %s AND is_active = TRUE", (email,))
            user = cursor.fetchone()
            
            if not user or not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                return {'success': False, 'error': 'Invalid credentials'}
            
            cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
            conn.commit()
            
            token = self._generate_token(user['id'], user['email'], user['role'], user['subscription_tier'])
            return {'success': True, 'user_id': user['id'], 'email': user['email'], 'role': user['role'], 'subscription_tier': user['subscription_tier'], 'token': token}
        finally:
            cursor.close()
            conn.close()
    
    def _generate_token(self, user_id: str, email: str, role: str, subscription_tier: str) -> str:
        payload = {'user_id': user_id, 'email': email, 'role': role, 'subscription_tier': subscription_tier, 'exp': datetime.utcnow() + timedelta(days=30)}
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except:
            return None
    
    def check_limits(self, user_id: str, action: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM usage_limits WHERE user_id = %s", (user_id,))
            limits = cursor.fetchone()
            if not limits:
                return {'allowed': False, 'error': 'No limits found'}
            
            if action == 'generation':
                if limits['generations_limit'] == -1:
                    return {'allowed': True, 'unlimited': True}
                if limits['generations_used'] >= limits['generations_limit']:
                    return {'allowed': False, 'error': 'Generation limit reached'}
            elif action == 'download':
                if limits['downloads_limit'] == -1:
                    return {'allowed': True, 'unlimited': True}
                if limits['downloads_used'] >= limits['downloads_limit']:
                    return {'allowed': False, 'error': 'Download limit reached'}
            
            return {'allowed': True, 'remaining': limits[f'{action}s_limit'] - limits[f'{action}s_used']}
        finally:
            cursor.close()
            conn.close()
    
    def increment_usage(self, user_id: str, action: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f"UPDATE usage_limits SET {action}s_used = {action}s_used + 1 WHERE user_id = %s", (user_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
