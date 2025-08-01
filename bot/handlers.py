"""
Telegram bot message handlers.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from scrapers.amazon_scraper import AmazonScraper
from utils.item_comparator import ItemComparator
from utils.formatter import MessageFormatter
from config import config

logger = logging.getLogger(__name__)

class BotHandlers:
    """Container class for all bot message handlers."""
    
    def __init__(self):
        self.scraper = AmazonScraper()
        self.comparator = ItemComparator()
        self.formatter = MessageFormatter()
    
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
            query = update.message.text.strip()
            
            if not query:
                await update.message.reply_text("Please send me a product name to search for.")
                return
            
            logger.info(f"User {user.id} searching for: {query}")
            
            # Send typing indicator
            await update.message.chat.send_action(action="typing")
            
            # Send initial response
            searching_message = await update.message.reply_text(
                f"🔍 Searching for '{query}' on Amazon...\nThis may take a few seconds."
            )
            
            try:
                # Perform search
                products = await self.scraper.search(query, config.MAX_SEARCH_RESULTS)
                
                if not products:
                    # No results found
                    message = self.formatter.format_no_results_message(query)
                    await searching_message.edit_text(
                        message,
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
                
                # Send header message
                header_message = self.formatter.format_search_header(top_products, query)
                await update.message.reply_text(
                    header_message,
                    parse_mode='MarkdownV2',
                    disable_web_page_preview=True
                )
                
                # Send individual product photos with captions
                for i, product in enumerate(top_products, 1):
                    try:
                        if product.image_url:
                            caption = self.formatter.format_product_caption(product, i)
                            await update.message.reply_photo(
                                photo=product.image_url,
                                caption=caption,
                                parse_mode='MarkdownV2'
                            )
                        else:
                            # Fallback to text message if no image
                            product_message = self.formatter.format_product_message(product, i)
                            await update.message.reply_text(
                                product_message,
                                parse_mode='MarkdownV2',
                                disable_web_page_preview=True
                            )
                    except Exception as img_error:
                        logger.warning(f"Failed to send image for product {i}: {img_error}")
                        # Fallback to text message
                        product_message = self.formatter.format_product_message(product, i)
                        await update.message.reply_text(
                            product_message,
                            parse_mode='MarkdownV2',
                            disable_web_page_preview=True
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
                logger.error(f"Search error for query '{query}': {search_error}")
                
                # Determine error type and send appropriate message
                if "timeout" in str(search_error).lower():
                    error_message = self.formatter.format_error_message("timeout")
                elif "network" in str(search_error).lower() or "connection" in str(search_error).lower():
                    error_message = self.formatter.format_error_message("network")
                else:
                    error_message = self.formatter.format_error_message("general")
                
                await searching_message.edit_text(
                    error_message,
                    parse_mode='MarkdownV2',
                    disable_web_page_preview=True
                )
            
        except Exception as e:
            logger.error(f"Error in search_products handler: {e}")
            
            try:
                await update.message.reply_text(
                    "❌ An unexpected error occurred. Please try again or contact support if the problem persists."
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
                    "❌ Sorry, something went wrong. Please try again."
                )
            except:
                pass  # Prevent cascading errors
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands."""
        try:
            await update.message.reply_text(
                "🤔 I don't understand that command.\n\n"
                "Just send me a product name to search, or use /help for more information."
            )
        except Exception as e:
            logger.error(f"Error in unknown_command handler: {e}")