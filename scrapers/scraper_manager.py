"""
Scraper manager to handle multiple e-commerce platforms.
"""
import logging
from typing import Dict, List, Optional, Union

from .base_scraper import BaseScraper, Product
from .amazon_scraper import AmazonScraper
from .ebay_scraper import EbayScraper

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages multiple e-commerce scrapers."""
    
    def __init__(self):
        """Initialize the scraper manager with available scrapers."""
        self._scrapers: Dict[str, BaseScraper] = {
            'amazon': AmazonScraper(),
            'ebay': EbayScraper()
        }
        
        # Aliases for common variations
        self._aliases = {
            'amazon.com': 'amazon',
            'amazon': 'amazon',
            'amzn': 'amazon',
            'ebay.com': 'ebay',
            'ebay': 'ebay',
            'bay': 'ebay'
        }
        
        logger.info(f"Initialized scraper manager with {len(self._scrapers)} scrapers")
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available e-commerce platforms."""
        return list(self._scrapers.keys())
    
    def get_platform_aliases(self) -> Dict[str, str]:
        """Get platform aliases mapping."""
        return self._aliases.copy()
    
    def normalize_platform(self, platform: str) -> Optional[str]:
        """
        Normalize platform name to standard format.
        
        Args:
            platform: Platform name (case-insensitive)
            
        Returns:
            Normalized platform name or None if not found
        """
        if not platform:
            return None
            
        platform_lower = platform.lower().strip()
        
        # Direct match
        if platform_lower in self._scrapers:
            return platform_lower
            
        # Alias match
        if platform_lower in self._aliases:
            return self._aliases[platform_lower]
            
        return None
    
    def is_platform_supported(self, platform: str) -> bool:
        """
        Check if a platform is supported.
        
        Args:
            platform: Platform name
            
        Returns:
            True if platform is supported, False otherwise
        """
        return self.normalize_platform(platform) is not None
    
    async def search(self, platform: str, query: str, max_results: int = 50) -> List[Product]:
        """
        Search for products on a specific platform.
        
        Args:
            platform: E-commerce platform name
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        normalized_platform = self.normalize_platform(platform)
        
        if not normalized_platform:
            logger.warning(f"Unsupported platform: {platform}")
            return []
        
        scraper = self._scrapers[normalized_platform]
        
        try:
            logger.info(f"Searching {normalized_platform} for: {query}")
            products = await scraper.search(query, max_results)
            logger.info(f"Found {len(products)} products on {normalized_platform}")
            return products
            
        except Exception as e:
            logger.error(f"Error searching {normalized_platform}: {e}")
            return []
    
    def get_platform_display_name(self, platform: str) -> str:
        """
        Get user-friendly display name for platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Display name for the platform
        """
        normalized = self.normalize_platform(platform)
        
        display_names = {
            'amazon': 'Amazon',
            'ebay': 'eBay'
        }
        
        return display_names.get(normalized, platform.title())