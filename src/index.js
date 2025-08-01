require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const cors = require('cors');
const { handleMessage, handleCommand } = require('./handlers/messageHandler');
const { logger } = require('./utils/logger');

// Initialize Express app for webhook (optional)
const app = express();
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Initialize Telegram Bot
const bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, {
  polling: process.env.NODE_ENV === 'development' ? true : false
});

// Handle incoming messages
bot.on('message', async (msg) => {
  try {
    const chatId = msg.chat.id;
    const text = msg.text;

    if (!text) {
      return;
    }

    // Handle commands
    if (text.startsWith('/')) {
      await handleCommand(bot, msg);
    } else {
      // Handle search queries
      await handleMessage(bot, msg);
    }
  } catch (error) {
    logger.error('Error handling message:', error);
    try {
      await bot.sendMessage(msg.chat.id, 'Sorry, something went wrong. Please try again later.');
    } catch (sendError) {
      logger.error('Error sending error message:', sendError);
    }
  }
});

// Handle bot errors
bot.on('error', (error) => {
  logger.error('Bot error:', error);
});

bot.on('polling_error', (error) => {
  logger.error('Polling error:', error);
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  logger.info(`Server is running on port ${PORT}`);
  logger.info('Telegram bot is ready!');
});

// Graceful shutdown
process.on('SIGINT', () => {
  logger.info('Shutting down gracefully...');
  bot.stopPolling();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Shutting down gracefully...');
  bot.stopPolling();
  process.exit(0);
}); 