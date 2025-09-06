#!/bin/bash
# Start script for Telegram Forward Bot

echo "🤖 Starting Telegram Forward Bot..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install requirements if needed
if [ -f "requirements.txt" ]; then
    echo "📋 Installing/updating requirements..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Start the bot
echo "🚀 Starting bot..."
python3 run.py
