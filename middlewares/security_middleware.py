from functools import wraps
from flask import request, make_response
import logging
from config import REQUIRE_HTTPS

logger = logging.getLogger(__name__)

def add_security_headers(response):
    """
    Add security headers to response
    """
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

def require_https(f):
    """
    Require HTTPS in production
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if REQUIRE_HTTPS and not request.is_secure:
            logger.warning(f"Non-HTTPS request from {request.remote_addr}")
            return make_response("HTTPS Required", 403)
        return f(*args, **kwargs)
    return decorated_function

def handle_cors(f):
    """
    Handle CORS requests
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
        
        # Handle actual request
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            response, status_code = response
        else:
            status_code = 200
        
        response = make_response(response, status_code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    return decorated_function

def validate_request_size(f):
    """
    Validate request size
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_length and request.content_length > 1024 * 1024:  # 1MB limit
            logger.warning(f"Request too large from {request.remote_addr}")
            return make_response("Request too large", 413)
        return f(*args, **kwargs)
    return decorated_function 