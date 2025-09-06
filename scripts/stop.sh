#!/bin/bash
# Stop script for Telegram Forward Bot

echo "🛑 Stopping Telegram Forward Bot..."

# Find and kill the bot process
PID=$(pgrep -f "python3 run.py")
if [ ! -z "$PID" ]; then
    echo "📍 Found bot process with PID: $PID"
    kill $PID
    echo "✅ Bot stopped successfully"
else
    echo "❌ Bot process not found"
fi
