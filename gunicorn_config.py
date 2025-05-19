import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5002')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# Process naming
proc_name = 'stock_analysis_api'

# SSL
keyfile = os.getenv('SSL_KEYFILE')
certfile = os.getenv('SSL_CERTFILE')

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Server hooks
def on_starting(server):
    """
    Server startup hook
    """
    # Create log directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

def post_fork(server, worker):
    """
    Worker fork hook
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """
    Pre-fork hook
    """
    pass

def pre_exec(server):
    """
    Pre-exec hook
    """
    server.log.info("Forked child, re-executing.") 