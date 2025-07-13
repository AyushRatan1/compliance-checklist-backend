#!/bin/bash

echo "🚀 Starting Compliance Checklist API Server..."

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your AWS credentials."
    exit 1
fi

# Kill any existing servers on port 8000
echo "🔄 Stopping any existing servers..."
pkill -f "uvicorn.*8000" || true
sleep 2

# Start the server using uvicorn directly
echo "🌟 Starting server on http://localhost:8002"
echo "📝 Logs will be shown below. Press Ctrl+C to stop."
echo "----------------------------------------"

# Start with explicit settings that should work
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8002 \
    --log-level info \
    --no-use-colors \
    --reload

echo "✅ Server stopped." 