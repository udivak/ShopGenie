"""
Main Telegram bot implementation.
"""
import logging
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters,
    ContextTypes
)

from .handlers import BotHandlers
from config import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ShopGenieBot:
    """Main Telegram bot class."""
    
    def __init__(self, token: str):
        """
        Initialize the bot with the given token.
        
        Args:
            token: Telegram bot token
        """
        self.token = token
        self.application = None
        self.handlers = BotHandlers()
        
    def setup_handlers(self) -> None:
        """Set up message and command handlers."""
        if not self.application:
            raise RuntimeError("Application not initialized. Call build() first.")
        
        # Command handlers
        self.application.add_handler(
            CommandHandler("start", self.handlers.start_command)
        )
        
        self.application.add_handler(
            CommandHandler("help", self.handlers.help_command)
        )
        
        # Message handler for product searches (non-command messages)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handlers.search_products
            )
        )
        
        # Handler for unknown commands
        self.application.add_handler(
            MessageHandler(
                filters.COMMAND,
                self.handlers.unknown_command
            )
        )
        
        # Error handler
        self.application.add_error_handler(self.handlers.error_handler)
        
        logger.info("Bot handlers configured successfully")
    
    def build(self) -> None:
        """Build the bot application."""
        try:
            # Create application
            self.application = Application.builder().token(self.token).build()
            
            # Setup handlers
            self.setup_handlers()
            
            logger.info("Bot application built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build bot application: {e}")
            raise
    
    async def start_polling(self) -> None:
        """Start the bot with polling mode."""
        if not self.application:
            raise RuntimeError("Application not built. Call build() first.")
        
        try:
            logger.info("Starting bot with polling...")
            
            # Start polling
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            logger.info("Bot is running and polling for updates...")
            
            # Keep the bot running
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise
        finally:
            # Cleanup
            await self.stop()
    
    async def start_webhook(self, webhook_url: str, port: int = 8443, 
                           cert_path: str = None, key_path: str = None) -> None:
        """
        Start the bot with webhook mode.
        
        Args:
            webhook_url: URL for the webhook
            port: Port to listen on
            cert_path: Path to SSL certificate file
            key_path: Path to SSL private key file
        """
        if not self.application:
            raise RuntimeError("Application not built. Call build() first.")
        
        try:
            logger.info(f"Starting bot with webhook: {webhook_url}")
            
            # Start with webhook
            await self.application.initialize()
            await self.application.start()
            
            # Set webhook
            await self.application.updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=self.token,
                webhook_url=f"{webhook_url}/{self.token}",
                cert=cert_path,
                key=key_path,
                drop_pending_updates=True
            )
            
            logger.info(f"Bot is running with webhook on port {port}")
            
            # Keep the bot running
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"Error during webhook setup: {e}")
            raise
        finally:
            # Cleanup
            await self.stop()
    
    async def stop(self) -> None:
        """Stop the bot gracefully."""
        if self.application:
            try:
                logger.info("Stopping bot...")
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Bot stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")
    
    def run_polling(self) -> None:
        """Run the bot in polling mode (synchronous wrapper)."""
        import asyncio
        
        try:
            if not self.application:
                self.build()
            
            # Run the async polling
            asyncio.run(self.start_polling())
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
            raise

def create_bot() -> ShopGenieBot:
    """
    Create and configure a ShopGenieBot instance.
    
    Returns:
        Configured ShopGenieBot instance
    """
    # Validate configuration
    config.validate()
    
    # Create bot
    bot = ShopGenieBot(config.TELEGRAM_BOT_TOKEN)
    bot.build()
    
    return bot