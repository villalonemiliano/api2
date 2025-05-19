from functools import wraps
from flask import request, jsonify, g
import time
from services.auth_service import AuthService
from models.request_log import RequestLog
import logging

logger = logging.getLogger(__name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('api_key')
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        
        # Validate API key
        user = AuthService.validate_api_key(api_key)
        if not user:
            return jsonify({"error": "Invalid API key"}), 401
        
        # Check rate limit
        within_limit, current_usage = AuthService.check_rate_limit(user)
        if not within_limit:
            return jsonify({
                "error": "Daily request limit exceeded",
                "limit": PLANS[user['plan']]['requests_per_day'],
                "used": current_usage
            }), 429
        
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
            'user_agent': request.user_agent.string
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
            except Exception as e:
                logger.error(f"Error logging request: {str(e)}")
        
        return response
    return decorated_function 