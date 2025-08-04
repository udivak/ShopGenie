# 🛍️ ShopGenie - Telegram Bot for Amazon Product Search

A sophisticated Telegram bot that searches Amazon for products and returns the top 4 best-matched results with comprehensive product information including pricing, ratings, sales data, and direct purchase links.

## ✨ Features

- 🔍 **Smart Product Search**: Advanced web scraping of Amazon search results
- 🏆 **Intelligent Ranking**: Multi-factor scoring system based on price, rating, and sales
- 📱 **Rich Formatting**: Beautiful Telegram messages with markdown formatting
- 🖼️ **Product Images**: Thumbnail images for visual product identification
- ⭐ **Detailed Info**: Price, rating, sales count, and direct purchase links
- 🚀 **Fast & Reliable**: Asynchronous processing with retry mechanisms
- 🛡️ **Error Handling**: Graceful error handling with user-friendly messages
- 🔧 **Modular Design**: Extensible architecture for adding more e-commerce sources

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ShopGenie
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file and add your Telegram Bot Token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

### Creating a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the token provided by BotFather
5. Add the token to your `.env` file

## 📋 Configuration Options

All configuration is handled through environment variables in the `.env` file:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Your Telegram bot token |
| `REQUEST_TIMEOUT` | ❌ | 10 | Request timeout in seconds |
| `MAX_RETRY_ATTEMPTS` | ❌ | 3 | Maximum retry attempts for failed requests |
| `DELAY_BETWEEN_REQUESTS` | ❌ | 1.0 | Delay between requests in seconds |
| `MAX_SEARCH_RESULTS` | ❌ | 50 | Maximum search results to scrape |
| `TOP_RESULTS_COUNT` | ❌ | 5 | Number of top results to return |
| `USER_AGENT` | ❌ | Chrome UA | User agent string for web scraping |

## 🏗️ Project Structure

```
ShopGenie/
├── main.py                 # Entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
├── bot/                  # Telegram bot components
│   ├── __init__.py
│   ├── telegram_bot.py   # Main bot class
│   └── handlers.py       # Message handlers
├── scrapers/             # Web scraping components
│   ├── __init__.py
│   ├── base_scraper.py   # Abstract scraper interface
│   └── amazon_scraper.py      # Amazon implementation
└── utils/                # Utility functions
    ├── __init__.py
    ├── item_comparator.py # Product ranking logic
    └── formatter.py      # Message formatting
```

## 🎯 Usage

### Bot Commands

- `/start` - Welcome message and introduction
- `/help` - Show help information and usage examples

### Searching for Products

Simply send any product name or description to the bot:

**Examples:**
- `wireless headphones`
- `smartphone case iPhone 14`
- `laptop stand adjustable`
- `LED strip lights`

### Bot Response

For each search, the bot returns up to 5 products with:
- 📱 **Product Title** (linked to Amazon)
- 💰 **Price** (in original currency)
- ⭐ **Rating** (with star visualization)
- 📊 **Review Count** (formatted with K/M suffixes)
- 🏪 **Source** (Amazon)
- 🔗 **Direct Purchase Link**

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

## 🔧 Extending to Other E-commerce Sources

The modular design makes it easy to add more e-commerce platforms:

### 1. Create a New Scraper

```python
# scrapers/amazon_scraper.py
from .base_scraper import BaseScraper, Product

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://amazon.com")
    
    async def search(self, query: str, max_results: int = 10) -> List[Product]:
        # Implement Amazon-specific scraping logic
        pass
    
    def _parse_product(self, element) -> Optional[Product]:
        # Implement Amazon product parsing
        pass
```

### 2. Update the Bot Handlers

```python
# bot/handlers.py
from scrapers.amazon_scraper import AmazonScraper

class BotHandlers:
    def __init__(self):
        self.amazon_scraper = AmazonScraper()
        # ... rest of initialization
```

### 3. Modify Search Logic

```python
# Search Amazon for products
amazon_products = await self.amazon_scraper.search(query)
top_products = self.comparator.rank_products(amazon_products)
```

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
```bash
python main.py
```

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

- [ ] Support for more e-commerce platforms (AliExpress, eBay, etc.)
- [ ] Price tracking and alerts
- [ ] User preferences and favorites
- [ ] Advanced filtering options
- [ ] Product comparison features
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Cache optimization
- [ ] Machine learning-based ranking

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing library
- [aiohttp](https://docs.aiohttp.org/) - Asynchronous HTTP client
- [Amazon](https://amazon.com) - Product data source

---

**Happy Shopping with ShopGenie! 🛒✨**