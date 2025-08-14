#!/bin/bash

# ChartInk Webhook Server Startup Script

echo "Starting ChartInk Webhook Server..."

# Change to the chartink directory
cd /root/chartink

# Activate virtual environment if it exists, otherwise create one
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check if the table exists in Supabase (optional manual step)
echo "Note: Make sure to run the SQL in create_table.sql in your Supabase dashboard first!"

# Start the webhook server
echo "Starting webhook server on port 8082..."
python3 webhook_server.py

# Alternative: Use gunicorn for production
# gunicorn -w 4 -b 0.0.0.0:8082 webhook_server:app
