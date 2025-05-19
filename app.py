from flask import Flask, request, g
import logging
from config import API_HOST, API_PORT, DEBUG, LOG_FILE, LOG_LEVEL, LOG_FORMAT
from database.connection import init_databases, close_db
from services.analysis_service import AnalysisService
from services.stats_service import StatsService
from services.auth_service import AuthService
from services.notification_service import NotificationService
from models.user import User
from utils.decorators import require_api_key, log_request
from middlewares.auth_middleware import require_admin
from utils.validators import validate_symbol, validate_email, validate_plan
from utils.response import (
    success_response, error_response, not_found_response,
    unauthorized_response, forbidden_response, rate_limit_response
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Register database teardown
app.teardown_appcontext(close_db)

@app.route('/analysis/<symbol>', methods=['GET'])
@require_api_key
@log_request
def get_stock_analysis(symbol):
    """Get stock analysis for a symbol"""
    try:
        # Validate symbol
        is_valid, result = validate_symbol(symbol)
        if not is_valid:
            return error_response(result)
        
        # Get analysis
        analysis = AnalysisService.get_stock_analysis(result, g.available_fields)
        if not analysis:
            return not_found_response(f"No analysis found for symbol {result}")
        
        return success_response(data=analysis)
    except Exception as e:
        logger.error(f"Error processing analysis request: {str(e)}")
        return error_response("Internal server error", status_code=500)

@app.route('/user/info', methods=['GET'])
@require_api_key
@log_request
def get_user_info():
    """Get user information and usage statistics"""
    try:
        stats = StatsService.get_user_stats(g.user)
        return success_response(data=stats)
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return error_response("Internal server error", status_code=500)

@app.route('/user/reset-api-key', methods=['POST'])
@require_api_key
@log_request
def reset_api_key():
    """Reset user's API key"""
    try:
        # Generate new API key
        new_api_key = User.reset_api_key(g.user['id'])
        
        # Send notification
        NotificationService.send_api_key_reset(g.user, new_api_key)
        
        return success_response(
            data={"api_key": new_api_key},
            message="API key reset successfully"
        )
    except Exception as e:
        logger.error(f"Error resetting API key: {str(e)}")
        return error_response("Internal server error", status_code=500)

@app.route('/admin/create_user', methods=['POST'])
@require_admin
@log_request
def create_user():
    """Create a new user (admin only)"""
    try:
        data = request.json
        if not data:
            return error_response("No data provided")
        
        # Validate required fields
        if not data.get('name'):
            return error_response("Name is required")
        
        # Validate email
        is_valid, result = validate_email(data.get('email'))
        if not is_valid:
            return error_response(result)
        
        # Validate plan
        is_valid, plan = validate_plan(data.get('plan'))
        if not is_valid:
            return error_response(plan)
        
        # Create user
        try:
            user = User.create(
                name=data['name'],
                email=result,
                plan=plan
            )
            return success_response(
                data=user,
                message="User created successfully"
            )
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return error_response("Email already registered")
            raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return error_response("Internal server error", status_code=500)

@app.route('/admin/users', methods=['GET'])
@require_admin
@log_request
def list_users():
    """List all users (admin only)"""
    try:
        users = User.get_all_users()
        return success_response(data=users)
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return error_response("Internal server error", status_code=500)

@app.route('/admin/user/<user_id>', methods=['GET'])
@require_admin
@log_request
def get_user_details(user_id):
    """Get detailed user information (admin only)"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return not_found_response(f"User {user_id} not found")
        
        # Get detailed stats
        stats = StatsService.get_user_stats(user)
        user['stats'] = stats
        
        return success_response(data=user)
    except Exception as e:
        logger.error(f"Error getting user details: {str(e)}")
        return error_response("Internal server error", status_code=500)

if __name__ == '__main__':
    # Initialize databases
    init_databases()
    
    # Start server
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG)