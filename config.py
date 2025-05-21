import os
from datetime import timedelta

# Environment
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
TESTING = ENVIRONMENT == 'testing'

# Database Configuration
DATABASE_ANALYSIS = 'test_stock_analysis.db' if TESTING else 'stock_analysis.db'
DATABASE_USERS = 'test_api_users.db' if TESTING else 'api_users.db'

# API Configuration
API_HOST = '0.0.0.0'
API_PORT = 5002
DEBUG = ENVIRONMENT == 'development'

# Security Configuration
REQUIRE_HTTPS = ENVIRONMENT == 'production'
API_KEY_HEADER = 'X-API-Key'  # Header for API key
API_KEY_LENGTH = 64
API_KEY_PATTERN = r'^[a-f0-9]{64}$'  # 64 character hex string

# Admin Configuration
ADMIN_API_KEYS = os.environ.get('ADMIN_API_KEYS', 'test_admin_key').split(',')
ADMIN_EMAIL_DOMAIN = os.environ.get('ADMIN_EMAIL_DOMAIN', 'admin.example.com')

# Rate Limiting
RATE_LIMIT_WINDOW = timedelta(days=1)
RATE_LIMIT_WARNING_THRESHOLD = 0.8  # 80% of limit
RATE_LIMIT_BY_MINUTE = 60 if not TESTING else 1000
RATE_LIMIT_BY_HOUR = 1000 if not TESTING else 10000

# Logging Configuration
LOG_FILE = 'test_api.log' if TESTING else 'api.log'
LOG_LEVEL = 'DEBUG' if TESTING else 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')  # For production error tracking

# Available Plans
PLANS = {
    'free': {
        'requests_per_day': 10 if not TESTING else 1000,
        'fields': ['short_term', 'medium_term', 'long_term'],
        'price': 0,
        'description': 'Basic analysis with short, medium and long term predictions'
    },
    'basic': {
        'requests_per_day': 100 if not TESTING else 1000,
        'fields': ['short_term', 'medium_term', 'long_term', 'fund_score'],
        'price': 9.99,
        'description': 'Includes fundamental analysis score'
    },
    'premium': {
        'requests_per_day': 1000 if not TESTING else 1000,
        'fields': ['short_term', 'medium_term', 'long_term', 'fund_score', 'price_data'],
        'price': 29.99,
        'description': 'Full access to all analysis features'
    },
    'enterprise': {
        'requests_per_day': -1,  # Unlimited
        'fields': 'all',
        'price': 99.99,
        'description': 'Unlimited access with priority support'
    }
}

# Notification Settings
NOTIFICATION_THRESHOLD = 0.8  # 80% of daily limit
SMTP_HOST = os.environ.get('SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
NOTIFICATION_FROM = os.environ.get('NOTIFICATION_FROM', 'noreply@example.com')

# Redis Configuration (for rate limiting in production)
REDIS_URL = os.environ.get('REDIS_URL', '')
USE_REDIS = bool(REDIS_URL) and not TESTING

# Metrics Configuration
ENABLE_METRICS = ENVIRONMENT == 'production'
PROMETHEUS_METRICS_PORT = 9090

# Security
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'test-secret-key' if TESTING else 'your-secret-key-here')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) 