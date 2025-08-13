"""
Configuration management for the ShopGenie Telegram bot.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the bot."""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Scraping Configuration
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', 3))
    DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', 1.0))
    
    # Search Configuration
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 50))
    TOP_RESULTS_COUNT = int(os.getenv('TOP_RESULTS_COUNT', 5))
    
    # User Agent for web scraping
    USER_AGENT = os.getenv('USER_AGENT', 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # Amazon Configuration (for reference - not used by scraper)
    # Amazon scraper uses hardcoded URLs for better reliability
    
    # AliExpress Open Platform API Configuration
    ALIEXPRESS_APP_KEY = os.getenv('ALIEXPRESS_APP_KEY')
    ALIEXPRESS_APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET')
    ALIEXPRESS_TRACKING_ID = os.getenv('ALIEXPRESS_TRACKING_ID')  # Optional: for affiliate tracking
    ALIEXPRESS_API_URL = os.getenv('ALIEXPRESS_API_URL', 'https://api-sg.aliexpress.com/sync')
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        # AliExpress API validation (optional - only if you want to use AliExpress)
        if cls.ALIEXPRESS_APP_KEY and not cls.ALIEXPRESS_APP_SECRET:
            raise ValueError("ALIEXPRESS_APP_SECRET is required when ALIEXPRESS_APP_KEY is set")
        
        return True

# Create a default config instance
config = Config()