#!/usr/bin/env python3
"""
Admin Controls and Monitoring
Handles admin commands, status monitoring, and bot management features.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class BotStats:
    """Data class for bot statistics."""
    messages_forwarded: int = 0
    messages_skipped: int = 0
    errors_count: int = 0
    start_time: datetime = None
    last_message_time: datetime = None
    is_active: bool = False
    uptime_seconds: int = 0
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.last_message_time:
            data['last_message_time'] = self.last_message_time.isoformat()
        return data

class AdminManager:
    """Manages admin commands and bot monitoring."""
    
    def __init__(self, admin_user_id: int, bot_instance=None):
        """
        Initialize admin manager.
        
        Args:
            admin_user_id: Telegram user ID of the admin
            bot_instance: Reference to the main bot instance
        """
        self.admin_user_id = admin_user_id
        self.bot_instance = bot_instance
        self.stats = BotStats()
        self.command_history: List[Dict[str, Any]] = []
        self.error_log: List[Dict[str, Any]] = []
        
        # Admin commands mapping
        self.commands = {
            '/start': self.cmd_start_forwarding,
            '/stop': self.cmd_stop_forwarding,
            '/status': self.cmd_get_status,
            '/stats': self.cmd_get_detailed_stats,
            '/help': self.cmd_get_help,
            '/config': self.cmd_get_config,
            '/logs': self.cmd_get_logs,
            '/reset_stats': self.cmd_reset_stats,
            '/test': self.cmd_test_connection,
            '/update_reference': self.cmd_update_reference,
            '/update_channel': self.cmd_update_channel,
        }
        
        logger.info(f"Admin manager initialized for user ID: {admin_user_id}")
    
    async def handle_admin_command(self, event):
        """
        Handle incoming admin commands.
        
        Args:
            event: Telegram message event
        """
        try:
            # Verify admin authorization
            if not self.is_admin(event.sender_id):
                await event.reply("❌ Unauthorized. Only admin can use bot commands.")
                return
            
            message_text = event.message.text.strip()
            command_parts = message_text.split(' ', 1)
            command = command_parts[0].lower()
            args = command_parts[1] if len(command_parts) > 1 else ""
            
            # Log command usage
            self.log_command(command, args, event.sender_id)
            
            # Execute command
            if command in self.commands:
                await self.commands[command](event, args)
            else:
                await self.cmd_unknown_command(event, command)
                
        except Exception as e:
            logger.error(f"Error handling admin command: {e}")
            await event.reply(f"❌ Error executing command: {str(e)}")
            self.log_error("Command execution error", str(e))
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is authorized admin."""
        return user_id == self.admin_user_id
    
    def log_command(self, command: str, args: str, user_id: int):
        """Log admin command usage."""
        self.command_history.append({
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'args': args,
            'user_id': user_id
        })
        
        # Keep only last 100 commands
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
    
    def log_error(self, error_type: str, error_message: str):
        """Log error for admin monitoring."""
        self.error_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message
        })
        self.stats.errors_count += 1
        
        # Keep only last 50 errors
        if len(self.error_log) > 50:
            self.error_log = self.error_log[-50:]
    
    def update_stats(self, action: str):
        """Update bot statistics."""
        if action == 'message_forwarded':
            self.stats.messages_forwarded += 1
            self.stats.last_message_time = datetime.now()
        elif action == 'message_skipped':
            self.stats.messages_skipped += 1
        
        # Update uptime
        if self.stats.start_time:
            self.stats.uptime_seconds = int((datetime.now() - self.stats.start_time).total_seconds())
    
    # Admin Commands Implementation
    
    async def cmd_start_forwarding(self, event, args: str):
        """Start message forwarding."""
        if self.bot_instance:
            self.bot_instance.is_forwarding = True
            self.stats.is_active = True
            await event.reply("✅ **Message forwarding started!**\n\nBot is now actively forwarding messages from source to destination group.")
            logger.info("Message forwarding started by admin")
        else:
            await event.reply("❌ Bot instance not available")
    
    async def cmd_stop_forwarding(self, event, args: str):
        """Stop message forwarding."""
        if self.bot_instance:
            self.bot_instance.is_forwarding = False
            self.stats.is_active = False
            await event.reply("⏹️ **Message forwarding stopped!**\n\nBot has stopped forwarding messages.")
            logger.info("Message forwarding stopped by admin")
        else:
            await event.reply("❌ Bot instance not available")
    
    async def cmd_get_status(self, event, args: str):
        """Get current bot status."""
        status = "🟢 **ACTIVE**" if self.stats.is_active else "🔴 **INACTIVE**"
        uptime = str(timedelta(seconds=self.stats.uptime_seconds))
        
        status_message = f"""
🤖 **Bot Status Report**

📊 **Current Status:** {status}
⏱️ **Uptime:** {uptime}
📈 **Messages Forwarded:** {self.stats.messages_forwarded}
⏭️ **Messages Skipped:** {self.stats.messages_skipped}
❌ **Errors:** {self.stats.errors_count}

📅 **Started:** {self.stats.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.stats.start_time else 'N/A'}
🕐 **Last Message:** {self.stats.last_message_time.strftime('%Y-%m-%d %H:%M:%S') if self.stats.last_message_time else 'N/A'}

Use /stats for detailed statistics.
        """.strip()
        
        await event.reply(status_message)
    
    async def cmd_get_detailed_stats(self, event, args: str):
        """Get detailed bot statistics."""
        if not self.bot_instance:
            await event.reply("❌ Bot instance not available")
            return
        
        config = self.bot_instance.config if hasattr(self.bot_instance, 'config') else None
        
        stats_message = f"""
📊 **Detailed Bot Statistics**

**📈 Performance Metrics:**
• Messages Forwarded: {self.stats.messages_forwarded}
• Messages Skipped: {self.stats.messages_skipped}
• Success Rate: {(self.stats.messages_forwarded / max(self.stats.messages_forwarded + self.stats.messages_skipped, 1) * 100):.1f}%
• Error Count: {self.stats.errors_count}

**⏱️ Time Information:**
• Bot Started: {self.stats.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.stats.start_time else 'N/A'}
• Uptime: {str(timedelta(seconds=self.stats.uptime_seconds))}
• Last Activity: {self.stats.last_message_time.strftime('%Y-%m-%d %H:%M:%S') if self.stats.last_message_time else 'N/A'}

**🔧 Configuration:**
• Source Group: {config.source_group_id if config else 'N/A'}
• Destination Group: {config.destination_group_id if config else 'N/A'}
• Channel Link: {config.channel_link if config else 'N/A'}
• Reference Text: {config.reference_text if config else 'N/A'}

**📝 Recent Activity:**
• Commands Executed: {len(self.command_history)}
• Recent Errors: {len([e for e in self.error_log if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=24)])}

Use /logs to view recent errors.
        """.strip()
        
        await event.reply(stats_message)
    
    async def cmd_get_help(self, event, args: str):
        """Show help message with all available commands."""
        help_message = """
🤖 **Telegram Forward Bot - Admin Commands**

**🔄 Control Commands:**
/start - Start message forwarding
/stop - Stop message forwarding
/test - Test bot connection and configuration

**📊 Monitoring Commands:**
/status - View current bot status
/stats - View detailed statistics
/logs - View recent error logs
/config - View bot configuration

**⚙️ Configuration Commands:**
/update_reference <text> - Update reference text
/update_channel <link> - Update channel link
/reset_stats - Reset bot statistics

**ℹ️ Information Commands:**
/help - Show this help message

**📋 Features:**
✅ Auto-forward messages with link removal
✅ Add custom reference text to messages
✅ Attach channel button to forwarded messages
✅ Real-time status monitoring
✅ Comprehensive error logging
✅ Admin-only access control

**📞 Support:**
If you encounter any issues, check the logs with /logs command.
        """.strip()
        
        await event.reply(help_message)
    
    async def cmd_get_config(self, event, args: str):
        """Show current bot configuration."""
        if not self.bot_instance or not hasattr(self.bot_instance, 'config'):
            await event.reply("❌ Configuration not available")
            return
        
        config = self.bot_instance.config
        config_message = f"""
⚙️ **Bot Configuration**

**📱 Telegram Settings:**
• Session Name: {config.session_name}
• API Configured: {'✅' if config.api_id and config.api_hash else '❌'}
• Phone Configured: {'✅' if config.phone_number else '❌'}

**📢 Group Settings:**
• Source Group ID: {config.source_group_id}
• Destination Group ID: {config.destination_group_id}

**🎨 Customization:**
• Channel Link: {config.channel_link}
• Reference Text: {config.reference_text}

**🔧 Advanced Settings:**
• Min Message Length: {config.min_message_length}
• Max Message Length: {config.max_message_length}
• Forward Media: {'✅' if config.forward_media else '❌'}
• Log Level: {config.log_level}

**👤 Admin Settings:**
• Admin User ID: {config.admin_user_id}

Use /update_reference or /update_channel to modify settings.
        """.strip()
        
        await event.reply(config_message)
    
    async def cmd_get_logs(self, event, args: str):
        """Show recent error logs."""
        if not self.error_log:
            await event.reply("✅ No recent errors found!")
            return
        
        recent_errors = self.error_log[-10:]  # Last 10 errors
        
        logs_message = "🚨 **Recent Error Logs:**\n\n"
        for i, error in enumerate(recent_errors, 1):
            timestamp = datetime.fromisoformat(error['timestamp']).strftime('%m-%d %H:%M')
            logs_message += f"**{i}.** `{timestamp}` - {error['type']}\n"
            logs_message += f"   {error['message'][:100]}{'...' if len(error['message']) > 100 else ''}\n\n"
        
        logs_message += f"Showing {len(recent_errors)} of {len(self.error_log)} total errors."
        
        await event.reply(logs_message)
    
    async def cmd_reset_stats(self, event, args: str):
        """Reset bot statistics."""
        self.stats = BotStats()
        self.command_history.clear()
        self.error_log.clear()
        
        await event.reply("🔄 **Statistics Reset**\n\nAll bot statistics have been reset to zero.")
        logger.info("Bot statistics reset by admin")
    
    async def cmd_test_connection(self, event, args: str):
        """Test bot connection and configuration."""
        test_results = []
        
        # Test bot instance
        if self.bot_instance:
            test_results.append("✅ Bot instance: OK")
            
            # Test client connection
            try:
                me = await self.bot_instance.client.get_me()
                test_results.append(f"✅ Telegram connection: OK (@{me.username})")
            except Exception as e:
                test_results.append(f"❌ Telegram connection: {str(e)}")
            
            # Test group access
            try:
                source_entity = await self.bot_instance.client.get_entity(self.bot_instance.config.source_group_id)
                test_results.append(f"✅ Source group access: OK ({source_entity.title})")
            except Exception as e:
                test_results.append(f"❌ Source group access: {str(e)}")
            
            try:
                dest_entity = await self.bot_instance.client.get_entity(self.bot_instance.config.destination_group_id)
                test_results.append(f"✅ Destination group access: OK ({dest_entity.title})")
            except Exception as e:
                test_results.append(f"❌ Destination group access: {str(e)}")
        else:
            test_results.append("❌ Bot instance: Not available")
        
        test_message = "🔍 **Connection Test Results:**\n\n" + "\n".join(test_results)
        await event.reply(test_message)
    
    async def cmd_update_reference(self, event, args: str):
        """Update reference text."""
        if not args:
            await event.reply("❌ Please provide new reference text.\nUsage: /update_reference <new text>")
            return
        
        if self.bot_instance and hasattr(self.bot_instance, 'config'):
            self.bot_instance.config.update_reference_text(args)
            await event.reply(f"✅ **Reference text updated!**\n\nNew reference: {args}")
        else:
            await event.reply("❌ Bot configuration not available")
    
    async def cmd_update_channel(self, event, args: str):
        """Update channel link."""
        if not args:
            await event.reply("❌ Please provide new channel link.\nUsage: /update_channel <new link>")
            return
        
        if self.bot_instance and hasattr(self.bot_instance, 'config'):
            self.bot_instance.config.update_channel_link(args)
            await event.reply(f"✅ **Channel link updated!**\n\nNew link: {args}")
        else:
            await event.reply("❌ Bot configuration not available")
    
    async def cmd_unknown_command(self, event, command: str):
        """Handle unknown commands."""
        await event.reply(f"❓ Unknown command: {command}\n\nUse /help to see available commands.")

# Utility functions
def format_uptime(seconds: int) -> str:
    """Format uptime seconds into human-readable string."""
    return str(timedelta(seconds=seconds))

def calculate_success_rate(forwarded: int, skipped: int) -> float:
    """Calculate success rate percentage."""
    total = forwarded + skipped
    if total == 0:
        return 0.0
    return (forwarded / total) * 100

