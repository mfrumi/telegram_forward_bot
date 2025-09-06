#!/usr/bin/env python3
"""
Telegram Auto-Forward Bot
A bot that forwards messages from one group to another with link removal and custom modifications.
"""

import os
import re
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageEntityUrl, MessageEntityTextUrl, MessageEntityMention,
    MessageEntityMentionName, KeyboardButtonUrl
)
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonRow

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramForwardBot:
    """Main bot class for handling message forwarding and processing."""
    
    def __init__(self):
        """Initialize the bot with configuration from environment variables."""
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.phone_number = os.getenv('PHONE_NUMBER', '')
        self.session_name = os.getenv('SESSION_NAME', 'telegram_forward_bot')
        
        # Group/Channel IDs
        self.source_group_id = int(os.getenv('SOURCE_GROUP_ID', '0'))
        self.destination_group_id = int(os.getenv('DESTINATION_GROUP_ID', '0'))
        
        # Bot configuration
        self.channel_link = os.getenv('CHANNEL_LINK', 'https://t.me/your_channel')
        self.reference_text = os.getenv('REFERENCE_TEXT', '📢 Forwarded by Bot')
        self.admin_user_id = int(os.getenv('ADMIN_USER_ID', '0'))
        
        # Bot state
        self.is_forwarding = False
        self.message_count = 0
        self.start_time = datetime.now()
        
        # Initialize Telegram client
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        
        logger.info("Bot initialized successfully")
    
    async def start(self):
        """Start the bot and connect to Telegram."""
        try:
            await self.client.start(phone=self.phone_number)
            logger.info("Bot connected to Telegram successfully")
            
            # Verify bot is connected
            me = await self.client.get_me()
            logger.info(f"Bot running as: {me.first_name} (@{me.username})")
            
            # Register event handlers
            self.register_handlers()
            
            logger.info("Bot is ready and listening for messages...")
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    def register_handlers(self):
        """Register event handlers for the bot."""
        
        # Handler for messages from source group
        @self.client.on(events.NewMessage(chats=self.source_group_id))
        async def handle_source_message(event):
            if self.is_forwarding:
                await self.process_and_forward_message(event)
        
        # Handler for admin commands
        @self.client.on(events.NewMessage(from_users=self.admin_user_id))
        async def handle_admin_command(event):
            await self.handle_admin_command(event)
    
    async def process_and_forward_message(self, event):
        """Process and forward message from source to destination group."""
        try:
            original_message = event.message
            
            # Skip if message is empty or from bot itself
            if not original_message.text or original_message.from_id.user_id == (await self.client.get_me()).id:
                return
            
            # Process the message text
            processed_text = self.remove_links(original_message.text)
            processed_text = self.add_reference(processed_text)
            
            # Create inline keyboard with channel button
            keyboard = self.create_channel_button()
            
            # Send processed message to destination group
            await self.client.send_message(
                self.destination_group_id,
                processed_text,
                buttons=keyboard
            )
            
            self.message_count += 1
            logger.info(f"Message forwarded successfully. Total: {self.message_count}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def remove_links(self, text: str) -> str:
        """Remove all types of links from the message text."""
        # Remove HTTP/HTTPS URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        
        # Remove Telegram links (t.me, telegram.me)
        text = re.sub(r'(?:https?://)?(?:t\.me|telegram\.me)/[^\s]+', '', text)
        
        # Remove @username mentions that could be channels/groups
        text = re.sub(r'@[a-zA-Z0-9_]+', '', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def add_reference(self, text: str) -> str:
        """Add custom reference to the message."""
        return f"{text}\n\n{self.reference_text}"
    
    def create_channel_button(self):
        """Create inline keyboard with channel button."""
        return [
            [KeyboardButtonUrl("🔗 Join Our Channel", self.channel_link)]
        ]
    
    async def handle_admin_command(self, event):
        """Handle admin commands."""
        command = event.message.text.lower().strip()
        
        if command == '/start_forwarding':
            self.is_forwarding = True
            await event.reply("✅ Message forwarding started!")
            logger.info("Message forwarding started by admin")
            
        elif command == '/stop_forwarding':
            self.is_forwarding = False
            await event.reply("⏹️ Message forwarding stopped!")
            logger.info("Message forwarding stopped by admin")
            
        elif command == '/status':
            status_message = self.get_status_message()
            await event.reply(status_message)
            
        elif command == '/help':
            help_message = self.get_help_message()
            await event.reply(help_message)
    
    def get_status_message(self) -> str:
        """Get current bot status message."""
        uptime = datetime.now() - self.start_time
        status = "🟢 Active" if self.is_forwarding else "🔴 Inactive"
        
        return f"""
📊 **Bot Status Report**

🔄 Forwarding Status: {status}
📈 Messages Forwarded: {self.message_count}
⏱️ Uptime: {str(uptime).split('.')[0]}
📥 Source Group ID: {self.source_group_id}
📤 Destination Group ID: {self.destination_group_id}
🔗 Channel Link: {self.channel_link}
📝 Reference Text: {self.reference_text}

Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    
    def get_help_message(self) -> str:
        """Get help message with available commands."""
        return """
🤖 **Admin Commands**

/start_forwarding - Start message forwarding
/stop_forwarding - Stop message forwarding  
/status - View bot status and statistics
/help - Show this help message

**Features:**
✅ Auto-forward messages from source to destination group
✅ Remove all links from messages
✅ Add custom reference text
✅ Attach channel button to each message
✅ Admin-only controls
✅ Real-time status monitoring

**Note:** Only authorized admin can use these commands.
        """.strip()

async def main():
    """Main function to run the bot."""
    bot = TelegramForwardBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        await bot.client.disconnect()
        logger.info("Bot disconnected")

if __name__ == "__main__":
    asyncio.run(main())

