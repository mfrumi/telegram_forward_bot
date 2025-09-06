#!/bin/bash
# Restart script for Telegram Forward Bot

echo "🔄 Restarting Telegram Forward Bot..."

# Stop the bot
./scripts/stop.sh

# Wait a moment
sleep 2

# Start the bot
./scripts/start.sh
