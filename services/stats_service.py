from models.user import User
from config import PLANS
import logging

logger = logging.getLogger(__name__)

class StatsService:
    @staticmethod
    def get_user_stats(user):
        """
        Get comprehensive user statistics
        """
        try:
            # Get basic usage stats
            usage_stats = User.get_usage_stats(user['id'])
            
            # Add plan information
            plan = PLANS.get(user['plan'], PLANS['free'])
            usage_stats['plan'] = {
                'name': user['plan'],
                'requests_per_day': plan['requests_per_day'],
                'available_fields': plan['fields']
            }
            
            # Add remaining requests
            if plan['requests_per_day'] > 0:
                usage_stats['remaining_today'] = max(0, plan['requests_per_day'] - usage_stats['today'])
            else:
                usage_stats['remaining_today'] = 'unlimited'
            
            return usage_stats
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            raise 