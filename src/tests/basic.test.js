const { formatSearchResults, formatProduct } = require('../utils/formatter');
const { rateLimiter } = require('../utils/rateLimiter');

// Mock product data for testing
const mockProducts = [
  {
    title: 'Wireless Bluetooth Headphones',
    price: '$15.99 - $25.99',
    rating: '4.5/5',
    imageUrl: 'https://example.com/image1.jpg',
    productUrl: 'https://www.aliexpress.com/item/test1',
    source: 'AliExpress'
  },
  {
    title: 'Smart Phone Case',
    price: '$3.50 - $8.99',
    rating: '4.2/5',
    imageUrl: 'https://example.com/image2.jpg',
    productUrl: 'https://www.aliexpress.com/item/test2',
    source: 'AliExpress'
  }
];

describe('Formatter Tests', () => {
  test('formatSearchResults should format products correctly', () => {
    const result = formatSearchResults(mockProducts, 'headphones');
    
    expect(result).toContain('Search Results for "headphones"');
    expect(result).toContain('Found 2 products on AliExpress');
    expect(result).toContain('Wireless Bluetooth Headphones');
    expect(result).toContain('$15.99 - $25.99');
    expect(result).toContain('4.5/5');
  });

  test('formatSearchResults should handle empty results', () => {
    const result = formatSearchResults([], 'nonexistent');
    
    expect(result).toContain('No products found for "nonexistent"');
  });

  test('formatProduct should escape HTML characters', () => {
    const productWithHtml = {
      title: 'Product with <script>alert("xss")</script>',
      price: '$10.00',
      rating: '4.0/5',
      productUrl: 'https://example.com',
      source: 'AliExpress'
    };
    
    const result = formatProduct(productWithHtml, 1);
    
    expect(result).toContain('&lt;script&gt;alert("xss")&lt;/script&gt;');
    expect(result).not.toContain('<script>');
  });
});

describe('Rate Limiter Tests', () => {
  beforeEach(() => {
    // Clear rate limiter state before each test
    rateLimiter.requests.clear();
  });

  test('should allow requests within limit', () => {
    const userId = 'test-user-1';
    
    // Should allow first 10 requests
    for (let i = 0; i < 10; i++) {
      expect(rateLimiter.checkLimit(userId)).toBe(true);
    }
  });

  test('should block requests over limit', () => {
    const userId = 'test-user-2';
    
    // Make 10 requests (at limit)
    for (let i = 0; i < 10; i++) {
      rateLimiter.checkLimit(userId);
    }
    
    // 11th request should be blocked
    expect(rateLimiter.checkLimit(userId)).toBe(false);
  });

  test('should reset after time window', () => {
    const userId = 'test-user-3';
    
    // Make some requests
    rateLimiter.checkLimit(userId);
    rateLimiter.checkLimit(userId);
    
    // Mock time passing (1 minute + 1 second)
    const originalDateNow = Date.now;
    Date.now = jest.fn(() => originalDateNow() + 61000);
    
    // Should allow requests again
    expect(rateLimiter.checkLimit(userId)).toBe(true);
    
    // Restore original Date.now
    Date.now = originalDateNow;
  });
});

describe('Integration Tests', () => {
  test('should handle special characters in search queries', () => {
    const specialQuery = 'headphones & speakers (wireless)';
    const result = formatSearchResults(mockProducts, specialQuery);
    
    expect(result).toContain('Search Results for "headphones & speakers (wireless)"');
  });

  test('should format multiple products correctly', () => {
    const result = formatSearchResults(mockProducts, 'test');
    
    // Should contain both products
    expect(result).toContain('Wireless Bluetooth Headphones');
    expect(result).toContain('Smart Phone Case');
    expect(result).toContain('$15.99 - $25.99');
    expect(result).toContain('$3.50 - $8.99');
  });
}); 