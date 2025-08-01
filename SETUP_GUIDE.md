# Quick Setup Guide - ShopGenie Telegram Bot

This is a quick start guide to get your ShopGenie bot running in minutes!

## 🚀 5-Minute Setup

### Step 1: Create Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "My ShopGenie")
4. Choose a username (must end with 'bot', e.g., "myshopgenie_bot")
5. **Copy the token** - you'll need this!

### Step 2: Set Up Project
```bash
# Clone and setup
git clone <your-repo-url>
cd ShopGenie
npm install

# Configure environment
cp env.example .env
```

### Step 3: Add Your Bot Token
Edit `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
NODE_ENV=development
```

### Step 4: Start the Bot
```bash
npm start
```

### Step 5: Test Your Bot
1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. Try searching: "wireless headphones"

## 🐳 Docker Setup (Alternative)

If you prefer Docker:

```bash
# Build and run with Docker
docker-compose up -d

# Check logs
docker-compose logs -f
```

## 📱 Bot Commands

- `/start` - Welcome message
- `/help` - Show help
- `/about` - About ShopGenie
- **Any product name** - Search AliExpress

## 🔧 Troubleshooting

### Bot not responding?
1. Check if the token is correct
2. Verify the bot is running: `npm start`
3. Check logs for errors

### No search results?
- Try different keywords
- Check internet connection
- AliExpress might be temporarily unavailable

### Rate limited?
- Wait 1 minute between searches
- This is normal protection

## 🌐 Deploy to Cloud

### Heroku (Recommended)
```bash
# Install Heroku CLI first
heroku create your-bot-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token
git push heroku main
```

### Railway
1. Connect GitHub repo
2. Add environment variables
3. Deploy automatically

## 📊 Features

✅ **Smart Search** - Find products on AliExpress  
✅ **Top 4 Results** - Best matches with details  
✅ **Price Info** - See prices and ranges  
✅ **Ratings** - Product ratings when available  
✅ **Direct Links** - Click to buy on AliExpress  
✅ **Rate Limiting** - Protection against abuse  
✅ **Error Handling** - Graceful error management  
✅ **Privacy Focused** - No data storage  

## 🎯 Example Searches

Try these searches:
- "wireless headphones"
- "phone case"
- "kitchen gadgets"
- "LED strip lights"
- "smart watch"

## 📞 Support

- Check the main README.md for detailed docs
- Review DEPLOYMENT.md for cloud deployment
- Open an issue on GitHub for bugs

---

**Happy shopping with ShopGenie! 🛍️** 