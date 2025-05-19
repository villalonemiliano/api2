import sqlite3
from flask import g
from contextlib import contextmanager
import logging
from config import DATABASE_ANALYSIS, DATABASE_USERS

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self._connection = None

    def get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

# Create database connection instances
analysis_db = DatabaseConnection(DATABASE_ANALYSIS)
users_db = DatabaseConnection(DATABASE_USERS)

def get_analysis_db():
    """Get or create analysis database connection"""
    if 'analysis_db' not in g:
        g.analysis_db = analysis_db.get_connection()
    return g.analysis_db

def get_users_db():
    """Get or create users database connection"""
    if 'users_db' not in g:
        g.users_db = users_db.get_connection()
    return g.users_db

def close_db(e=None):
    """Close database connections"""
    analysis_db.close()
    users_db.close()

@contextmanager
def get_db_connection(db_type='analysis'):
    """Context manager for database connections"""
    try:
        if db_type == 'analysis':
            conn = get_analysis_db()
        else:
            conn = get_users_db()
        yield conn
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if db_type == 'analysis':
            analysis_db.close()
        else:
            users_db.close()

def init_databases():
    """Initialize database schemas"""
    with get_db_connection('users') as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                plan TEXT DEFAULT 'free',
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        ''')
        
        # Request logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                api_key TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                symbol TEXT,
                timestamp TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                status_code INTEGER,
                response_time REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Daily usage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_usage (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE (user_id, date)
            )
        ''')
        
        conn.commit() 