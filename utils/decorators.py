from functools import wraps
from flask import request, jsonify, g
import time
import re
from services.auth_service import AuthService
from models.request_log import RequestLog
from utils.response import unauthorized_response, rate_limit_response
from config import API_KEY_HEADER, API_KEY_PATTERN, RATE_LIMIT_WARNING_THRESHOLD
import logging

logger = logging.getLogger(__name__)

def validate_api_key_format(api_key):
    """Validate API key format"""
    if not api_key:
        return False, "API key is required"
    
    if not re.match(API_KEY_PATTERN, api_key):
        return False, "Invalid API key format"
    
    return True, api_key

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get(API_KEY_HEADER)
        
        # Validate API key format
        is_valid, result = validate_api_key_format(api_key)
        if not is_valid:
            logger.warning(f"Invalid API key format from IP: {request.remote_addr}")
            return unauthorized_response(result)
        
        # Validate API key and get user
        user = AuthService.validate_api_key(result)
        if not user:
            logger.warning(f"Invalid API key from IP: {request.remote_addr}")
            return unauthorized_response("Invalid API key")
        
        # Check rate limit
        within_limit, current_usage = AuthService.check_rate_limit(user)
        if not within_limit:
            logger.warning(f"Rate limit exceeded for user {user['id']}")
            return rate_limit_response(
                PLANS[user['plan']]['requests_per_day'],
                current_usage
            )
        
        # Check if approaching rate limit
        if PLANS[user['plan']]['requests_per_day'] > 0:
            usage_ratio = current_usage / PLANS[user['plan']]['requests_per_day']
            if usage_ratio >= RATE_LIMIT_WARNING_THRESHOLD:
                logger.warning(
                    f"User {user['id']} approaching rate limit: "
                    f"{current_usage}/{PLANS[user['plan']]['requests_per_day']}"
                )
        
        # Store user in request context
        g.user = user
        g.available_fields = AuthService.get_available_fields(user)
        
        return f(*args, **kwargs)
    return decorated_function

def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Get request info
        request_info = {
            'endpoint': request.path,
            'symbol': kwargs.get('symbol', '').upper(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string,
            'method': request.method,
            'query_params': dict(request.args)
        }
        
        # Execute view
        response = f(*args, **kwargs)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log request if user is authenticated
        if hasattr(g, 'user'):
            try:
                RequestLog.log_request(
                    user_id=g.user['id'],
                    api_key=g.user['api_key'],
                    endpoint=request_info['endpoint'],
                    symbol=request_info['symbol'],
                    ip_address=request_info['ip_address'],
                    user_agent=request_info['user_agent'],
                    status_code=response[1] if isinstance(response, tuple) else 200,
                    response_time=response_time
                )
                
                # Log warning if response time is high
                if response_time > 1.0:  # More than 1 second
                    logger.warning(
                        f"Slow response time ({response_time:.2f}s) for "
                        f"endpoint {request_info['endpoint']} from user {g.user['id']}"
                    )
            except Exception as e:
                logger.error(f"Error logging request: {str(e)}")
        
        return response
    return decorated_function 