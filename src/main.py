#!/usr/bin/env python3
"""
Telegram Auto-Forward Bot - Main Application
Enhanced version with comprehensive admin controls and monitoring.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Optional

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telethon import TelegramClient, events
from telethon.tl.types import KeyboardButtonUrl

from config import get_config
from message_processor import MessageProcessor
from admin import AdminManager

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
    """Enhanced Telegram bot for message forwarding with admin controls."""
    
    def __init__(self):
        """Initialize the bot with all components."""
        try:
            # Load configuration
            self.config = get_config()
            
            # Initialize components
            self.message_processor = MessageProcessor(self.config.reference_text)
            self.admin_manager = AdminManager(self.config.admin_user_id, self)
            
            # Bot state
            self.is_forwarding = False
            self.client: Optional[TelegramClient] = None
            
            # Initialize Telegram client
            self.client = TelegramClient(
                self.config.session_name,
                self.config.api_id,
                self.config.api_hash
            )
            
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def start(self):
        """Start the bot and connect to Telegram."""
        try:
            # Connect to Telegram
            await self.client.start(phone=self.config.phone_number)
            logger.info("Bot connected to Telegram successfully")
            
            # Verify connection
            me = await self.client.get_me()
            logger.info(f"Bot running as: {me.first_name} (@{me.username})")
            
            # Verify group access
            await self.verify_group_access()
            
            # Register event handlers
            self.register_handlers()
            
            # Send startup notification to admin
            await self.send_startup_notification()
            
            logger.info("Bot is ready and listening for messages...")
            
            # Keep the bot running
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            self.admin_manager.log_error("Startup error", str(e))
            raise
    
    async def verify_group_access(self):
        """Verify bot has access to required groups."""
        try:
            # Check source group
            source_entity = await self.client.get_entity(self.config.source_group_id)
            logger.info(f"Source group verified: {source_entity.title}")
            
            # Check destination group
            dest_entity = await self.client.get_entity(self.config.destination_group_id)
            logger.info(f"Destination group verified: {dest_entity.title}")
            
        except Exception as e:
            logger.error(f"Group access verification failed: {e}")
            raise
    
    def register_handlers(self):
        """Register all event handlers."""
        
        # Handler for messages from source group
        @self.client.on(events.NewMessage(chats=self.config.source_group_id))
        async def handle_source_message(event):
            if self.is_forwarding:
                await self.process_and_forward_message(event)
        
        # Handler for admin commands (from admin user)
        @self.client.on(events.NewMessage(from_users=self.config.admin_user_id))
        async def handle_admin_command(event):
            await self.admin_manager.handle_admin_command(event)
        
        # Handler for bot mentions (optional - for public commands)
        @self.client.on(events.NewMessage(pattern=r'/\w+'))
        async def handle_public_command(event):
            # Only respond to admin in private chat
            if event.is_private and event.sender_id == self.config.admin_user_id:
                await self.admin_manager.handle_admin_command(event)
        
        logger.info("Event handlers registered successfully")
    
    async def process_and_forward_message(self, event):
        """Process and forward message from source to destination group."""
        try:
            original_message = event.message
            
            # Skip messages from self
            me = await self.client.get_me()
            if original_message.from_id and original_message.from_id.user_id == me.id:
                return
            
            # Check if message should be forwarded
            should_forward, reason = self.message_processor.should_forward_message(
                original_message, self.config.min_message_length
            )
            
            if not should_forward:
                logger.debug(f"Message skipped: {reason}")
                self.admin_manager.update_stats('message_skipped')
                return
            
            # Process the message
            processed_text = await self.process_message_content(original_message)
            
            if not processed_text:
                logger.debug("Message skipped: No content after processing")
                self.admin_manager.update_stats('message_skipped')
                return
            
            # Create inline keyboard with channel button
            keyboard = self.create_channel_button()
            
            # Forward media if present and enabled
            if original_message.media and self.config.forward_media:
                await self.client.send_message(
                    self.config.destination_group_id,
                    processed_text,
                    file=original_message.media,
                    buttons=keyboard
                )
            else:
                # Send text only
                await self.client.send_message(
                    self.config.destination_group_id,
                    processed_text,
                    buttons=keyboard
                )
            
            # Update statistics
            self.admin_manager.update_stats('message_forwarded')
            
            logger.info(f"Message forwarded successfully. Total: {self.admin_manager.stats.messages_forwarded}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.admin_manager.log_error("Message processing error", str(e))
    
    async def process_message_content(self, message) -> str:
        """Process message content (remove links, add reference, etc.)."""
        try:
            text = message.text or ""
            
            # Remove links
            processed_text = self.message_processor.remove_all_links(text)
            
            # Clean formatting
            processed_text = self.message_processor.clean_text_formatting(processed_text)
            
            # Check length limits
            if len(processed_text) > self.config.max_message_length:
                processed_text = processed_text[:self.config.max_message_length - 3] + "..."
            
            # Add reference
            processed_text = self.message_processor.add_custom_reference(processed_text)
            
            return processed_text
            
        except Exception as e:
            logger.error(f"Error processing message content: {e}")
            return ""
    
    def create_channel_button(self):
        """Create inline keyboard with channel button."""
        return [
            [KeyboardButtonUrl("🔗 Join Our Channel", self.config.channel_link)]
        ]
    
    async def send_startup_notification(self):
        """Send startup notification to admin."""
        try:
            startup_message = f"""
🤖 **Bot Started Successfully!**

✅ Connected as: {(await self.client.get_me()).first_name}
📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 Forwarding Status: {'Active' if self.is_forwarding else 'Inactive'}

**Configuration:**
📥 Source Group: {self.config.source_group_id}
📤 Destination Group: {self.config.destination_group_id}
🔗 Channel Link: {self.config.channel_link}
📝 Reference: {self.config.reference_text}

Use /help to see available commands.
            """.strip()
            
            await self.client.send_message(self.config.admin_user_id, startup_message)
            
        except Exception as e:
            logger.error(f"Failed to send startup notification: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown the bot."""
        try:
            logger.info("Shutting down bot...")
            
            # Send shutdown notification to admin
            try:
                shutdown_message = f"""
🤖 **Bot Shutting Down**

📊 **Final Statistics:**
• Messages Forwarded: {self.admin_manager.stats.messages_forwarded}
• Messages Skipped: {self.admin_manager.stats.messages_skipped}
• Errors: {self.admin_manager.stats.errors_count}
• Uptime: {self.admin_manager.stats.uptime_seconds} seconds

Bot stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """.strip()
                
                await self.client.send_message(self.config.admin_user_id, shutdown_message)
            except:
                pass  # Don't fail shutdown if notification fails
            
            # Disconnect client
            if self.client:
                await self.client.disconnect()
            
            logger.info("Bot shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main function to run the bot."""
    bot = None
    
    try:
        logger.info("Starting Telegram Forward Bot...")
        
        # Create and start bot
        bot = TelegramForwardBot()
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        # Cleanup
        if bot:
            await bot.shutdown()

if __name__ == "__main__":
    # Handle Windows event loop policy
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the bot
    asyncio.run(main())

