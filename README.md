# 🛍️ ShopGenie - Multi-Platform Shopping Telegram Bot

A sophisticated Telegram bot that searches multiple e-commerce platforms (Amazon & eBay) for products and returns the top-ranked results with comprehensive product information including pricing, ratings, sales data, and direct purchase links. Features intelligent search parsing, platform-specific optimizations, and robust error handling.

## ✨ Features

- 🛒 **Multi-Platform Support**: Search both Amazon and eBay with a single bot
- 🔍 **Smart Product Search**: Advanced web scraping with platform-specific optimizations
- 🛠️ **eBay API Integration**: Official eBay API support for reliable, fast searches (optional)
- 💬 **Flexible Input Parsing**: Multiple search formats (`item, platform` or `platform, item` or `item on platform`)
- 🏆 **Intelligent Ranking**: Multi-factor scoring system based on price, rating, and sales
- 📱 **Rich Formatting**: Beautiful Telegram messages with markdown formatting and product photos
- 🖼️ **Product Images**: High-quality product images with intelligent fallbacks
- ⭐ **Detailed Info**: Price, rating, sales count, platform, and direct purchase links
- 🚀 **Fast & Reliable**: Asynchronous processing with retry mechanisms and exponential backoff
- 🛡️ **Advanced Error Handling**: Platform status tracking with user-friendly error messages
- 🤖 **Anti-Bot Detection**: Intelligent handling of rate limiting and bot detection
- 🔧 **Modular Design**: Extensible scraper manager for adding more e-commerce platforms
- 🔄 **Development Mode**: Auto-reload functionality for seamless development

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

#### Automated Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ShopGenie
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure the bot:**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file and add your Telegram Bot Token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. **Activate the virtual environment:**
   ```bash
   source shopgenie_env/bin/activate
   ```

5. **Run the bot:**
   ```bash
   python main.py              # Production mode
   python run_dev.py           # Development mode with auto-reload
   ```

#### Manual Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd ShopGenie
   python3 -m venv shopgenie_env
   source shopgenie_env/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure and run (same as steps 3-5 above)**

### Creating a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the token provided by BotFather
5. Add the token to your `.env` file

### Setting Up eBay API (Optional but Recommended)

To get the best eBay search results, set up eBay developer credentials:

