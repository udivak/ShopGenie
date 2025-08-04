"""
Message formatting utilities for Telegram bot.
"""
import logging
from typing import List
from scrapers.base_scraper import Product

logger = logging.getLogger(__name__)

class MessageFormatter:
    """Utility class for formatting messages for Telegram."""
    
    @staticmethod
    def format_product_message(product: Product, index: int = 1) -> str:
        """
        Format a single product for Telegram message.
        
        Args:
            product: Product to format
            index: Product index in the list
            
        Returns:
            Formatted message string
        """
        try:
            # Start with product number and title
            message = f"🛍️ *{index}\\. {MessageFormatter._escape_markdown(product.title)}*\n\n"
            
            # Add price
            if product.price and product.price != "N/A":
                message += f"💰 *Price:* {MessageFormatter._escape_markdown(product.price)}\n"
            
            # Add rating with stars
            if product.rating > 0:
                stars = MessageFormatter._get_star_rating(product.rating)
                # Format rating: show whole numbers without decimal (5/5 instead of 5.0/5)
                if product.rating == int(product.rating):
                    rating_text = f"{int(product.rating)}/5"
                else:
                    rating_text = f"{product.rating:.1f}/5"
                escaped_rating = MessageFormatter._escape_markdown(rating_text)
                message += f"⭐ *Rating:* {escaped_rating} {stars}\n"
            
            # Add sales count
            if product.sales > 0:
                sales_text = MessageFormatter._format_sales_count(product.sales)
                message += f"📊 *Sales:* {sales_text}\n"
            
            # Add source
            message += f"🏪 *Source:* {product.source}\n\n"
            
            # Add purchase link
            if product.product_url:
                message += f"🔗 [View Product]({product.product_url})\n\n"
            
            message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting product message: {e}")
            return f"❌ Error formatting product information\n\n"
    
    @staticmethod
    def format_search_header(products: List[Product], query: str, platform: str = None) -> str:
        """Format search results header."""
        message = f"🔍 *Search Results for:* {MessageFormatter._escape_markdown(query)}\n"
        if platform:
            message += f"🏪 *Platform:* {MessageFormatter._escape_markdown(platform)}\n"
        message += f"📦 Found {len(products)} products\n\n"
        return message
    
    @staticmethod
    def format_product_caption(product: Product, index: int) -> str:
        """Format product caption for photo message."""
        try:
            # Start with product number and title
            message = f"*{index}\\. {MessageFormatter._escape_markdown(product.title)}*\n\n"
            
            # Add price
            if product.price and product.price != "N/A":
                message += f"💰 *Price:* {MessageFormatter._escape_markdown(product.price)}\n"
            
            # Add rating with stars
            if product.rating > 0:
                stars = MessageFormatter._get_star_rating(product.rating)
                # Format rating: show whole numbers without decimal (5/5 instead of 5.0/5)
                if product.rating == int(product.rating):
                    rating_text = f"{int(product.rating)}/5"
                else:
                    rating_text = f"{product.rating:.1f}/5"
                escaped_rating = MessageFormatter._escape_markdown(rating_text)
                message += f"⭐ *Rating:* {escaped_rating} {stars}\n"
            
            # Add sales count
            if product.sales > 0:
                sales_text = MessageFormatter._format_sales_count(product.sales)
                message += f"📊 *Sales:* {sales_text}\n"
            
            # Add source
            message += f"🏪 *Source:* {product.source}\n\n"
            
            # Add purchase link
            if product.product_url:
                message += f"🔗 [View Product]({product.product_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting product caption: {e}")
            return f"❌ Error formatting product information"
    
    @staticmethod
    def format_footer_message() -> str:
        """Format footer message."""
        return "🤖 *ShopGenie Bot* \\- Happy shopping\\! 🛒"
    
    @staticmethod
    def format_search_results(products: List[Product], query: str) -> str:
        """
        Format complete search results for Telegram.
        
        Args:
            products: List of products to format
            query: Original search query
            
        Returns:
            Complete formatted message
        """
        try:
            if not products:
                return MessageFormatter.format_no_results_message(query)
            
            # Header
            message = f"🔍 *Search Results for:* {MessageFormatter._escape_markdown(query)}\n"
            message += f"📦 Found {len(products)} products\n\n"
            message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Format each product
            for i, product in enumerate(products, 1):
                message += MessageFormatter.format_product_message(product, i)
            
            # Footer
            message += "🤖 *ShopGenie Bot* \\- Happy shopping\\! 🛒"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting search results: {e}")
            return "❌ Error formatting search results. Please try again."
    
    @staticmethod
    def format_no_results_message(query: str) -> str:
        """Format message when no results are found."""
        message = f"🔍 *Search Results for:* {MessageFormatter._escape_markdown(query)}\n\n"
        message += "😔 No products found matching your search\\.\n\n"
        message += "*Try:*\n"
        message += "• Using different keywords\n"
        message += "• Being more specific\n"
        message += "• Checking spelling\n\n"
        message += "🤖 *ShopGenie Bot* \\- Better luck next time\\!"
        
        return message
    
    @staticmethod
    def format_error_message(error_type: str = "general", platform: str = None) -> str:
        """Format error messages."""
        platform_text = platform or "the platform"
        
        if error_type == "network":
            message = "🌐 *Network Error*\n\n"
            message += f"Unable to connect to {platform_text}\\. This could be due to:\n"
            message += "• Temporary server issues\n"
            message += "• Network connectivity problems\n"
            message += "• Rate limiting\n\n"
            message += "Please try again in a few minutes\\."
        
        elif error_type == "timeout":
            message = "⏰ *Request Timeout*\n\n"
            message += "The search is taking longer than expected\\.\n"
            message += "Please try again with a different search term\\."
        
        else:
            message = "❌ *Something went wrong*\n\n"
            message += "An unexpected error occurred while searching\\.\n\n"
            message += "*Please check your search format:*\n"
            message += "`item name, platform` or `platform, item name`\n\n"
            message += "*Supported platforms:* Amazon, eBay\n\n"
            message += "*Examples:*\n"
            message += "• `bluetooth speaker, amazon`\n"
            message += "• `ebay, wireless headphones`"
        
        message += "\n\n🤖 *ShopGenie Bot*"
        return message

    @staticmethod
    def format_search_parameter_error(error_message: str) -> str:
        """Format search parameter error messages."""
        return error_message
    
    @staticmethod
    def format_help_message() -> str:
        """Format help message."""
        message = "🤖 *ShopGenie Bot Help*\n\n"
        message += "*How to use:*\n"
        message += "Send me your search in this format:\n"
        message += "`item name, platform` or `platform, item name`\n\n"
        
        message += "*Supported platforms:*\n"
        message += "• Amazon\n"
        message += "• eBay\n\n"
        
        message += "*Examples:*\n"
        message += "• `bluetooth speaker, amazon`\n"
        message += "• `ebay, wireless headphones`\n"
        message += "• `laptop on amazon`\n"
        message += "• `phone case from ebay`\n\n"
        
        message += "*Commands:*\n"
        message += "/start \\- Start the bot\n"
        message += "/help \\- Show this help message\n\n"
        
        message += "🛍️ Happy shopping with ShopGenie\\!"
        
        return message
    
    @staticmethod
    def format_start_message() -> str:
        """Format welcome/start message."""
        message = "🛍️ *Welcome to ShopGenie Bot\\!*\n\n"
        message += "I help you find the best products across multiple platforms\\!\n\n"
        message += "*How to search:*\n"
        message += "Send: `item name, platform`\n"
        message += "Or: `platform, item name`\n\n"
        
        message += "*Supported platforms:*\n"
        message += "• Amazon\n"
        message += "• eBay\n\n"
        
        message += "*Example:* `bluetooth speaker, amazon`\n\n"
        message += "Type /help for more information\\.\n\n"
        message += "Let's start shopping\\! 🛒"
        
        return message
    
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
    
    @staticmethod
    def _get_star_rating(rating: float) -> str:
        """Convert numeric rating to star representation using integer part."""
        # Use integer part of rating (4.x shows as 4 stars)
        full_stars = int(rating)
        empty_stars = 5 - full_stars
        
        return "⭐" * full_stars + "☆" * empty_stars
    
    @staticmethod
    def _format_sales_count(sales: int) -> str:
        """Format sales count with appropriate suffix."""
        if sales >= 1000000:
            return f"{sales / 1000000:.1f}M"
        elif sales >= 1000:
            return f"{sales / 1000:.1f}K"
        else:
            return str(sales)