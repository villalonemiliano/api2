from functools import wraps
from flask import request, g
from utils.response import unauthorized_response, forbidden_response
import logging
from config import ADMIN_API_KEYS

logger = logging.getLogger(__name__)

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return unauthorized_response("Missing or invalid Authorization header")
        
        api_key = auth_header.split(' ')[1]
        
        # Check if API key is in admin list
        if api_key not in ADMIN_API_KEYS:
            logger.warning(f"Unauthorized admin access attempt from IP: {request.remote_addr}")
            return forbidden_response("Admin access required")
        
        # Store admin info in request context
        g.is_admin = True
        g.admin_api_key = api_key
        
        return f(*args, **kwargs)
    return decorated_function 