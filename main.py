"""
ShopGenie Telegram Bot - Main Entry Point

A Telegram bot that searches Amazon for products and returns 
the top 4 best-matched results with pricing, ratings, and direct links.
"""
import sys
import logging
import asyncio
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bot.telegram_bot import create_bot
from config import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('shopgenie_bot.log')
    ]
)

# Set logging levels for specific modules
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.INFO)
logging.getLogger('aiohttp').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the ShopGenie bot."""
    try:
        logger.info("=" * 50)
        logger.info("Starting ShopGenie Telegram Bot")
        logger.info("=" * 50)
        
        # Validate configuration
        try:
            config.validate()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            print(f"\n❌ Configuration Error: {e}")
            print("\nPlease ensure you have:")
            print("1. Created a .env file in the project root")
            print("2. Added your Telegram bot token: TELEGRAM_BOT_TOKEN=your_token_here")
            print("3. Optionally configured other settings (see README.md)")
            return 1
        
        # Create and start bot
        try:
            bot = create_bot()
            logger.info("Bot created successfully")
            
            print("\n🤖 ShopGenie Bot is starting...")
            print("📱 Ready to help users find products on Amazon!")
            print("🔄 Running in polling mode...")
            print("\nPress Ctrl+C to stop the bot\n")
            
            # Start the bot
            bot.run_polling()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            print(f"\n❌ Failed to start bot: {e}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n\n👋 ShopGenie Bot stopped. Goodbye!")
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())