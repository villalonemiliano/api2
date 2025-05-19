import sqlite3
import os
import logging
from config import ADMIN_API_KEYS, ADMIN_EMAIL_DOMAIN

logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize the database with required tables and admin user
    """
    try:
        # Create database directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        # Read and execute schema
        with open('database/schema.sql', 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
        
        # Create admin user if it doesn't exist
        admin_email = f"admin@{ADMIN_EMAIL_DOMAIN}"
        cursor.execute('SELECT id FROM users WHERE email = ?', (admin_email,))
        if not cursor.fetchone():
            from models.user import User
            admin_user = User.create(
                name="Admin User",
                email=admin_email,
                plan="admin"
            )
            logger.info(f"Created admin user with ID: {admin_user['user_id']}")
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    init_database() 