from models.user import User
from models.request_log import RequestLog
from config import PLANS
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def validate_api_key(api_key):
        """
        Validate API key and return user if valid
        """
        try:
            user = User.get_by_api_key(api_key)
            if not user:
                return None
            
            # Update last login
            User.update_last_login(user['id'])
            
            return user
        except Exception as e:
            logger.error(f"Error validating API key: {str(e)}")
            raise

    @staticmethod
    def check_rate_limit(user):
        """
        Check if user has exceeded their rate limit
        """
        try:
            if user['plan'] not in PLANS:
                return True, 0  # No limit for unknown plans
            
            plan = PLANS[user['plan']]
            if plan['requests_per_day'] < 0:
                return True, 0  # Unlimited requests
            
            daily_usage = RequestLog.get_daily_usage(user['id'])
            return daily_usage < plan['requests_per_day'], daily_usage
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            raise

    @staticmethod
    def get_available_fields(user):
        """
        Get available fields for user's plan
        """
        try:
            if user['plan'] not in PLANS:
                return PLANS['free']['fields']
            return PLANS[user['plan']]['fields']
        except Exception as e:
            logger.error(f"Error getting available fields: {str(e)}")
            raise 