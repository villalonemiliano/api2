from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def success_response(data=None, message=None):
    """
    Format successful response
    """
    response = {
        "status": "success"
    }
    
    if data is not None:
        response["data"] = data
    
    if message is not None:
        response["message"] = message
    
    return jsonify(response)

def error_response(message, status_code=400, error_code=None):
    """
    Format error response
    """
    response = {
        "status": "error",
        "message": message
    }
    
    if error_code is not None:
        response["error_code"] = error_code
    
    return jsonify(response), status_code

def not_found_response(message="Resource not found"):
    """
    Format 404 response
    """
    return error_response(message, status_code=404, error_code="NOT_FOUND")

def unauthorized_response(message="Unauthorized"):
    """
    Format 401 response
    """
    return error_response(message, status_code=401, error_code="UNAUTHORIZED")

def forbidden_response(message="Forbidden"):
    """
    Format 403 response
    """
    return error_response(message, status_code=403, error_code="FORBIDDEN")

def rate_limit_response(limit, used):
    """
    Format 429 response
    """
    return error_response(
        "Rate limit exceeded",
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED"
    ), {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Used": str(used),
        "X-RateLimit-Remaining": str(max(0, limit - used))
    } 