#!/usr/bin/env python3
"""
Configuration Management
Handles loading and validation of environment variables and bot settings.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class BotConfig:
    """Configuration manager for the Telegram bot."""
    
    def __init__(self, env_file: str = '.env'):
        """
        Initialize configuration from environment variables.
        
        Args:
            env_file: Path to the .env file
        """
        # Load environment variables
        load_dotenv(env_file)
        
        # Telegram API Configuration
        self.api_id = self._get_int_env('API_ID')
        self.api_hash = self._get_env('API_HASH')
        self.phone_number = self._get_env('PHONE_NUMBER')
        self.session_name = self._get_env('SESSION_NAME', 'telegram_forward_bot')
        
        # Group/Channel Configuration
        self.source_group_id = self._get_int_env('SOURCE_GROUP_ID')
        self.destination_group_id = self._get_int_env('DESTINATION_GROUP_ID')
        
        # Bot Customization
        self.channel_link = self._get_env('CHANNEL_LINK', 'https://t.me/your_channel')
        self.reference_text = self._get_env('REFERENCE_TEXT', '📢 Forwarded by Bot')
        
        # Admin Configuration
        self.admin_user_id = self._get_int_env('ADMIN_USER_ID')
        
        # Optional Settings
        self.min_message_length = self._get_int_env('MIN_MESSAGE_LENGTH', 10)
        self.max_message_length = self._get_int_env('MAX_MESSAGE_LENGTH', 4000)
        self.forward_media = self._get_bool_env('FORWARD_MEDIA', True)
        self.log_level = self._get_env('LOG_LEVEL', 'INFO')
        
        # Validate required configuration
        self._validate_config()
        
        logger.info("Configuration loaded successfully")
    
    def _get_env(self, key: str, default: Optional[str] = None) -> str:
        """Get environment variable with optional default."""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _get_int_env(self, key: str, default: Optional[int] = None) -> int:
        """Get integer environment variable with optional default."""
        value = os.getenv(key)
        if value is None:
            if default is not None:
                return default
            raise ValueError(f"Required environment variable {key} is not set")
        
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Environment variable {key} must be an integer, got: {value}")
    
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable with default."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _validate_config(self):
        """Validate required configuration values."""
        errors = []
        
        if not self.api_id or self.api_id == 0:
            errors.append("API_ID is required and must be a valid integer")
        
        if not self.api_hash:
            errors.append("API_HASH is required")
        
        if not self.phone_number:
            errors.append("PHONE_NUMBER is required")
        
        if not self.source_group_id or self.source_group_id == 0:
            errors.append("SOURCE_GROUP_ID is required and must be a valid integer")
        
        if not self.destination_group_id or self.destination_group_id == 0:
            errors.append("DESTINATION_GROUP_ID is required and must be a valid integer")
        
        if not self.admin_user_id or self.admin_user_id == 0:
            errors.append("ADMIN_USER_ID is required and must be a valid integer")
        
        if self.source_group_id == self.destination_group_id:
            errors.append("SOURCE_GROUP_ID and DESTINATION_GROUP_ID cannot be the same")
        
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_message)
            raise ValueError(error_message)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration (excluding sensitive data)."""
        return {
            'session_name': self.session_name,
            'source_group_id': self.source_group_id,
            'destination_group_id': self.destination_group_id,
            'channel_link': self.channel_link,
            'reference_text': self.reference_text,
            'admin_user_id': self.admin_user_id,
            'min_message_length': self.min_message_length,
            'max_message_length': self.max_message_length,
            'forward_media': self.forward_media,
            'log_level': self.log_level,
            'api_configured': bool(self.api_id and self.api_hash),
            'phone_configured': bool(self.phone_number)
        }
    
    def update_reference_text(self, new_reference: str):
        """Update the reference text dynamically."""
        self.reference_text = new_reference
        logger.info(f"Reference text updated to: {new_reference}")
    
    def update_channel_link(self, new_link: str):
        """Update the channel link dynamically."""
        self.channel_link = new_link
        logger.info(f"Channel link updated to: {new_link}")

# Global configuration instance
config = None

def get_config(env_file: str = '.env') -> BotConfig:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = BotConfig(env_file)
    return config

def reload_config(env_file: str = '.env') -> BotConfig:
    """Reload the configuration from environment variables."""
    global config
    config = BotConfig(env_file)
    return config

