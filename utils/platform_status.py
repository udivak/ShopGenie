"""
Platform status tracking and user messaging for when scrapers encounter issues.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PlatformStatus:
    """Track platform availability and provide user-friendly status messages."""
    
    def __init__(self):
        self._status_cache: Dict[str, dict] = {}
        self._cache_duration = timedelta(minutes=15)  # Cache status for 15 minutes
    
    def record_platform_result(self, platform: str, success: bool, product_count: int = 0):
        """
        Record the result of a platform search.
        
        Args:
            platform: Platform name (e.g., 'ebay', 'amazon')
            success: Whether the search completed without errors
            product_count: Number of products found
        """
        now = datetime.now()
        
        # Determine status based on results
        if not success:
            status = 'error'
        elif product_count == 0:
            status = 'limited'  # Working but returning no results (possible bot detection)
        else:
            status = 'working'
        
        self._status_cache[platform] = {
            'status': status,
            'last_checked': now,
            'product_count': product_count,
            'success': success
        }
        
        logger.info(f"Platform {platform} status: {status} ({product_count} products)")
    
    def get_platform_status(self, platform: str) -> Optional[str]:
        """
        Get the current status of a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Status string: 'working', 'limited', 'error', or None if no data
        """
        if platform not in self._status_cache:
            return None
        
        cache_entry = self._status_cache[platform]
        
        # Check if cache is still valid
        if datetime.now() - cache_entry['last_checked'] > self._cache_duration:
            return None
        
        return cache_entry['status']
    
    def get_user_message(self, platform: str, search_term: str) -> str:
        """
        Get a user-friendly message based on platform status.
        
        Args:
            platform: Platform name
            search_term: What the user was searching for
            
        Returns:
            Formatted message for the user
        """
        status = self.get_platform_status(platform)
        platform_display = platform.title()
        
        if status == 'error':
            return (
                f"⚠️ *{platform_display} Temporarily Unavailable*\n\n"
                f"Sorry, we're having trouble connecting to {platform_display} right now\\. "
                f"This could be due to:\n"
                f"• Server maintenance\n"
                f"• Network issues\n"
                f"• High traffic\n\n"
                f"Please try again in a few minutes or search on Amazon instead\\."
            )
        
        elif status == 'limited':
            return (
                f"🤖 *{platform_display} Anti\\-Bot Detection*\n\n"
                f"It looks like {platform_display} is limiting automated searches right now\\. "
                f"This is common when they detect bot traffic\\.\n\n"
                f"*What you can do:*\n"
                f"• Try a different search term\n"
                f"• Search on Amazon instead\n"
                f"• Try again in 10\\-15 minutes\n\n"
                f"Amazon searches are working normally\\!"
            )
        
        else:
            # Default no results message
            return (
                f"😔 *No results found for:* {search_term}\n\n"
                f"*Try:*\n"
                f"• Using different keywords\n"
                f"• Being more specific\n"
                f"• Checking spelling\n"
                f"• Searching on Amazon instead\n\n"
                f"💡 *Tip:* Amazon typically has more inventory\\!"
            )

# Global instance
platform_status = PlatformStatus()