1. **Create an eBay Developer Account:**
   - Go to [eBay Developer Program](https://developer.ebay.com/)
   - Sign up for a developer account
   - Create a new application

2. **Get Your Credentials:**
   - Note down your **App ID**, **Cert ID**, and **Dev ID**
   - These will be provided in your eBay developer dashboard

3. **Configure Environment:**
   - Add the credentials to your `.env` file:
   ```
   EBAY_APP_ID=your_app_id_here
   EBAY_CERT_ID=your_cert_id_here
   EBAY_DEV_ID=your_dev_id_here
   EBAY_ENVIRONMENT=sandbox  # or production
   EBAY_SITE_ID=0  # 0 for US, 3 for UK, etc.
   ```

4. **Test the Setup:**
   ```bash
   python test_ebay_api.py
   ```

**Benefits of eBay API:**
- ✅ More reliable and faster searches
- ✅ Better structured data
- ✅ No anti-bot detection issues
- ✅ Access to detailed product information
- ✅ Higher rate limits

## 📋 Configuration Options

All configuration is handled through environment variables in the `.env` file:

### Required Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Your Telegram bot token |

### Optional Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REQUEST_TIMEOUT` | ❌ | 10 | Request timeout in seconds |
| `MAX_RETRY_ATTEMPTS` | ❌ | 3 | Maximum retry attempts for failed requests |
| `DELAY_BETWEEN_REQUESTS` | ❌ | 1.0 | Delay between requests in seconds |
| `MAX_SEARCH_RESULTS` | ❌ | 50 | Maximum search results to scrape |
| `TOP_RESULTS_COUNT` | ❌ | 5 | Number of top results to return |
| `USER_AGENT` | ❌ | Chrome UA | User agent string for web scraping |

### eBay API Configuration (Optional)

To enable eBay API-based searching (recommended), you need to set up eBay developer credentials:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EBAY_APP_ID` | ❌ | - | Your eBay application ID |
| `EBAY_CERT_ID` | ❌ | - | Your eBay certificate ID |
| `EBAY_DEV_ID` | ❌ | - | Your eBay developer ID |
| `EBAY_ENVIRONMENT` | ❌ | sandbox | API environment (sandbox/production) |
| `EBAY_SITE_ID` | ❌ | 0 | eBay site ID (0=US, 3=UK, etc.) |

**Note:** If eBay API credentials are not provided, the bot will fall back to web scraping for eBay searches.

## 🏗️ Project Structure

```
ShopGenie/
├── main.py                    # Main entry point
├── run_dev.py                 # Development mode with auto-reload
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
├── setup.sh                  # Automated setup script
├── test_bot.py               # Testing framework
├── README.md                 # This file
├── bot/                      # Telegram bot components
│   ├── __init__.py
│   ├── telegram_bot.py       # Main bot class and factory
│   └── handlers.py           # Message handlers and command processing
├── scrapers/                 # Web scraping components
│   ├── __init__.py
│   ├── base_scraper.py       # Abstract scraper interface
│   ├── scraper_manager.py    # Multi-platform scraper manager
│   ├── amazon_scraper.py     # Amazon implementation
│   └── ebay_scraper.py       # eBay implementation
└── utils/                    # Utility functions
    ├── __init__.py
    ├── item_comparator.py     # Product ranking and scoring logic
    ├── formatter.py           # Telegram message formatting
    ├── item_formatter.py      # General product formatting
    ├── message_parser.py      # Search query parsing
    └── platform_status.py    # Platform health tracking
```

## 🎯 Usage

### Bot Commands

- `/start` - Welcome message and introduction
- `/help` - Show help information and usage examples

### Searching for Products

The bot supports multiple flexible search formats. You **must** specify both the item and platform:

**Supported Formats:**
- `item name, platform`
- `platform, item name`
- `item name on platform`
- `item name from platform`

**Supported Platforms:**
- `amazon` (or `amazon.com`, `amzn`)
- `ebay` (or `ebay.com`, `bay`)

**Examples:**
- `wireless headphones, amazon`
- `ebay, smartphone case iPhone 14`
- `laptop stand on amazon`
- `LED strip lights from ebay`

### Bot Response

For each search, the bot returns up to 5 top-ranked products with:
- 🖼️ **Product Image** (when available)
- 📱 **Product Title** (cleaned and formatted)
- 💰 **Price** (in original currency)
- ⭐ **Rating** (with star visualization)
- 📊 **Sales/Reviews** (formatted with K/M suffixes)
- 🏪 **Platform** (Amazon or eBay)
- 🔗 **Direct Purchase Link**

### Error Handling

The bot provides intelligent error messages for:
- Platform availability issues
- Anti-bot detection responses
- Network connectivity problems
- Invalid search formats

## 🧠 Ranking Algorithm

The bot uses a sophisticated scoring system to rank products:

### Scoring Factors (Weighted)
- **Rating** (40%): Product rating on 0-5 scale
- **Reviews** (30%): Number of reviews (log-scaled)
- **Price** (30%): Lower prices score higher (inverse relationship)

### Ranking Methods
- `score`: Composite score (default)
- `price`: Lowest price first
- `rating`: Highest rating first
- `reviews`: Most reviews first

## 🔧 Extending to Other E-commerce Platforms

The modular design with `ScraperManager` makes it easy to add more e-commerce platforms:

### 1. Create a New Scraper

```python
# scrapers/new_platform_scraper.py
from .base_scraper import BaseScraper, Product
from typing import List, Optional

class NewPlatformScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://newplatform.com",
            headers={
                'User-Agent': 'Mozilla/5.0 ...',
                # Add platform-specific headers
            }
        )
    
    async def search(self, query: str, max_results: int = 50) -> List[Product]:
        # Implement platform-specific search logic
        search_url = f"{self.base_url}/search?q={query}"
        # ... scraping implementation
        pass
    
    def _parse_product(self, element) -> Optional[Product]:
        # Implement platform-specific product parsing
        return Product(
            title=title,
            price=price,
            rating=rating,
            sales=sales,
            image_url=image_url,
            product_url=product_url,
            source="NewPlatform"
        )
```

### 2. Register with ScraperManager

```python
# scrapers/scraper_manager.py
from .new_platform_scraper import NewPlatformScraper

class ScraperManager:
    def __init__(self):
        self._scrapers: Dict[str, BaseScraper] = {
            'amazon': AmazonScraper(),
            'ebay': EbayScraper(),
            'newplatform': NewPlatformScraper()  # Add your scraper
        }
        
        # Add aliases
        self._aliases = {
            # ... existing aliases
            'newplatform.com': 'newplatform',
            'np': 'newplatform'
        }
