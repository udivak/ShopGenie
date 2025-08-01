"""
Item comparison and ranking utilities.
"""
from typing import List, Callable
import logging

from scrapers.base_scraper import Product

logger = logging.getLogger(__name__)

class ItemComparator:
    """Utility class for comparing and ranking products."""
    
    @staticmethod
    def calculate_score(product: Product, 
                       price_weight: float = 0.3,
                       rating_weight: float = 0.4,
                       sales_weight: float = 0.3) -> float:
        """
        Calculate a composite score for a product based on multiple factors.
        
        Args:
            product: Product to score
            price_weight: Weight for price factor (lower price = higher score)
            rating_weight: Weight for rating factor
            sales_weight: Weight for sales factor
            
        Returns:
            Composite score (higher is better)
        """
        try:
            # Normalize rating (0-5 scale to 0-1)
            rating_score = min(product.rating / 5.0, 1.0) if product.rating > 0 else 0.0
            
            # Normalize sales (log scale to handle wide range)
            import math
            if product.sales > 0:
                sales_score = min(math.log10(product.sales + 1) / 6.0, 1.0)  # Assuming max ~1M sales
            else:
                sales_score = 0.0
            
            # Price score (inverse - lower price is better)
            # Extract numeric price value
            price_value = ItemComparator._extract_price_value(product.price)
            if price_value > 0:
                # Normalize price (assuming reasonable range $1-$1000)
                price_score = max(0, 1.0 - min(price_value / 1000.0, 1.0))
            else:
                price_score = 0.5  # Neutral score for unknown price
            
            # Calculate weighted score
            total_score = (
                rating_score * rating_weight +
                sales_score * sales_weight +
                price_score * price_weight
            )
            
            logger.debug(f"Product: {product.title[:30]}... | "
                        f"Rating: {rating_score:.2f} | "
                        f"Sales: {sales_score:.2f} | "
                        f"Price: {price_score:.2f} | "
                        f"Total: {total_score:.2f}")
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating score for product {product.title}: {e}")
            return 0.0
    
    @staticmethod
    def _extract_price_value(price_str: str) -> float:
        """Extract numeric price value from price string."""
        import re
        if not price_str:
            return 0.0
        
        # Remove currency symbols and extract number
        price_clean = re.sub(r'[^\d.,]', '', price_str)
        price_clean = price_clean.replace(',', '')
        
        try:
            return float(price_clean)
        except ValueError:
            return 0.0
    
    @staticmethod
    def rank_products(products: List[Product], 
                     ranking_method: str = 'score',
                     limit: int = 4) -> List[Product]:
        """
        Rank products based on specified criteria.
        
        Args:
            products: List of products to rank
            ranking_method: Method to use ('score', 'price', 'rating', 'sales')
            limit: Maximum number of products to return
            
        Returns:
            Ranked list of products
        """
        if not products:
            return []
        
        try:
            if ranking_method == 'score':
                # Use composite score
                ranked = sorted(products, 
                              key=lambda p: ItemComparator.calculate_score(p),
                              reverse=True)
            
            elif ranking_method == 'price':
                # Sort by price (lowest first)
                ranked = sorted(products,
                              key=lambda p: ItemComparator._extract_price_value(p.price))
            
            elif ranking_method == 'rating':
                # Sort by rating (highest first)
                ranked = sorted(products,
                              key=lambda p: p.rating,
                              reverse=True)
            
            elif ranking_method == 'sales':
                # Sort by sales (highest first)
                ranked = sorted(products,
                              key=lambda p: p.sales,
                              reverse=True)
            
            else:
                logger.warning(f"Unknown ranking method: {ranking_method}, using 'score'")
                return ItemComparator.rank_products(products, 'score', limit)
            
            result = ranked[:limit]
            logger.info(f"Ranked {len(products)} products, returning top {len(result)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error ranking products: {e}")
            return products[:limit]  # Return first N as fallback
    
    @staticmethod
    def filter_products(products: List[Product],
                       min_rating: float = 0.0,
                       max_price: float = float('inf'),
                       min_sales: int = 0) -> List[Product]:
        """
        Filter products based on criteria.
        
        Args:
            products: List of products to filter
            min_rating: Minimum rating threshold
            max_price: Maximum price threshold
            min_sales: Minimum sales threshold
            
        Returns:
            Filtered list of products
        """
        filtered = []
        
        for product in products:
            try:
                # Check rating
                if product.rating < min_rating:
                    continue
                
                # Check price
                price_value = ItemComparator._extract_price_value(product.price)
                if price_value > max_price:
                    continue
                
                # Check sales
                if product.sales < min_sales:
                    continue
                
                filtered.append(product)
                
            except Exception as e:
                logger.debug(f"Error filtering product {product.title}: {e}")
                continue
        
        logger.info(f"Filtered {len(products)} products to {len(filtered)}")
        return filtered