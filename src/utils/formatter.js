/**
 * Format search results into a Telegram message
 */
function formatSearchResults(results, query) {
  if (!results || results.length === 0) {
    return `🔍 No products found for "${query}"`;
  }

  let message = `🔍 Search Results for "${query}"\n\n`;
  message += `Found ${results.length} product${results.length > 1 ? 's' : ''} on AliExpress:\n\n`;

  results.forEach((product, index) => {
    message += formatProduct(product, index + 1);
  });

  message += `\n💡 Tip: Click on any product title to view it on AliExpress!`;
  
  return message;
}

/**
 * Format a single product
 */
function formatProduct(product, index) {
  let formatted = `${index}. `;
  
  // Product title as clickable link
  if (product.productUrl) {
    formatted += `<a href="${product.productUrl}">${escapeHtml(product.title)}</a>\n`;
  } else {
    formatted += `<b>${escapeHtml(product.title)}</b>\n`;
  }
  
  // Price
  if (product.price) {
    formatted += `💰 <b>Price:</b> ${escapeHtml(product.price)}\n`;
  }
  
  // Rating
  if (product.rating && product.rating !== 'N/A') {
    formatted += `⭐ <b>Rating:</b> ${escapeHtml(product.rating)}\n`;
  }
  
  // Image (if available)
  if (product.imageUrl) {
    formatted += `🖼️ <a href="${product.imageUrl}">View Image</a>\n`;
  }
  
  formatted += '\n';
  
  return formatted;
}

/**
 * Escape HTML special characters for Telegram
 */
function escapeHtml(text) {
  if (!text) return '';
  
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Format error message
 */
function formatErrorMessage(error) {
  return `❌ Error: ${escapeHtml(error.message || 'Unknown error occurred')}`;
}

/**
 * Format help message
 */
function formatHelpMessage() {
  return `📖 <b>ShopGenie Help</b>\n\n` +
         `🔍 <b>How to search:</b>\n` +
         `Just send me the name of any product you want to find on AliExpress.\n\n` +
         `📋 <b>Available commands:</b>\n` +
         `/start - Start the bot\n` +
         `/help - Show this help message\n` +
         `/about - About ShopGenie\n\n` +
         `💡 <b>Tips:</b>\n` +
         `• Be specific with your search terms\n` +
         `• Use English keywords for better results\n` +
         `• I'll show you the top 4 best matches\n\n` +
         `⚠️ Note: I respect rate limits to ensure reliable service.`;
}

/**
 * Format welcome message
 */
function formatWelcomeMessage() {
  return `🎉 <b>Welcome to ShopGenie!</b> 🛍️\n\n` +
         `I can help you find products on AliExpress. Simply send me the name of any item you're looking for.\n\n` +
         `<b>Examples:</b>\n` +
         `• "wireless headphones"\n` +
         `• "phone case"\n` +
         `• "kitchen gadgets"\n\n` +
         `Use /help for more information.`;
}

/**
 * Format about message
 */
function formatAboutMessage() {
  return `🤖 <b>About ShopGenie</b>\n\n` +
         `ShopGenie is your personal shopping assistant that helps you find products on AliExpress.\n\n` +
         `✨ <b>Features:</b>\n` +
         `• Quick product search\n` +
         `• Price comparison\n` +
         `• Direct purchase links\n` +
         `• Product ratings and images\n\n` +
         `🔒 <b>Privacy:</b> I don't store your search queries or personal data.\n\n` +
         `Version: 1.0.0`;
}

module.exports = {
  formatSearchResults,
  formatProduct,
  formatErrorMessage,
  formatHelpMessage,
  formatWelcomeMessage,
  formatAboutMessage
}; 