```

### 3. Update Platform Display Names

```python
# Add to scraper_manager.py get_platform_display_name method
display_names = {
    'amazon': 'Amazon',
    'ebay': 'eBay',
    'newplatform': 'NewPlatform'  # Add display name
}
```

### 4. Update Documentation

Update help messages in `utils/formatter.py` and `utils/message_parser.py` to include the new platform.

**That's it!** The `ScraperManager` automatically handles the new platform, and users can search with formats like:
- `headphones, newplatform`
- `newplatform, laptop`
- `phone case on newplatform`

## 🛡️ Security & Compliance

### Data Privacy
- ✅ No user queries or personal data are logged or stored
- ✅ Only essential operational logs are maintained
- ✅ No user tracking or analytics

### Rate Limiting
- ✅ Configurable delays between requests
- ✅ Retry mechanisms with exponential backoff
- ✅ Respect for Amazon ToS and rate limits

### Best Practices
- ✅ Proper user agent headers
- ✅ Graceful error handling
- ✅ Timeout controls
- ✅ Resource cleanup

## 🚀 Deployment Options

### Local Development

#### Production Mode
```bash
source shopgenie_env/bin/activate
python main.py
```

#### Development Mode (Recommended for Development)
```bash
source shopgenie_env/bin/activate
python run_dev.py
```

**Development Mode Features:**
- 🔄 **Auto-reload**: Automatically restarts the bot when you modify any `.py` files
- 📁 **File Watching**: Monitors `bot/`, `scrapers/`, `utils/` directories and root files
- 🛠️ **Development Friendly**: Faster iteration cycles for bot development
- 📊 **Process Management**: Graceful restart and cleanup of bot processes

#### Testing
```bash
source shopgenie_env/bin/activate
python test_bot.py
```

The test framework validates:
- Configuration loading
- Scraper functionality
- Message formatting
- Error handling

### Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Cloud Deployment

#### Heroku
1. Create a `Procfile`:
   ```
   worker: python main.py
   ```
2. Deploy using Heroku CLI or GitHub integration

#### AWS/GCP/Azure
- Use container services or serverless functions
- Set environment variables in the cloud console
- Ensure proper logging and monitoring

### Webhook Mode (Production)

For production deployments, consider using webhook mode instead of polling:

```python
# In main.py, replace polling with webhook
bot = create_bot()
await bot.start_webhook(
    webhook_url="https://yourdomain.com",
    port=8443
)
```

## 📊 Monitoring & Logging

### Log Files
- `shopgenie_bot.log` - Application logs with rotation
- Separate log levels for different components

### Metrics to Monitor
- Search success rate
- Response times
- Error rates
- User activity

### Health Checks
- Bot responsiveness
- Amazon accessibility
- Memory usage

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond:**
- ✅ Check if the bot token is correct
- ✅ Verify the bot is running (`python main.py`)
- ✅ Check network connectivity

**Search returns no results:**
- ✅ Try different search terms
- ✅ Check if Amazon is accessible
- ✅ Verify user agent and headers

**Frequent timeouts:**
- ✅ Increase `REQUEST_TIMEOUT` in configuration
- ✅ Reduce `MAX_SEARCH_RESULTS`
- ✅ Check network stability

**Rate limiting errors:**
- ✅ Increase `DELAY_BETWEEN_REQUESTS`
- ✅ Reduce request frequency
- ✅ Consider using proxy rotation

### Debug Mode

Enable debug logging by modifying `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Testing

Run a quick test search:
```python
# test_bot.py
import asyncio
from scrapers.amazon_scraper import AmazonScraper

async def test():
    scraper = AmazonScraper()
    products = await scraper.search("test product")
    print(f"Found {len(products)} products")

asyncio.run(test())
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

- 📧 **Issues**: Use GitHub Issues for bug reports and feature requests
- 💬 **Discussions**: Use GitHub Discussions for questions and ideas
- 📖 **Documentation**: Check this README and inline code comments

## 🔮 Future Enhancements

### Completed ✅
- ✅ Support for multiple e-commerce platforms (Amazon, eBay)
- ✅ Advanced error handling and platform status tracking
- ✅ Flexible message parsing with multiple input formats
- ✅ Development mode with auto-reload functionality
- ✅ Comprehensive testing framework
- ✅ Rich product formatting with images

### Planned 🔄
- [ ] Support for more e-commerce platforms (AliExpress, Walmart, Target)
- [ ] Price tracking and alerts
- [ ] User preferences and favorites
- [ ] Advanced filtering options (price range, rating, etc.)
- [ ] Product comparison features
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Cache optimization for faster repeated searches
- [ ] Machine learning-based ranking improvements
- [ ] Database integration for search history
- [ ] Web interface (FastAPI integration)
- [ ] Scheduled price monitoring
- [ ] Product availability notifications

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing library
- [aiohttp](https://docs.aiohttp.org/) - Asynchronous HTTP client
- [Amazon](https://amazon.com) - Product data source

---

**Happy Shopping with ShopGenie! 🛒✨**