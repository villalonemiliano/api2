import re
import logging

logger = logging.getLogger(__name__)

def validate_symbol(symbol):
    """
    Validate stock symbol format
    """
    if not symbol:
        return False, "Symbol is required"
    
    # Basic symbol validation (letters, numbers, dots, hyphens)
    if not re.match(r'^[A-Za-z0-9.-]+$', symbol):
        return False, "Invalid symbol format"
    
    return True, symbol.upper()

def validate_email(email):
    """
    Validate email format
    """
    if not email:
        return False, "Email is required"
    
    # Basic email validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False, "Invalid email format"
    
    return True, email.lower()

def validate_plan(plan):
    """
    Validate subscription plan
    """
    valid_plans = ['free', 'basic', 'premium', 'enterprise']
    if not plan:
        return True, 'free'  # Default to free plan
    
    if plan.lower() not in valid_plans:
        return False, f"Invalid plan. Must be one of: {', '.join(valid_plans)}"
    
    return True, plan.lower() 