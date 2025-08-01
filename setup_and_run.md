# 🚀 ShopGenie Bot - Setup & Running Guide

This guide shows you how to set up, run, and test the ShopGenie Telegram bot.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install all required packages
pip3 install -r requirements.txt

# Or if you prefer pip
pip install -r requirements.txt
```

### 2. Configure Your Bot Token

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file and add your bot token
# You can use any text editor:
nano .env
# or
vim .env
# or
code .env
```

Add your token to the `.env` file:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 3. Create Your Telegram Bot

If you haven't created a bot yet:

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Choose a name: `ShopGenie Bot` (or any name you like)
4. Choose a username: `your_shopgenie_bot` (must end with `bot`)
5. Copy the token BotFather gives you
6. Paste it in your `.env` file

## 🧪 Testing the Bot

Before running the bot, test that everything works:

```bash
# Run the comprehensive test suite
python3 test_bot.py
```

This will test:
- ✅ Configuration loading
- ✅ Module imports
- ✅ Amazon scraper
- ✅ Product ranking system
- ✅ Message formatting
- ✅ Bot creation

**Expected output:**
```
🧪 ShopGenie Bot - Test Suite
==================================================
🔧 Testing Configuration...
✅ Telegram bot token is configured
✅ Request timeout: 10s
✅ Max retry attempts: 3

📦 Testing Module Imports...
✅ Bot modules imported successfully
✅ Bot instance created successfully

💬 Testing Message Formatter...
✅ Single product message formatted
✅ Search results message formatted

🏆 Testing Item Comparator...
   • Test Product 1: Score = 0.542
   • Test Product 2: Score = 0.651
   • Test Product 3: Score = 0.489

🔍 Testing Amazon Scraper with query: 'bluetooth headphones'...
✅ Found 3 products

📊 Test Results Summary
==============================
✅ PASS Configuration
✅ PASS Module Imports
✅ PASS Message Formatter
✅ PASS Item Comparator
✅ PASS Amazon Scraper

🎯 5/5 tests passed

🎉 All tests passed! Your bot is ready to run.
```

## 🚀 Running the Bot

### Option 1: Normal Mode (Production)

```bash
# Run the bot normally
python3 main.py
```

**Output:**
```
🤖 ShopGenie Bot is starting...
📱 Ready to help users find products on Amazon!
🔄 Running in polling mode...

Press Ctrl+C to stop the bot

2024-01-01 12:00:00 - Bot started successfully
2024-01-01 12:00:01 - Bot is running and polling for updates...
```

### Option 2: Development Mode with Auto-Reload

```bash
# Run with auto-reload (restarts when code changes)
python3 run_dev.py
```

**Output:**
```
🤖 ShopGenie Bot - Development Mode with Auto-Reload
============================================================
📁 Watching for file changes in:
   • *.py files in current directory
   • bot/ directory
   • scrapers/ directory
   • utils/ directory

🔄 Bot will auto-restart when files are modified
⏹️  Press Ctrl+C to stop

🚀 Bot started with PID: 12345
2024-01-01 12:00:00 - Bot started successfully
```

**When you edit a file:**
```
🔄 File changed: bot/handlers.py
♻️  Restarting bot...
🚀 Bot started with PID: 12346
```

## 🧪 Testing Your Live Bot

Once the bot is running, test it on Telegram:

### 1. Start a Chat with Your Bot
- Search for your bot username on Telegram
- Start a chat and send `/start`

**Expected response:**
```
🛍️ Welcome to ShopGenie Bot!

I help you find the best products on Amazon.

Just send me:
• Any product name or description
• I'll search and show you the top 4 results
• With prices, ratings, and direct purchase links

Example: Try typing "bluetooth speaker"

Type /help for more information.

Let's start shopping! 🛒
```

### 2. Test Product Search
Send a product name like: `wireless headphones`

**Expected response:**
```
🔍 Search Results for: wireless headphones
📦 Found 4 products

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛍️ 1. Wireless Bluetooth Headphones Gaming...

💰 Price: $25.99
⭐ Rating: 4.5/5 ⭐⭐⭐⭐⭐
📊 Sales: 1.2K
🏪 Source: Amazon

🔗 View Product

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3. Test Commands
- `/help` - Should show help information
- `/start` - Should show welcome message

## 🐛 Troubleshooting

### Bot Not Responding

1. **Check if bot is running:**
   ```bash
   # Should show running process
   ps aux | grep python3
   ```

2. **Check logs:**
   ```bash
   # Look at recent logs
   tail -f shopgenie_bot.log
   ```

3. **Verify token:**
   ```bash
   # Test your .env file is loaded correctly
   python3 -c "from config import config; print('Token set:', bool(config.TELEGRAM_BOT_TOKEN))"
   ```

### No Search Results

1. **Test network connectivity:**
   ```bash
   # Test if Amazon is accessible
curl -I https://www.amazon.com
   ```

2. **Run scraper test:**
   ```bash
   # Test scraper independently
   python3 -c "
   import asyncio
   from scrapers.amazon_scraper import AmazonScraper
   async def test():
       scraper = AmazonScraper()
       products = await scraper.search('test')
       print(f'Found {len(products)} products')
   asyncio.run(test())
   "
   ```

### Common Error Messages

**"No module named 'dotenv'":**
```bash
pip3 install python-dotenv
```

**"TELEGRAM_BOT_TOKEN environment variable is required":**
- Check your `.env` file exists
- Verify the token format is correct
- Make sure there are no extra spaces

**"HTTP 401 Unauthorized":**
- Your bot token is invalid
- Get a new token from @BotFather

## 🔧 Development Tips

### Auto-Reload Features
- 🔄 Automatically restarts when Python files change
- 📁 Watches all project directories
- ⚡ Fast development cycle

### Debugging
- 📊 Use `test_bot.py` to test individual components
- 📝 Check `shopgenie_bot.log` for detailed logs
- 🔍 Set logging level to DEBUG in `main.py` for verbose output

### Code Changes
1. Edit any Python file
2. Save the file
3. Bot automatically restarts with new code
4. Test immediately on Telegram

## 🚀 Production Deployment

For production, use the normal mode:
```bash
# Production
python3 main.py

# Or with process management
nohup python3 main.py > bot.log 2>&1 &
```

Consider using:
- **PM2** for process management
- **Docker** for containerization
- **Cloud services** (Heroku, AWS, etc.)

## 📝 Next Steps

1. ✅ Get your bot running locally
2. ✅ Test all functionality
3. ✅ Deploy to production
4. 🛍️ Start helping users find products!

**Happy coding! 🎉**