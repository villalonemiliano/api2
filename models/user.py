import uuid
import hashlib
import datetime
from database.connection import get_db_connection
import logging
from config import PLANS, API_KEY_LENGTH

logger = logging.getLogger(__name__)

class User:
    @staticmethod
    def create(name, email, plan='free'):
        """
        Create a new user with API key
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                
                # Generate user ID and API key
                user_id = str(uuid.uuid4())
                api_key = hashlib.sha256(f"{user_id}:{datetime.datetime.now().timestamp()}".encode()).hexdigest()
                
                # Validate plan
                if plan not in PLANS:
                    plan = 'free'
                
                now = datetime.datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO users (id, name, email, api_key, plan, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, name, email, api_key, plan, now, now))
                
                conn.commit()
                
                return {
                    "user_id": user_id,
                    "api_key": api_key,
                    "plan": plan
                }
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    @staticmethod
    def get_by_api_key(api_key):
        """
        Get user by API key
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                user = cursor.execute('SELECT * FROM users WHERE api_key = ?', (api_key,)).fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by API key: {str(e)}")
            raise

    @staticmethod
    def get_by_id(user_id):
        """
        Get user by ID
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise

    @staticmethod
    def get_all_users():
        """
        Get all users (admin only)
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                users = cursor.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
                return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise

    @staticmethod
    def update_last_login(user_id):
        """
        Update user's last login timestamp
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                now = datetime.datetime.now().isoformat()
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (now, user_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            raise

    @staticmethod
    def reset_api_key(user_id):
        """
        Reset user's API key
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                
                # Generate new API key
                new_api_key = hashlib.sha256(
                    f"{user_id}:{datetime.datetime.now().timestamp()}".encode()
                ).hexdigest()
                
                # Update user
                cursor.execute('UPDATE users SET api_key = ? WHERE id = ?', (new_api_key, user_id))
                conn.commit()
                
                return new_api_key
        except Exception as e:
            logger.error(f"Error resetting API key: {str(e)}")
            raise

    @staticmethod
    def update_plan(user_id, new_plan):
        """
        Update user's subscription plan
        """
        try:
            if new_plan not in PLANS:
                raise ValueError(f"Invalid plan: {new_plan}")
            
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET plan = ? WHERE id = ?', (new_plan, user_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating plan: {str(e)}")
            raise

    @staticmethod
    def get_usage_stats(user_id):
        """
        Get user's usage statistics
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                today = datetime.date.today().isoformat()
                
                # Get today's usage
                today_usage = cursor.execute('''
                    SELECT request_count FROM daily_usage 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today)).fetchone()
                
                today_count = today_usage['request_count'] if today_usage else 0
                
                # Get total usage
                total_usage = cursor.execute('''
                    SELECT COUNT(*) as count FROM request_logs 
                    WHERE user_id = ?
                ''', (user_id,)).fetchone()
                
                total_count = total_usage['count'] if total_usage else 0
                
                # Get top symbols
                top_symbols = cursor.execute('''
                    SELECT symbol, COUNT(*) as count 
                    FROM request_logs 
                    WHERE user_id = ? AND symbol != ''
                    GROUP BY symbol 
                    ORDER BY count DESC 
                    LIMIT 5
                ''', (user_id,)).fetchall()
                
                return {
                    "today": today_count,
                    "total": total_count,
                    "top_symbols": [{"symbol": row['symbol'], "count": row['count']} for row in top_symbols]
                }
        except Exception as e:
            logger.error(f"Error getting usage stats: {str(e)}")
            raise 