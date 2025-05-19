import uuid
import datetime
from database.connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

class RequestLog:
    @staticmethod
    def log_request(user_id, api_key, endpoint, symbol, ip_address, user_agent, status_code, response_time):
        """
        Log an API request
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                log_id = str(uuid.uuid4())
                timestamp = datetime.datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO request_logs 
                    (id, user_id, api_key, endpoint, symbol, timestamp, ip_address, user_agent, status_code, response_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    log_id, user_id, api_key, endpoint, symbol, timestamp,
                    ip_address, user_agent, status_code, response_time
                ))
                
                # Update daily usage
                today = datetime.date.today().isoformat()
                daily = cursor.execute('''
                    SELECT id FROM daily_usage 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today)).fetchone()
                
                if daily:
                    cursor.execute('''
                        UPDATE daily_usage 
                        SET request_count = request_count + 1 
                        WHERE id = ?
                    ''', (daily['id'],))
                else:
                    daily_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO daily_usage (id, user_id, date, request_count)
                        VALUES (?, ?, ?, 1)
                    ''', (daily_id, user_id, today))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")
            raise

    @staticmethod
    def get_daily_usage(user_id, date=None):
        """
        Get user's daily usage for a specific date
        """
        try:
            with get_db_connection('users') as conn:
                cursor = conn.cursor()
                if date is None:
                    date = datetime.date.today().isoformat()
                
                usage = cursor.execute('''
                    SELECT request_count 
                    FROM daily_usage 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, date)).fetchone()
                
                return usage['request_count'] if usage else 0
        except Exception as e:
            logger.error(f"Error getting daily usage: {str(e)}")
            raise 