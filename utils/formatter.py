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
                message += f"⭐ *Rating:* {product.rating:.1f}/5 {stars}\n"
            
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
    def format_error_message(error_type: str = "general") -> str:
        """Format error messages."""
        if error_type == "network":
            message = "🌐 *Network Error*\n\n"
            message += "Unable to connect to AliExpress\\. This could be due to:\n"
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
            message += "An unexpected error occurred while searching\\.\n"
            message += "Please try again or contact support if the problem persists\\."
        
        message += "\n\n🤖 *ShopGenie Bot*"
        return message
    
    @staticmethod
    def format_help_message() -> str:
        """Format help message."""
        message = "🤖 *ShopGenie Bot Help*\n\n"
        message += "*How to use:*\n"
        message += "• Send me any product name to search\n"
        message += "• I'll find the best 4 matches from AliExpress\n"
        message += "• Each result includes price, rating, and direct link\n\n"
        
        message += "*Examples:*\n"
        message += "• \"wireless headphones\"\n"
        message += "• \"smartphone case\"\n"
        message += "• \"laptop stand\"\n\n"
        
        message += "*Commands:*\n"
        message += "/start \\- Start the bot\n"
        message += "/help \\- Show this help message\n\n"
        
        message += "🛍️ Happy shopping with ShopGenie\\!"
        
        return message
    
    @staticmethod
    def format_start_message() -> str:
        """Format welcome/start message."""
        message = "🛍️ *Welcome to ShopGenie Bot\\!*\n\n"
        message += "I help you find the best products on AliExpress\\.\n\n"
        message += "*Just send me:*\n"
        message += "• Any product name or description\n"
        message += "• I'll search and show you the top 4 results\n"
        message += "• With prices, ratings, and direct purchase links\n\n"
        
        message += "*Example:* Try typing \"bluetooth speaker\"\n\n"
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
        """Convert numeric rating to star representation."""
        full_stars = int(rating)
        half_star = 1 if (rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        return "⭐" * full_stars + "⭐" * half_star + "☆" * empty_stars
    
    @staticmethod
    def _format_sales_count(sales: int) -> str:
        """Format sales count with appropriate suffix."""
        if sales >= 1000000:
            return f"{sales / 1000000:.1f}M"
        elif sales >= 1000:
            return f"{sales / 1000:.1f}K"
        else:
            return str(sales)