const { searchAliExpress } = require('../services/aliexpressService');
const { formatSearchResults } = require('../utils/formatter');
const { logger } = require('../utils/logger');
const { rateLimiter } = require('../utils/rateLimiter');

/**
 * Handle incoming search messages
 */
async function handleMessage(bot, msg) {
  const chatId = msg.chat.id;
  const query = msg.text.trim();
  const userId = msg.from.id;

  // Check rate limiting
  if (!rateLimiter.checkLimit(userId)) {
    await bot.sendMessage(chatId, '⚠️ Too many requests! Please wait a moment before searching again.');
    return;
  }

  // Send typing indicator
  await bot.sendChatAction(chatId, 'typing');

  try {
    logger.info(`Search query from user ${userId}: ${query}`);

    // Search AliExpress
    const results = await searchAliExpress(query);

    if (!results || results.length === 0) {
      await bot.sendMessage(chatId, 
        `🔍 No products found for "${query}"\n\nTry searching with different keywords or check your spelling.`
      );
      return;
    }

    // Format and send results
    const formattedMessage = formatSearchResults(results, query);
    
    // Send results in chunks if message is too long
    const maxLength = 4096;
    if (formattedMessage.length <= maxLength) {
      await bot.sendMessage(chatId, formattedMessage, { 
        parse_mode: 'HTML',
        disable_web_page_preview: false
      });
    } else {
      // Split into multiple messages
      const chunks = splitMessage(formattedMessage, maxLength);
      for (const chunk of chunks) {
        await bot.sendMessage(chatId, chunk, { 
          parse_mode: 'HTML',
          disable_web_page_preview: false
        });
      }
    }

  } catch (error) {
    logger.error('Error handling search message:', error);
    await bot.sendMessage(chatId, 
      '❌ Sorry, I encountered an error while searching. Please try again later.'
    );
  }
}

/**
 * Handle bot commands
 */
async function handleCommand(bot, msg) {
  const chatId = msg.chat.id;
  const command = msg.text.toLowerCase();

  switch (command) {
    case '/start':
      await bot.sendMessage(chatId, 
        `🎉 Welcome to ShopGenie! 🛍️\n\n` +
        `I can help you find products on AliExpress. Simply send me the name of any item you're looking for.\n\n` +
        `Examples:\n` +
        `• "wireless headphones"\n` +
        `• "phone case"\n` +
        `• "kitchen gadgets"\n\n` +
        `Use /help for more information.`
      );
      break;

    case '/help':
      await bot.sendMessage(chatId,
        `📖 ShopGenie Help\n\n` +
        `🔍 How to search:\n` +
        `Just send me the name of any product you want to find on AliExpress.\n\n` +
        `📋 Available commands:\n` +
        `/start - Start the bot\n` +
        `/help - Show this help message\n` +
        `/about - About ShopGenie\n\n` +
        `💡 Tips:\n` +
        `• Be specific with your search terms\n` +
        `• Use English keywords for better results\n` +
        `• I'll show you the top 4 best matches\n\n` +
        `⚠️ Note: I respect rate limits to ensure reliable service.`
      );
      break;

    case '/about':
      await bot.sendMessage(chatId,
        `🤖 About ShopGenie\n\n` +
        `ShopGenie is your personal shopping assistant that helps you find products on AliExpress.\n\n` +
        `✨ Features:\n` +
        `• Quick product search\n` +
        `• Price comparison\n` +
        `• Direct purchase links\n` +
        `• Product ratings and images\n\n` +
        `🔒 Privacy: I don't store your search queries or personal data.\n\n` +
        `Version: 1.0.0`
      );
      break;

    default:
      await bot.sendMessage(chatId, 
        `❓ Unknown command. Use /help to see available commands.`
      );
      break;
  }
}

/**
 * Split long messages into chunks
 */
function splitMessage(message, maxLength) {
  const chunks = [];
  let currentChunk = '';
  
  const lines = message.split('\n');
  
  for (const line of lines) {
    if ((currentChunk + line + '\n').length > maxLength) {
      if (currentChunk) {
        chunks.push(currentChunk.trim());
        currentChunk = '';
      }
      
      // If a single line is too long, split it
      if (line.length > maxLength) {
        const words = line.split(' ');
        let tempLine = '';
        
        for (const word of words) {
          if ((tempLine + word + ' ').length > maxLength) {
            if (tempLine) {
              chunks.push(tempLine.trim());
              tempLine = '';
            }
            tempLine = word + ' ';
          } else {
            tempLine += word + ' ';
          }
        }
        
        if (tempLine) {
          currentChunk = tempLine;
        }
      } else {
        currentChunk = line + '\n';
      }
    } else {
      currentChunk += line + '\n';
    }
  }
  
  if (currentChunk) {
    chunks.push(currentChunk.trim());
  }
  
  return chunks;
}

module.exports = {
  handleMessage,
  handleCommand
}; 