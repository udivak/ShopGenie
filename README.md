# ShopGenie - Telegram Bot for AliExpress Search

A powerful Telegram bot that helps users find products on AliExpress by searching for items and returning the top 4 best matches with prices, ratings, and direct purchase links.

## Features

- 🔍 **Smart Product Search**: Search AliExpress with any product name
- 📊 **Top 4 Results**: Get the best matches with detailed information
- 💰 **Price Information**: See product prices and price ranges
- ⭐ **Ratings**: View product ratings when available
- 🖼️ **Product Images**: Access product thumbnails
- 🔗 **Direct Links**: Click to go directly to AliExpress product pages
- ⚡ **Rate Limiting**: Built-in protection against abuse
- 🛡️ **Error Handling**: Graceful handling of errors and edge cases
- 🔒 **Privacy Focused**: No user data storage

## Quick Start

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn
- Telegram Bot Token (see setup instructions below)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ShopGenie
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. **Start the bot**
   ```bash
   npm start
   ```

   For development with auto-restart:
   ```bash
   npm run dev
   ```

## Telegram Bot Setup

### Creating a Telegram Bot

1. **Start a chat with BotFather**
   - Open Telegram and search for `@BotFather`
   - Start a conversation with BotFather

2. **Create a new bot**
   - Send `/newbot` command
   - Follow the instructions to name your bot
   - Choose a username (must end with 'bot')

3. **Get your bot token**
   - BotFather will send you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - Copy this token and add it to your `.env` file

4. **Configure bot settings (optional)**
   - Use `/setdescription` to add a description
   - Use `/setabouttext` to add about text
   - Use `/setcommands` to set command list

### Bot Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information and available commands
- `/about` - Learn more about ShopGenie

## Usage

1. **Start the bot** by sending `/start`
2. **Search for products** by sending any product name
3. **View results** with prices, ratings, and direct links
4. **Click on product titles** to go to AliExpress

### Example Searches

- "wireless headphones"
- "phone case"
- "kitchen gadgets"
- "LED strip lights"
- "smart watch"

## Project Structure

```
ShopGenie/
├── src/
│   ├── index.js              # Main application entry point
│   ├── handlers/
│   │   └── messageHandler.js # Message and command handlers
│   ├── services/
│   │   └── aliexpressService.js # AliExpress search service
│   └── utils/
│       ├── formatter.js      # Message formatting utilities
│       ├── logger.js         # Logging utility
│       └── rateLimiter.js    # Rate limiting utility
├── package.json
├── env.example
└── README.md
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Required |
| `PORT` | Server port | 3000 |
| `NODE_ENV` | Environment (development/production) | development |
| `ALIEXPRESS_SEARCH_URL` | AliExpress search URL | https://www.aliexpress.com/wholesale |
| `USER_AGENT` | Browser user agent for requests | Chrome user agent |
| `MAX_REQUESTS_PER_MINUTE` | Rate limit per user | 10 |
| `REQUEST_DELAY_MS` | Delay between requests | 1000 |

## Deployment

### Local Development

```bash
npm run dev
```

### Production Deployment

#### Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token
   heroku config:set NODE_ENV=production
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

#### Railway

1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically

#### VPS/Cloud Server

1. **Clone and install**
   ```bash
   git clone <repository-url>
   cd ShopGenie
   npm install
   ```

2. **Set up environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Use PM2 for process management**
   ```bash
   npm install -g pm2
   pm2 start src/index.js --name shopgenie
   pm2 startup
   pm2 save
   ```

## Extending the Bot

### Adding New E-commerce Sources

The bot is designed to be easily extensible. To add support for other platforms:

1. **Create a new service** in `src/services/`
   ```javascript
   // src/services/amazonService.js
   async function searchAmazon(query) {
     // Implementation for Amazon search
   }
   ```

2. **Update the message handler** to use multiple sources
   ```javascript
   // In messageHandler.js
   const amazonResults = await searchAmazon(query);
   const aliexpressResults = await searchAliExpress(query);
   const allResults = [...amazonResults, ...aliexpressResults];
   ```

3. **Add source indicators** in the formatter
   ```javascript
   // In formatter.js
   formatted += `[${product.source}] `;
   ```

### Adding New Features

- **Product filtering**: Add price range, rating filters
- **Wishlist**: Save favorite products
- **Price alerts**: Notify when prices drop
- **Product comparisons**: Compare multiple products
- **Categories**: Browse by product categories

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the bot token is correct
   - Verify the bot is running without errors
   - Check server logs for issues

2. **No search results**
   - AliExpress may have changed their HTML structure
   - Check if the site is accessible
   - Try different search terms

3. **Rate limiting**
   - The bot respects rate limits to prevent abuse
   - Wait a minute before making another search

4. **Deployment issues**
   - Ensure all environment variables are set
   - Check if the port is available
   - Verify Node.js version compatibility

### Debug Mode

Enable debug logging by setting:
```
NODE_ENV=development
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational purposes. Please respect AliExpress's terms of service and rate limits. The bot uses web scraping which may be subject to changes in AliExpress's website structure.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the logs for error messages
- Open an issue on GitHub

---

**ShopGenie** - Your personal shopping assistant on Telegram! 🛍️ 