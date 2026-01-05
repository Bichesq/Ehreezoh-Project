#!/bin/bash

# Activate virtual environment and start FastAPI server with uvicorn

echo "Starting backend server..."

# Navigate to the backend directory
cd backend

# Activate the virtual environment (Windows path - adjust if on Linux/Mac)
source venv/Scripts/activate

# Start the uvicorn server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
