#!/bin/bash

# Exit on any error
set -e

# Create the data directory if it doesn't exist
mkdir -p /app/data

# Run Django migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "Starting server..."
exec "$@"
