"""
Base scraper class for e-commerce platforms.
Provides a common interface for different e-commerce scrapers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Product:
    """Data class representing a product."""
    title: str
    price: str
    rating: float
    sales: int
    image_url: str
    product_url: str
    source: str = "unknown"
    
    def to_dict(self) -> Dict:
        """Convert product to dictionary."""
        return {
            'title': self.title,
            'price': self.price,
            'rating': self.rating,
            'sales': self.sales,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'source': self.source
        }

class BaseScraper(ABC):
    """Abstract base class for e-commerce scrapers."""
    
    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        self.base_url = base_url
        self.headers = headers or {}
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[Product]:
        """
        Search for products based on query.
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        pass
    
    @abstractmethod
    def _parse_product(self, element) -> Optional[Product]:
        """
        Parse a single product element from the page.
        
        Args:
            element: HTML element containing product data
            
        Returns:
            Product object or None if parsing fails
        """
        pass
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\t', ' ')
    
    def _extract_number(self, text: str) -> float:
        """Extract numeric value from text."""
        import re
        if not text:
            return 0.0
        
        # Remove currency symbols and extract number
        numbers = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return 0.0
        return 0.0