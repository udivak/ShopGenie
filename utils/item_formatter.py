"""
General item formatter for consistent product display across all platforms.
"""
import logging
from typing import List, Optional
from scrapers.base_scraper import Product

logger = logging.getLogger(__name__)

class ItemFormatter:
    """General formatter for product items from any e-commerce platform."""
    
    @staticmethod
    def format_product_card(product: Product, index: int) -> dict:
        """
        Format a product into a standardized card format.
        
        Args:
            product: Product object from any scraper
            index: Display index/position
            
        Returns:
            Formatted product card dictionary
        """
        try:
            # Clean and standardize the title
            clean_title = ItemFormatter._clean_product_title(product.title, product.source)
            
            # Format price consistently
            clean_price = ItemFormatter._format_price(product.price)
            
            # Generate star rating display
            star_display = ItemFormatter._format_star_rating(product.rating)
            
            # Format sales/review count
            sales_display = ItemFormatter._format_sales_count(product.sales)
            
            # Ensure image URL is valid
            image_url = ItemFormatter._validate_image_url(product.image_url, product.source)
            
            # If no image URL, try to generate a fallback based on platform
            if not image_url:
                image_url = ItemFormatter._get_fallback_image(product.source, clean_title)
            
            # Platform display name
            platform_display = ItemFormatter._get_platform_display_name(product.source)
            
            return {
                'index': index,
                'title': clean_title,
                'price': clean_price,
                'rating': product.rating,
                'rating_display': star_display,
                'sales': product.sales,
                'sales_display': sales_display,
                'image_url': image_url,
                'product_url': product.product_url,
                'platform': platform_display,
                'has_image': bool(image_url),
                'is_valid': bool(clean_title and len(clean_title) > 3)
            }
            
        except Exception as e:
            logger.error(f"Error formatting product card: {e}")
            return {
                'index': index,
                'title': "Error formatting product",
                'price': "N/A",
                'rating': 0.0,
                'rating_display': "☆☆☆☆☆",
                'sales': 0,
                'sales_display': "0",
                'image_url': "",
                'product_url': "",
                'platform': product.source,
                'has_image': False,
                'is_valid': False
            }
    
    @staticmethod
    def format_telegram_caption(product_card: dict) -> str:
        """
        Format product card for Telegram photo caption.
        
        Args:
            product_card: Formatted product card from format_product_card
            
        Returns:
            Telegram-ready caption with MarkdownV2 formatting
        """
        try:
            caption = f"*{product_card['index']}\\. {ItemFormatter._escape_markdown(product_card['title'])}*\n\n"
            
            # Add price
            if product_card['price'] and product_card['price'] != "N/A":
                caption += f"💰 *Price:* {ItemFormatter._escape_markdown(product_card['price'])}\n"
            
            # Add rating with stars
            if product_card['rating'] > 0:
                rating_text = f"{product_card['rating']:.1f}/5" if product_card['rating'] != int(product_card['rating']) else f"{int(product_card['rating'])}/5"
                caption += f"⭐ *Rating:* {ItemFormatter._escape_markdown(rating_text)} {product_card['rating_display']}\n"
            
            # Add sales count
            if product_card['sales'] > 0:
                caption += f"📊 *Sales:* {product_card['sales_display']}\n"
            
            # Add platform
            caption += f"🏪 *Platform:* {product_card['platform']}\n\n"
            
            # Add purchase link
            if product_card['product_url']:
                caption += f"🔗 [View Product]({product_card['product_url']})"
            
            return caption
            
        except Exception as e:
            logger.error(f"Error formatting Telegram caption: {e}")
            return f"❌ Error formatting product information"
    
    @staticmethod
    def format_telegram_text(product_card: dict) -> str:
        """
        Format product card for Telegram text message (fallback when no image).
        
        Args:
            product_card: Formatted product card from format_product_card
            
        Returns:
            Telegram-ready text message with MarkdownV2 formatting
        """
        try:
            message = f"🛍️ *{product_card['index']}\\. {ItemFormatter._escape_markdown(product_card['title'])}*\n\n"
            
            # Add price
            if product_card['price'] and product_card['price'] != "N/A":
                message += f"💰 *Price:* {ItemFormatter._escape_markdown(product_card['price'])}\n"
            
            # Add rating with stars
            if product_card['rating'] > 0:
                rating_text = f"{product_card['rating']:.1f}/5" if product_card['rating'] != int(product_card['rating']) else f"{int(product_card['rating'])}/5"
                message += f"⭐ *Rating:* {ItemFormatter._escape_markdown(rating_text)} {product_card['rating_display']}\n"
            
            # Add sales count
            if product_card['sales'] > 0:
                message += f"📊 *Sales:* {product_card['sales_display']}\n"
            
            # Add platform
            message += f"🏪 *Platform:* {product_card['platform']}\n\n"
            
            # Add purchase link
            if product_card['product_url']:
                message += f"🔗 [View Product]({product_card['product_url']})\n\n"
            
            message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting Telegram text: {e}")
            return f"❌ Error formatting product information\n\n"
    
    @staticmethod
    def _clean_product_title(title: str, platform: str) -> str:
        """Clean and standardize product title."""
        if not title:
            return "Unknown Item"
        
        cleaned = title.strip()
        
        # Platform-specific cleaning
        if platform.lower() == "ebay":
            # Remove eBay-specific suffixes
            ebay_suffixes = [
                "| eBay",
                "- eBay",
                "Shop on eBay",
                "Buy It Now",
                "Best Offer"
            ]
            for suffix in ebay_suffixes:
                if cleaned.endswith(suffix):
                    cleaned = cleaned[:-len(suffix)].strip()
            
            # Remove common eBay prefixes
            ebay_prefixes = [
                "SPONSORED:",
                "Hot This Week:",
                "New Listing:",
                "BRAND NEW:"
            ]
            for prefix in ebay_prefixes:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
        
        elif platform.lower() == "amazon":
            # Remove Amazon-specific text
            amazon_suffixes = [
                "- Amazon.com",
                "on Amazon",
                "Amazon's Choice"
            ]
            for suffix in amazon_suffixes:
                if cleaned.endswith(suffix):
                    cleaned = cleaned[:-len(suffix)].strip()
        
        # General cleaning
        # Remove multiple spaces
        cleaned = " ".join(cleaned.split())
        
        # Truncate if too long (Telegram has limits)
        if len(cleaned) > 100:
            cleaned = cleaned[:97] + "..."
        
        return cleaned or "Unknown Item"
    
    @staticmethod
    def _format_price(price: str) -> str:
        """Format price consistently."""
        if not price or price == "N/A":
            return "N/A"
        
        # Remove extra whitespace
        price = price.strip()
        
        # If price already has currency symbol, return as-is
        if price.startswith(('$', '£', '€', '¥', '₹')):
            return price
        
        # Try to detect if it's a number and add $
        import re
        if re.match(r'^\d+(\.\d{2})?$', price):
            price = f"${price}"
        
        return price
    
    @staticmethod
    def _format_star_rating(rating: float) -> str:
        """Convert numeric rating to star representation."""
        if rating <= 0:
            return "☆☆☆☆☆"
        
        full_stars = int(rating)
        empty_stars = 5 - full_stars
        
        return "⭐" * full_stars + "☆" * empty_stars
    
    @staticmethod
    def _format_sales_count(sales: int) -> str:
        """Format sales count with appropriate suffix."""
        if sales <= 0:
            return "0"
        
        if sales >= 1000000:
            return f"{sales / 1000000:.1f}M"
        elif sales >= 1000:
            return f"{sales / 1000:.1f}K"
        else:
            return str(sales)
    
    @staticmethod
    def _validate_image_url(image_url: str, platform: str) -> str:
        """Validate and clean image URL."""
        if not image_url:
            return ""
        
        # Basic URL validation
        if not image_url.startswith(('http://', 'https://')):
            return ""
        
        # Platform-specific image URL validation
        if platform.lower() == "ebay":
            # eBay images should be from their CDN
            if 'ebayimg.com' not in image_url and 'ebaystatic.com' not in image_url:
                # Log but don't reject - eBay might use other CDNs
                logger.debug(f"Unusual eBay image URL: {image_url}")
        
        elif platform.lower() == "amazon":
            # Amazon images should be from their CDN
            if 'images-amazon.com' not in image_url and 'm.media-amazon.com' not in image_url:
                logger.debug(f"Unusual Amazon image URL: {image_url}")
        
        return image_url
    
    @staticmethod
    def _get_fallback_image(platform: str, title: str) -> str:
        """
        Get a fallback image URL when product image is not available.
        
        Args:
            platform: Platform name (e.g., 'ebay', 'amazon')
            title: Product title for potential image generation
            
        Returns:
            Fallback image URL or empty string
        """
        # Use placeholder image service for consistent product images
        # This creates a 400x400 image with platform branding and product name
        
        if platform.lower() == 'ebay':
            # Create a placeholder image with eBay branding
            # Using a public placeholder service that supports text
            title_encoded = title.replace(' ', '+')[:50]  # Limit length and encode spaces
            return f"https://via.placeholder.com/400x400/0064D2/FFFFFF?text=eBay+Product%0A{title_encoded}"
        
        elif platform.lower() == 'amazon':
            # Amazon placeholder (though Amazon usually has images)
            title_encoded = title.replace(' ', '+')[:50]
            return f"https://via.placeholder.com/400x400/FF9900/FFFFFF?text=Amazon+Product%0A{title_encoded}"
        
        else:
            # Generic placeholder for other platforms
            title_encoded = title.replace(' ', '+')[:50]
            return f"https://via.placeholder.com/400x400/6C757D/FFFFFF?text=Product%0A{title_encoded}"
    
    @staticmethod
    def _get_platform_display_name(platform: str) -> str:
        """Get user-friendly platform display name."""
        platform_names = {
            'amazon': 'Amazon',
            'ebay': 'eBay',
            'walmart': 'Walmart',
            'target': 'Target'
        }
        
        return platform_names.get(platform.lower(), platform.title())
    
    @staticmethod
    def _escape_markdown(text: str) -> str:
        """Escape special characters for MarkdownV2."""
        if not text:
            return ""
        
        # Characters that need escaping in MarkdownV2
        special_chars = r'_*[]()~`>#+-=|{}.!'
        
        escaped = ""
        for char in text:
            if char in special_chars:
                escaped += f"\\{char}"
            else:
                escaped += char
        
        return escaped