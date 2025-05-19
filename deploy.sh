#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Create required directories
mkdir -p logs data

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/init_db.py

# Set up SSL certificates if provided
if [ -n "$SSL_CERTFILE" ] && [ -n "$SSL_KEYFILE" ]; then
    echo "SSL certificates found, configuring HTTPS..."
else
    echo "Warning: SSL certificates not found, running without HTTPS"
fi

# Start Gunicorn
echo "Starting Gunicorn server..."
gunicorn -c gunicorn_config.py app:app 