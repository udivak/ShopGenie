"""
Telegram bot message handlers.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from scrapers.scraper_manager import ScraperManager
from utils.item_comparator import ItemComparator
from utils.formatter import MessageFormatter
from utils.message_parser import MessageParser
from utils.item_formatter import ItemFormatter
from utils.platform_status import platform_status
from config import config

logger = logging.getLogger(__name__)

class BotHandlers:
    """Container class for all bot message handlers."""
    
    def __init__(self):
        self.scraper_manager = ScraperManager()
        self.comparator = ItemComparator()
        self.formatter = MessageFormatter()
        self.item_formatter = ItemFormatter()
        self.parser = MessageParser()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        try:
            user = update.effective_user
            logger.info(f"User {user.id} ({user.username}) started the bot")
            
            message = self.formatter.format_start_message()
            await update.message.reply_text(
                message,
                parse_mode='MarkdownV2',
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text(
                "Welcome to ShopGenie Bot! Send me a product name to search."
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        try:
            message = self.formatter.format_help_message()
            await update.message.reply_text(
                message,
                parse_mode='MarkdownV2',
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text(
                "ShopGenie Bot Help:\n\n"
                "Send me any product name to search for items on Amazon.\n"
                "I'll show you the top 4 results with prices and ratings!"
            )
    
    async def search_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle product search messages."""
        try:
            user = update.effective_user
            message_text = update.message.text.strip()
            
            if not message_text:
                await update.message.reply_text("Please send me a search query.")
                return
            
            logger.info(f"User {user.id} sent message: {message_text}")
            
            # Parse the search request
            search_request = self.parser.parse_search_message(message_text)
            
            # Check if parsing was successful
            if not search_request.is_valid:
                if search_request.error_message:
                    await update.message.reply_text(
                        search_request.error_message,
                        parse_mode='MarkdownV2',
                        disable_web_page_preview=True
                    )
                else:
                    await update.message.reply_text(
                        "Could not understand your search request. Please use the format: 'item name, platform'"
                    )
                return
            
            # Validate platform
            if not self.scraper_manager.is_platform_supported(search_request.platform):
                await update.message.reply_text(
                    f"Platform '{search_request.platform}' is not supported. "
                    f"Supported platforms: {', '.join(self.scraper_manager.get_available_platforms())}"
                )
                return
            
            logger.info(f"User {user.id} searching for: {search_request.item_name} on {search_request.platform}")
            
            # Send typing indicator
            await update.message.chat.send_action(action="typing")
            
            # Get platform display name
            platform_display = self.scraper_manager.get_platform_display_name(search_request.platform)
            
            # Send initial response
            searching_message = await update.message.reply_text(
                f"🔍 Searching for '{search_request.item_name}' on {platform_display}...\nThis may take a few seconds."
            )
            
            try:
                # Perform search using the scraper manager
                products = await self.scraper_manager.search(
                    search_request.platform, 
                    search_request.item_name, 
                    config.MAX_SEARCH_RESULTS
                )
                
                # Record platform status
                platform_status.record_platform_result(
                    search_request.platform, 
                    success=True, 
                    product_count=len(products)
                )
                
                if not products:
                    # No results found - check if it's a platform issue
                    status_message = platform_status.get_user_message(
                        search_request.platform, 
                        search_request.item_name
                    )
                    await searching_message.edit_text(
                        status_message,
                        parse_mode='MarkdownV2',
                        disable_web_page_preview=True
                    )
                    return
                
                # Rank products and get top results
                top_products = self.comparator.rank_products(
                    products, 
                    ranking_method='score',
                    limit=config.TOP_RESULTS_COUNT
                )
                
                # Delete the searching message
                await searching_message.delete()
                
                # Send header message with platform info
                header_message = self.formatter.format_search_header(
                    top_products, 
                    search_request.item_name,
                    platform_display
                )
                await update.message.reply_text(
                    header_message,
                    parse_mode='MarkdownV2',
                    disable_web_page_preview=True
                )
                
                # Send individual product photos with captions using the new formatter
                for i, product in enumerate(top_products, 1):
                    try:
                        # Format product using the general item formatter
                        product_card = self.item_formatter.format_product_card(product, i)
                        
                        # Skip invalid products
                        if not product_card['is_valid']:
                            logger.warning(f"Skipping invalid product {i}: {product_card['title']}")
                            continue
                        
                        if product_card['has_image'] and product_card['image_url']:
                            # Send photo with caption
                            caption = self.item_formatter.format_telegram_caption(product_card)
                            await update.message.reply_photo(
                                photo=product_card['image_url'],
                                caption=caption,
                                parse_mode='MarkdownV2'
                            )
                        else:
                            # Fallback to text message if no image
                            product_message = self.item_formatter.format_telegram_text(product_card)
                            await update.message.reply_text(
                                product_message,
                                parse_mode='MarkdownV2',
                                disable_web_page_preview=True
                            )
                    except Exception as img_error:
                        logger.warning(f"Failed to send image for product {i}: {img_error}")
                        # Fallback to text message using the general formatter
                        try:
                            product_card = self.item_formatter.format_product_card(product, i)
                            product_message = self.item_formatter.format_telegram_text(product_card)
                            await update.message.reply_text(
                                product_message,
                                parse_mode='MarkdownV2',
                                disable_web_page_preview=True
                            )
                        except Exception as fallback_error:
                            logger.error(f"Fallback formatting also failed for product {i}: {fallback_error}")
                            # Ultimate fallback - simple text
                            await update.message.reply_text(
                                f"❌ Error displaying product {i}: {product.title[:50]}..."
                            )
                
                # Send footer message
                footer_message = self.formatter.format_footer_message()
                await update.message.reply_text(
                    footer_message,
                    parse_mode='MarkdownV2',
                    disable_web_page_preview=True
                )
                
                logger.info(f"Successfully sent {len(top_products)} results to user {user.id}")
                
            except Exception as search_error:
                logger.error(f"Search error for query '{search_request.item_name}' on {search_request.platform}: {search_error}")
                
                # Record platform failure
                platform_status.record_platform_result(
                    search_request.platform, 
                    success=False, 
                    product_count=0
                )
                
                # Get platform-specific error message
                if "timeout" in str(search_error).lower() or "unavailable" in str(search_error).lower():
                    error_message = platform_status.get_user_message(
                        search_request.platform, 
                        search_request.item_name
                    )
                else:
                    # Fallback to generic error
                    error_message = self.formatter.format_error_message("general", platform_display)
                
                await searching_message.edit_text(
                    error_message,
                    parse_mode='MarkdownV2',
                    disable_web_page_preview=True
                )
            
        except Exception as e:
            logger.error(f"Error in search_products handler: {e}")
            
            try:
                await update.message.reply_text(
                    "❌ Something went wrong while processing your search\\.\n\n"
                    "🔍 *Please use this format:*\n"
                    "`item name, platform` or `platform, item name`\n\n"
                    "📱 *Supported platforms:* Amazon, eBay\n\n"
                    "*Examples:*\n"
                    "• `bluetooth speaker, amazon`\n"
                    "• `ebay, wireless headphones`\n"
                    "• `laptop on amazon`",
                    parse_mode='MarkdownV2'
                )
            except:
                pass  # Prevent cascading errors
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors that occur during bot operation."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to notify the user if possible
        if isinstance(update, Update) and update.message:
            try:
                await update.message.reply_text(
                    "❌ Oops\\! Something unexpected happened\\.\n\n"
                    "🔍 *Please use this format:*\n"
                    "`item name, platform` or `platform, item name`\n\n"
                    "📱 *Supported platforms:* Amazon, eBay\n\n"
                    "*Examples:*\n"
                    "• `bluetooth speaker, amazon`\n"
                    "• `ebay, wireless headphones`\n"
                    "• `phone case from ebay`",
                    parse_mode='MarkdownV2'
                )
            except:
                pass  # Prevent cascading errors
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands."""
        try:
            await update.message.reply_text(
                "🤔 I don't understand that command\\.\n\n"
                "🔍 *Please use this format:*\n"
                "`item name, platform` or `platform, item name`\n\n"
                "📱 *Supported platforms:* Amazon, eBay\n\n"
                "*Examples:*\n"
                "• `bluetooth speaker, amazon`\n"
                "• `ebay, wireless headphones`\n"
                "• `laptop on amazon`\n\n"
                "Or use /help for more information\\.",
                parse_mode='MarkdownV2'
            )
        except Exception as e:
            logger.error(f"Error in unknown_command handler: {e}")