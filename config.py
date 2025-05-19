import os
from datetime import timedelta

# Database Configuration
DATABASE_ANALYSIS = 'stock_analysis.db'
DATABASE_USERS = 'api_users.db'

# API Configuration
API_HOST = '0.0.0.0'
API_PORT = 5002
DEBUG = False

# Logging Configuration
LOG_FILE = 'api2.log'
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Rate Limiting
RATE_LIMIT_WINDOW = timedelta(days=1)

# Available Plans
PLANS = {
    'free': {'requests_per_day': 10, 'fields': ['short_term', 'medium_term', 'long_term']},
    'basic': {'requests_per_day': 100, 'fields': ['short_term', 'medium_term', 'long_term', 'fund_score']},
    'premium': {'requests_per_day': 1000, 'fields': ['short_term', 'medium_term', 'long_term', 'fund_score', 'price_data']},
    'enterprise': {'requests_per_day': -1, 'fields': 'all'}  # -1 means unlimited
}

# Security
API_KEY_LENGTH = 64
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here')  # Change in production
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) 