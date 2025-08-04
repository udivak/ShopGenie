"""
Message parser utilities for extracting search parameters from user input.
"""
import re
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SearchRequest:
    """Represents a parsed search request."""
    item_name: Optional[str] = None
    platform: Optional[str] = None
    is_valid: bool = False
    error_message: Optional[str] = None

class MessageParser:
    """Parser for user messages to extract search parameters."""
    
    def __init__(self):
        """Initialize the message parser."""
        # Known e-commerce platforms and their variations
        self.platforms = {
            'amazon', 'amazon.com', 'amzn',
            'ebay', 'ebay.com', 'bay'
        }
        
        # Common separators
        self.separators = [',', ';', '|', ':', 'on', 'from', 'in']
        
    def parse_search_message(self, message: str) -> SearchRequest:
        """
        Parse a user message to extract item name and platform.
        
        Supports formats:
        - "item name, platform"
        - "platform, item name"
        - "item name on platform"
        - "search item name in platform"
        - etc.
        
        Args:
            message: User message to parse
            
        Returns:
            SearchRequest object with parsed data
        """
        if not message or not message.strip():
            return SearchRequest(
                error_message="Please provide a search query. Format: 'item name, platform' or 'platform, item name'"
            )
        
        # Clean the message
        cleaned_message = message.strip()
        
        # Try different parsing strategies
        search_request = (
            self._parse_comma_separated(cleaned_message) or
            self._parse_keyword_separated(cleaned_message) or
            self._parse_single_item(cleaned_message)
        )
        
        # Validate the result
        if search_request.item_name and search_request.platform:
            search_request.is_valid = True
        elif search_request.item_name and not search_request.platform:
            search_request.error_message = (
                "Missing platform! Please specify where to search.\n\n"
                "🔍 *Supported formats:*\n"
                "• `item name, platform`\n"
                "• `platform, item name`\n"
                "• `item name on platform`\n\n"
                "📱 *Supported platforms:* Amazon, eBay\n\n"
                "*Example:* `bluetooth speaker, amazon`"
            )
        elif search_request.platform and not search_request.item_name:
            search_request.error_message = (
                "Missing item name! Please specify what to search for.\n\n"
                "🔍 *Supported formats:*\n"
                "• `item name, platform`\n"
                "• `platform, item name`\n"
                "• `item name on platform`\n\n"
                "📱 *Supported platforms:* Amazon, eBay\n\n"
                "*Example:* `bluetooth speaker, amazon`"
            )
        else:
            search_request.error_message = (
                "Could not understand your search request!\n\n"
                "🔍 *Supported formats:*\n"
                "• `item name, platform`\n"
                "• `platform, item name`\n"
                "• `item name on platform`\n\n"
                "📱 *Supported platforms:* Amazon, eBay\n\n"
                "*Example:* `bluetooth speaker, amazon`"
            )
        
        return search_request
    
    def _parse_comma_separated(self, message: str) -> Optional[SearchRequest]:
        """Parse comma-separated format: 'item, platform' or 'platform, item'."""
        if ',' not in message:
            return None
        
        parts = [part.strip() for part in message.split(',', 1)]
        if len(parts) != 2:
            return None
        
        part1, part2 = parts
        
        # Check which part is the platform
        if self._is_platform(part1):
            return SearchRequest(item_name=part2, platform=part1)
        elif self._is_platform(part2):
            return SearchRequest(item_name=part1, platform=part2)
        
        return None
    
    def _parse_keyword_separated(self, message: str) -> Optional[SearchRequest]:
        """Parse keyword-separated format: 'item on/from/in platform'."""
        # Look for common keywords
        pattern = r'(.+?)\s+(on|from|in|at)\s+(.+?)$'
        match = re.search(pattern, message, re.IGNORECASE)
        
        if match:
            part1 = match.group(1).strip()
            keyword = match.group(2).strip()
            part2 = match.group(3).strip()
            
            # 'item on platform' format
            if self._is_platform(part2):
                return SearchRequest(item_name=part1, platform=part2)
        
        # Try reverse pattern: 'platform for item'
        pattern = r'(.+?)\s+(for)\s+(.+?)$'
        match = re.search(pattern, message, re.IGNORECASE)
        
        if match:
            part1 = match.group(1).strip()
            part2 = match.group(3).strip()
            
            if self._is_platform(part1):
                return SearchRequest(item_name=part2, platform=part1)
        
        return None
    
    def _parse_single_item(self, message: str) -> SearchRequest:
        """Parse single item without explicit platform."""
        # Check if the entire message is a platform
        if self._is_platform(message):
            return SearchRequest(platform=message)
        
        # Assume it's an item name without platform
        return SearchRequest(item_name=message)
    
    def _is_platform(self, text: str) -> bool:
        """Check if text represents a known platform."""
        if not text:
            return False
        
        text_lower = text.lower().strip()
        return text_lower in self.platforms
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platform names."""
        return ['Amazon', 'eBay']
    
    def get_example_formats(self) -> List[str]:
        """Get example search formats."""
        return [
            "bluetooth speaker, amazon",
            "ebay, wireless headphones",
            "laptop on amazon",
            "search for phone in ebay"
        ]