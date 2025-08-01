const axios = require('axios');
const cheerio = require('cheerio');
const { logger } = require('../utils/logger');

/**
 * Search AliExpress for products
 */
async function searchAliExpress(query) {
  try {
    logger.info(`Searching AliExpress for: ${query}`);
    
    // Construct search URL
    const searchUrl = buildSearchUrl(query);
    
    // Make request with proper headers
    const response = await axios.get(searchUrl, {
      headers: {
        'User-Agent': process.env.USER_AGENT || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
      },
      timeout: 10000
    });

    // Parse HTML response
    const $ = cheerio.load(response.data);
    
    // Extract product information
    const products = extractProducts($);
    
    logger.info(`Found ${products.length} products for query: ${query}`);
    return products.slice(0, 4); // Return top 4 results
    
  } catch (error) {
    logger.error('Error searching AliExpress:', error.message);
    
    // Return mock data for development/testing
    if (process.env.NODE_ENV === 'development') {
      return getMockProducts(query);
    }
    
    throw new Error('Failed to search AliExpress. Please try again later.');
  }
}

/**
 * Build search URL for AliExpress
 */
function buildSearchUrl(query) {
  const baseUrl = process.env.ALIEXPRESS_SEARCH_URL || 'https://www.aliexpress.com/wholesale';
  const encodedQuery = encodeURIComponent(query);
  return `${baseUrl}?SearchText=${encodedQuery}&SortType=total_tranpro_desc`;
}

/**
 * Extract product information from HTML
 */
function extractProducts($) {
  const products = [];
  
  try {
    // Try multiple selectors as AliExpress structure may change
    const productSelectors = [
      '.list-item',
      '.product-item',
      '[data-product-id]',
      '.JIIxO'
    ];
    
    let productElements = null;
    
    for (const selector of productSelectors) {
      productElements = $(selector);
      if (productElements.length > 0) {
        logger.info(`Found products using selector: ${selector}`);
        break;
      }
    }
    
    if (!productElements || productElements.length === 0) {
      logger.warn('No product elements found with any selector');
      return getMockProducts('default');
    }
    
    productElements.each((index, element) => {
      if (index >= 4) return; // Limit to 4 products
      
      try {
        const $element = $(element);
        
        // Extract product information
        const title = extractTitle($element);
        const price = extractPrice($element);
        const rating = extractRating($element);
        const imageUrl = extractImageUrl($element);
        const productUrl = extractProductUrl($element);
        
        if (title && price) {
          products.push({
            title: title.trim(),
            price: price.trim(),
            rating: rating || 'N/A',
            imageUrl: imageUrl || '',
            productUrl: productUrl || '',
            source: 'AliExpress'
          });
        }
      } catch (error) {
        logger.error('Error extracting product data:', error.message);
      }
    });
    
  } catch (error) {
    logger.error('Error parsing AliExpress HTML:', error.message);
  }
  
  return products;
}

/**
 * Extract product title
 */
function extractTitle($element) {
  const titleSelectors = [
    '.item-title',
    '.product-title',
    'h3',
    '.title',
    '[title]'
  ];
  
  for (const selector of titleSelectors) {
    const title = $element.find(selector).first().text() || $element.find(selector).first().attr('title');
    if (title && title.trim()) {
      return title;
    }
  }
  
  return null;
}

/**
 * Extract product price
 */
function extractPrice($element) {
  const priceSelectors = [
    '.price-current',
    '.price',
    '.item-price',
    '[data-price]'
  ];
  
  for (const selector of priceSelectors) {
    const price = $element.find(selector).first().text();
    if (price && price.trim()) {
      return price;
    }
  }
  
  return null;
}

/**
 * Extract product rating
 */
function extractRating($element) {
  const ratingSelectors = [
    '.rating',
    '.stars',
    '[data-rating]'
  ];
  
  for (const selector of ratingSelectors) {
    const rating = $element.find(selector).first().text();
    if (rating && rating.trim()) {
      return rating;
    }
  }
  
  return null;
}

/**
 * Extract product image URL
 */
function extractImageUrl($element) {
  const imgSelectors = [
    'img[src]',
    'img[data-src]',
    '.product-image img'
  ];
  
  for (const selector of imgSelectors) {
    const img = $element.find(selector).first();
    const src = img.attr('src') || img.attr('data-src');
    if (src && src.trim()) {
      return src.startsWith('http') ? src : `https:${src}`;
    }
  }
  
  return null;
}

/**
 * Extract product URL
 */
function extractProductUrl($element) {
  const linkSelectors = [
    'a[href]',
    '.product-link',
    '.item-link'
  ];
  
  for (const selector of linkSelectors) {
    const link = $element.find(selector).first();
    const href = link.attr('href');
    if (href && href.trim()) {
      return href.startsWith('http') ? href : `https://www.aliexpress.com${href}`;
    }
  }
  
  return null;
}

/**
 * Get mock products for development/testing
 */
function getMockProducts(query) {
  return [
    {
      title: `Wireless Bluetooth Headphones - ${query}`,
      price: '$15.99 - $25.99',
      rating: '4.5/5',
      imageUrl: 'https://via.placeholder.com/150x150?text=Headphones',
      productUrl: 'https://www.aliexpress.com/item/mock1',
      source: 'AliExpress'
    },
    {
      title: `Smart Phone Case for ${query}`,
      price: '$3.50 - $8.99',
      rating: '4.2/5',
      imageUrl: 'https://via.placeholder.com/150x150?text=Phone+Case',
      productUrl: 'https://www.aliexpress.com/item/mock2',
      source: 'AliExpress'
    },
    {
      title: `LED Strip Lights - ${query} Collection`,
      price: '$12.99 - $18.50',
      rating: '4.7/5',
      imageUrl: 'https://via.placeholder.com/150x150?text=LED+Lights',
      productUrl: 'https://www.aliexpress.com/item/mock3',
      source: 'AliExpress'
    },
    {
      title: `Kitchen Gadgets Set - ${query} Style`,
      price: '$22.99 - $35.00',
      rating: '4.3/5',
      imageUrl: 'https://via.placeholder.com/150x150?text=Kitchen+Gadgets',
      productUrl: 'https://www.aliexpress.com/item/mock4',
      source: 'AliExpress'
    }
  ];
}

module.exports = {
  searchAliExpress
}; 