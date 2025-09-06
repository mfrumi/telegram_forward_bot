#!/usr/bin/env python3
"""
Message Processing Utilities
Handles message text processing, link removal, and content modification.
"""

import re
import logging
from typing import List, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Utility class for processing and modifying message content."""
    
    def __init__(self, reference_text: str = "📢 Forwarded by Bot"):
        """
        Initialize the message processor.
        
        Args:
            reference_text: Custom reference text to add to messages
        """
        self.reference_text = reference_text
        
        # Compile regex patterns for better performance
        self.url_patterns = [
            re.compile(r'https?://[^\s]+', re.IGNORECASE),  # HTTP/HTTPS URLs
            re.compile(r'www\.[^\s]+', re.IGNORECASE),      # www URLs
            re.compile(r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*', re.IGNORECASE)  # Domain URLs
        ]
        
        self.telegram_patterns = [
            re.compile(r'(?:https?://)?(?:t\.me|telegram\.me)/[^\s]+', re.IGNORECASE),
            re.compile(r'@[a-zA-Z0-9_]+', re.IGNORECASE),  # Username mentions
            re.compile(r'tg://[^\s]+', re.IGNORECASE)      # Telegram deep links
        ]
        
        self.channel_patterns = [
            re.compile(r'(?:join|channel|group)[\s]*:[\s]*@?[a-zA-Z0-9_]+', re.IGNORECASE),
            re.compile(r'(?:telegram|tg)[\s]*(?:channel|group|chat)[\s]*:?[\s]*@?[a-zA-Z0-9_]+', re.IGNORECASE)
        ]
    
    def remove_all_links(self, text: str) -> str:
        """
        Remove all types of links from message text.
        
        Args:
            text: Original message text
            
        Returns:
            Text with all links removed
        """
        if not text:
            return text
            
        processed_text = text
        
        # Remove standard URLs
        for pattern in self.url_patterns:
            processed_text = pattern.sub('', processed_text)
        
        # Remove Telegram-specific links
        for pattern in self.telegram_patterns:
            processed_text = pattern.sub('', processed_text)
        
        # Remove channel/group references
        for pattern in self.channel_patterns:
            processed_text = pattern.sub('', processed_text)
        
        # Clean up extra whitespace and line breaks
        processed_text = re.sub(r'\s+', ' ', processed_text)
        processed_text = re.sub(r'\n\s*\n', '\n', processed_text)
        processed_text = processed_text.strip()
        
        return processed_text
    
    def add_custom_reference(self, text: str) -> str:
        """
        Add custom reference text to the message.
        
        Args:
            text: Processed message text
            
        Returns:
            Text with reference added
        """
        if not text:
            return self.reference_text
            
        return f"{text}\n\n{self.reference_text}"
    
    def extract_media_info(self, message) -> dict:
        """
        Extract media information from a message.
        
        Args:
            message: Telegram message object
            
        Returns:
            Dictionary containing media information
        """
        media_info = {
            'has_media': False,
            'media_type': None,
            'file_size': 0,
            'file_name': None
        }
        
        if message.media:
            media_info['has_media'] = True
            
            if hasattr(message.media, 'photo'):
                media_info['media_type'] = 'photo'
            elif hasattr(message.media, 'document'):
                media_info['media_type'] = 'document'
                if hasattr(message.media.document, 'size'):
                    media_info['file_size'] = message.media.document.size
                if hasattr(message.media.document, 'attributes'):
                    for attr in message.media.document.attributes:
                        if hasattr(attr, 'file_name'):
                            media_info['file_name'] = attr.file_name
            elif hasattr(message.media, 'video'):
                media_info['media_type'] = 'video'
            elif hasattr(message.media, 'audio'):
                media_info['media_type'] = 'audio'
        
        return media_info
    
    def should_forward_message(self, message, min_length: int = 10) -> Tuple[bool, str]:
        """
        Determine if a message should be forwarded based on various criteria.
        
        Args:
            message: Telegram message object
            min_length: Minimum text length for forwarding
            
        Returns:
            Tuple of (should_forward: bool, reason: str)
        """
        # Skip empty messages
        if not message.text and not message.media:
            return False, "Empty message"
        
        # Skip very short messages (likely spam)
        if message.text and len(message.text.strip()) < min_length:
            return False, f"Message too short (< {min_length} characters)"
        
        # Skip messages that are only links
        text_without_links = self.remove_all_links(message.text or "")
        if message.text and len(text_without_links.strip()) < 5:
            return False, "Message contains only links"
        
        # Skip messages from bots (if sender info is available)
        if hasattr(message, 'sender') and message.sender and hasattr(message.sender, 'bot'):
            if message.sender.bot:
                return False, "Message from bot"
        
        return True, "Message approved for forwarding"
    
    def clean_text_formatting(self, text: str) -> str:
        """
        Clean and normalize text formatting.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return text
        
        # Remove excessive emojis (more than 3 consecutive)
        text = re.sub(r'([\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]){4,}', r'\1\1\1', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{4,}', '!!!', text)
        text = re.sub(r'[?]{4,}', '???', text)
        text = re.sub(r'[.]{4,}', '...', text)
        
        # Remove excessive capitalization (more than 3 consecutive caps)
        text = re.sub(r'[A-Z]{4,}', lambda m: m.group()[:3], text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def get_processing_stats(self, original_text: str, processed_text: str) -> dict:
        """
        Get statistics about the text processing.
        
        Args:
            original_text: Original message text
            processed_text: Processed message text
            
        Returns:
            Dictionary with processing statistics
        """
        return {
            'original_length': len(original_text) if original_text else 0,
            'processed_length': len(processed_text) if processed_text else 0,
            'links_removed': len(re.findall(r'https?://[^\s]+', original_text or "")),
            'mentions_removed': len(re.findall(r'@[a-zA-Z0-9_]+', original_text or "")),
            'reduction_percentage': round(
                ((len(original_text or "") - len(processed_text or "")) / max(len(original_text or ""), 1)) * 100, 2
            )
        }

# Utility functions for standalone use
def quick_remove_links(text: str) -> str:
    """Quick function to remove links from text."""
    processor = MessageProcessor()
    return processor.remove_all_links(text)

def quick_add_reference(text: str, reference: str = "📢 Forwarded by Bot") -> str:
    """Quick function to add reference to text."""
    processor = MessageProcessor(reference)
    return processor.add_custom_reference(text)

