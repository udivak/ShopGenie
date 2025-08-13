# AliExpress Human-Like Scraper Guide

## Overview

The AliExpress Human-Like Scraper is designed to extract product data from AliExpress without requiring API credentials. It mimics real browser behavior to avoid bot detection and provides a reliable alternative to the official API.

## Key Features

### 🚫 No API Credentials Required
- Works without AliExpress Open Platform API keys
- No need to register for developer accounts
- Immediate setup and usage

### 🤖 Anti-Bot Detection
- **Browser Profile Rotation**: Switches between realistic browser profiles
- **Sec-Fetch Headers**: Includes modern browser security headers
- **Human-like Timing**: Random delays between requests
- **Session Management**: Maintains cookies and session state
- **Rate Limiting**: Conservative request patterns

### 🔄 Adaptive Behavior
- Automatically changes browser profiles when blocked
- Implements exponential backoff on errors
- Handles rate limiting gracefully
- Retries with different strategies

## How It Works

### 1. Browser Profile System
The scraper maintains multiple realistic browser profiles:

```python
@dataclass
class BrowserProfile:
    user_agent: str
    sec_ch_ua: str
    sec_ch_ua_platform: str
    sec_ch_ua_mobile: str
    accept_language: str
    viewport_width: int
    viewport_height: int
```

**Supported Browsers:**
- Chrome on Windows/macOS/Android
- Firefox on Windows/macOS
- Safari on macOS/iOS

### 2. HTTP Headers Strategy
Generates realistic headers that modern browsers send:

```python
headers = {
    'User-Agent': profile.user_agent,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': profile.accept_language,
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1'
}
```

### 3. Rate Limiting
Conservative rate limiting to avoid detection:
- **Minimum delay**: 3 seconds between requests
- **Maximum delay**: 7 seconds between requests
- **Rate limit**: 10 requests per minute
- **Random jitter**: Adds unpredictability

### 4. Session Management
- Maintains cookies across requests
- Establishes session with homepage visit
- Proper referer chain management

## Usage

### Basic Usage

```python
import asyncio
from scrapers.aliexpress_human_scraper import AliExpressHumanScraper

async def search_products():
    scraper = AliExpressHumanScraper()
    
    # Search for products
    products = await scraper.search("wireless headphones", max_results=10)
    
    for product in products:
        print(f"Title: {product.title}")
        print(f"Price: {product.price}")
        print(f"Rating: {product.rating}")
        print(f"Sales: {product.sales}")
        print(f"URL: {product.product_url}")
        print("-" * 50)

# Run the search
asyncio.run(search_products())
```

### Integration with Scraper Manager

```python
from scrapers.scraper_manager import ScraperManager

# Initialize with human-like scraping (default)
manager = ScraperManager(use_human_like_scraping=True)

# Search AliExpress
products = await manager.search("aliexpress", "phone case", max_results=5)
```

## Configuration

### Rate Limiting Settings
You can adjust the rate limiting behavior:

```python
scraper = AliExpressHumanScraper()

# Modify rate limiting (be careful not to be too aggressive)
scraper.min_delay = 2.0  # Minimum delay between requests
scraper.max_delay = 5.0  # Maximum delay between requests
scraper.requests_per_minute = 15  # Rate limit
```

### Browser Profile Selection
The scraper automatically rotates browser profiles, but you can influence the selection:

```python
# Force a specific profile (not recommended for production)
scraper.current_profile = scraper.browser_profiles[0]  # Chrome on Windows
```

## Error Handling

### Common Error Responses

| Status Code | Meaning | Action Taken |
|-------------|---------|--------------|
| 200 | Success | Continue normally |
| 429 | Rate Limited | Wait 15-30 seconds, change profile |
| 403 | Forbidden | Change browser profile, retry |
| 406 | Not Acceptable | Change browser profile, retry |
| 500+ | Server Error | Log and continue |

### Adaptive Behavior
The scraper automatically adapts to blocking:

```python
elif response.status in [403, 406]:
    logger.warning(f"Blocked with status {response.status}, changing browser profile")
    self.current_profile = None  # Force profile change
    await asyncio.sleep(random.uniform(10, 20))
    return None
```

## Best Practices

### 1. Respectful Scraping
- Don't exceed recommended rate limits
- Use the scraper responsibly
- Consider the impact on AliExpress servers

### 2. Error Handling
- Always handle exceptions gracefully
- Implement retry logic in your application
- Monitor for blocking patterns

### 3. Data Validation
- Validate extracted data before using
- Handle missing or malformed data
- Implement fallback strategies

### 4. Monitoring
- Log scraping activities
- Monitor success rates
- Track blocking incidents

## Limitations

### 1. Rate Limiting
- Conservative rate limits to avoid detection
- May be slower than API-based solutions
- Requires patience for large datasets

### 2. Page Structure Changes
- AliExpress may change their HTML structure
- CSS selectors may need updates
- Requires maintenance over time

### 3. Blocking Risk
- Still possible to get blocked if used aggressively
- Requires careful rate limiting
- May need proxy rotation for heavy usage

## Troubleshooting

### Common Issues

#### 1. No Products Found
```python
# Check if page structure has changed
logger.debug("No product elements found - page structure may have changed")
```

**Solutions:**
- Update CSS selectors
- Check if AliExpress changed their layout
- Verify the search URL is correct

#### 2. Rate Limited
```python
# The scraper handles this automatically
logger.warning("Rate limited, waiting longer and changing profile")
```

**Solutions:**
- Wait for the automatic retry
- Reduce request frequency
- Consider using proxies

#### 3. Blocked Requests
```python
# The scraper changes profiles automatically
logger.warning(f"Blocked with status {response.status}, changing browser profile")
```

**Solutions:**
- Let the scraper handle profile rotation
- Wait for automatic retry
- Consider changing IP address

### Debug Mode
Enable debug logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

### Test Script
Use the provided test script to verify functionality:

```bash
python test_human_scraper.py
```

### Manual Testing
Test with different search queries:
- Simple terms: "phone case"
- Complex terms: "wireless bluetooth headphones"
- Special characters: "USB-C cable"

## Security Considerations

### 1. Ethical Usage
- Respect robots.txt (where applicable)
- Don't overload servers
- Use data responsibly

### 2. Legal Compliance
- Check AliExpress terms of service
- Ensure compliance with local laws
- Respect intellectual property rights

### 3. Data Privacy
- Don't store personal information
- Implement data retention policies
- Secure any cached data

## Performance Tips

### 1. Optimize Requests
- Use appropriate `max_results` values
- Implement caching where possible
- Batch requests when appropriate

### 2. Error Recovery
- Implement exponential backoff
- Use circuit breaker patterns
- Monitor and alert on failures

### 3. Resource Management
- Close sessions properly
- Monitor memory usage
- Implement connection pooling

## Future Enhancements

### Planned Features
1. **Proxy Support**: Rotate IP addresses
2. **Advanced Fingerprinting**: Canvas and WebGL fingerprinting
3. **Machine Learning**: Optimize request patterns
4. **CAPTCHA Solving**: Integrate CAPTCHA solving services
5. **Mobile App Simulation**: Mimic mobile app API calls

### Contributing
To contribute improvements:
1. Test thoroughly with different scenarios
2. Maintain backward compatibility
3. Update documentation
4. Follow ethical scraping practices

## Conclusion

The AliExpress Human-Like Scraper provides a reliable way to extract product data without API credentials. By mimicking real browser behavior, it successfully bypasses most bot detection mechanisms while being respectful to AliExpress servers.

Remember to use this tool responsibly and in accordance with AliExpress terms of service and applicable laws. 