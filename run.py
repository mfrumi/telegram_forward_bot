#!/usr/bin/env python3
"""
Telegram Forward Bot - Run Script
Simple script to start the bot with proper error handling.
"""

import os
import sys
import asyncio
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = ['telethon', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print(f"❌ Environment file '{env_file}' not found!")
        print("Please copy '.env.example' to '.env' and configure it with your settings.")
        return False
    
    # Check for required environment variables
    required_vars = [
        'API_ID', 'API_HASH', 'PHONE_NUMBER',
        'SOURCE_GROUP_ID', 'DESTINATION_GROUP_ID',
        'ADMIN_USER_ID'
    ]
    
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print(f"Please configure them in your '{env_file}' file.")
        return False
    
    return True

async def main():
    """Main function to run the bot."""
    print("🤖 Telegram Forward Bot Starting...")
    
    # Setup logging
    setup_logging()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment configuration
    if not check_env_file():
        sys.exit(1)
    
    try:
        # Import and run the bot
        from main import main as bot_main
        await bot_main()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        logging.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Handle Windows event loop policy
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the bot
    asyncio.run(main())

