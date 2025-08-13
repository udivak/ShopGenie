"""
AliExpress Human-like Web Scraper
Designed to mimic human browsing behavior and avoid bot detection without requiring API credentials.
"""
import asyncio
import aiohttp
import random
import time
import json
import hashlib
from typing import List, Optional, Dict, Any
import logging
from urllib.parse import quote, urlencode
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re

from .base_scraper import BaseScraper, Product

logger = logging.getLogger(__name__)

@dataclass
class BrowserProfile:
    """Browser profile for mimicking different browsers"""
    user_agent: str
    sec_ch_ua: str
    sec_ch_ua_platform: str
    sec_ch_ua_mobile: str
    accept_language: str
    viewport_width: int
    viewport_height: int

class AliExpressHumanScraper(BaseScraper):
    """Human-like AliExpress web scraper implementation - no API credentials required."""
    
    def __init__(self):
        # Initialize with base configuration
        super().__init__(
            base_url="https://www.aliexpress.com",
            headers={}  # We'll set headers dynamically
        )
        
        # Browser profiles for rotation
        self.browser_profiles = self._init_browser_profiles()
        self.current_profile = None
        
        # Session management
        self.session = None
        self.cookies = {}
        self.request_count = 0
        self.last_request_time = 0
        
        # Rate limiting configuration - conservative to avoid detection
        self.min_delay = 3.0  # Minimum delay between requests (seconds)
        self.max_delay = 7.0  # Maximum delay between requests (seconds)
        self.requests_per_minute = 10  # Conservative rate limit
        
        # Search patterns to avoid detection
        self.search_endpoints = [
            "/w/wholesale-{query}.html",
            "/wholesale/{query}.html",
            "/af/{query}.html"
        ]
    
    def _init_browser_profiles(self) -> List[BrowserProfile]:
        """Initialize realistic browser profiles"""
        profiles = [
            # Chrome on Windows (most common)
            BrowserProfile(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                sec_ch_ua='"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                sec_ch_ua_platform='"Windows"',
                sec_ch_ua_mobile='?0',
                accept_language='en-US,en;q=0.9',
                viewport_width=1920,
                viewport_height=1080
            ),
            # Chrome on macOS
            BrowserProfile(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                sec_ch_ua='"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                sec_ch_ua_platform='"macOS"',
                sec_ch_ua_mobile='?0',
                accept_language='en-US,en;q=0.9',
                viewport_width=1440,
                viewport_height=900
            ),
            # Firefox on Windows
            BrowserProfile(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                sec_ch_ua='',  # Firefox doesn't send Sec-CH-UA headers
                sec_ch_ua_platform='',
                sec_ch_ua_mobile='',
                accept_language='en-US,en;q=0.5',
                viewport_width=1920,
                viewport_height=1080
            ),
            # Chrome on Android
            BrowserProfile(
                user_agent='Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                sec_ch_ua='"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                sec_ch_ua_platform='"Android"',
                sec_ch_ua_mobile='?1',
                accept_language='en-US,en;q=0.9',
                viewport_width=412,
                viewport_height=915
            ),
            # Safari on macOS
            BrowserProfile(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                sec_ch_ua='',  # Safari doesn't send Sec-CH-UA headers
                sec_ch_ua_platform='',
                sec_ch_ua_mobile='',
                accept_language='en-US,en;q=0.9',
                viewport_width=1440,
                viewport_height=900
            )
        ]
        return profiles
    
    def _select_browser_profile(self) -> BrowserProfile:
        """Select a random browser profile or rotate"""
        if not self.current_profile:
            self.current_profile = random.choice(self.browser_profiles)
        else:
            # Occasionally change profile (15% chance) to avoid detection
            if random.random() < 0.15:
                self.current_profile = random.choice(self.browser_profiles)
        
        return self.current_profile
    
    def _generate_headers(self, profile: BrowserProfile, referer: str = None, is_navigation: bool = True) -> Dict[str, str]:
        """Generate realistic HTTP headers for the request"""
        headers = {
            'User-Agent': profile.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': profile.accept_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        # Add Sec-Fetch headers for navigation requests (critical for bot detection bypass)
        if is_navigation:
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin' if referer and 'aliexpress.com' in referer else 'cross-site',
                'Sec-Fetch-User': '?1'
            })
        
        # Add Chrome-specific headers
        if 'Chrome' in profile.user_agent and profile.sec_ch_ua:
            headers.update({
                'Sec-CH-UA': profile.sec_ch_ua,
                'Sec-CH-UA-Mobile': profile.sec_ch_ua_mobile,
                'Sec-CH-UA-Platform': profile.sec_ch_ua_platform
            })
        
        # Add referer if provided
        if referer:
            headers['Referer'] = referer
        
        return headers
    
    async def _wait_for_rate_limit(self):
        """Implement intelligent rate limiting to mimic human behavior"""
        current_time = time.time()
        
        # Calculate delay based on recent request pattern
        if self.last_request_time > 0:
            time_since_last = current_time - self.last_request_time
            min_interval = 60.0 / self.requests_per_minute
            
            if time_since_last < min_interval:
                delay = min_interval - time_since_last
                # Add random jitter to avoid detection
                delay += random.uniform(0, 3.0)
                logger.debug(f"Rate limiting: waiting {delay:.2f} seconds")
                await asyncio.sleep(delay)
        
        # Add random delay to mimic human behavior
        human_delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(human_delay)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create an HTTP session with realistic configuration"""
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=10
        )
        
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=2,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        return aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            trust_env=True
        )
    
    async def _make_request(self, url: str, referer: str = None, is_navigation: bool = True) -> Optional[str]:
        """Make a human-like HTTP request"""
        await self._wait_for_rate_limit()
        
        profile = self._select_browser_profile()
        headers = self._generate_headers(profile, referer, is_navigation)
        
        if not self.session:
            self.session = await self._create_session()
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Update cookies
                    try:
                        for cookie in response.cookies:
                            if hasattr(cookie, 'key') and hasattr(cookie, 'value'):
                                self.cookies[cookie.key] = cookie.value
                    except Exception as e:
                        logger.debug(f"Cookie handling error: {e}")
                        # Continue without cookies if there's an issue
                    
                    return content
                elif response.status == 429:
                    # Rate limited - wait longer and change profile
                    logger.warning("Rate limited, waiting longer and changing profile")
                    self.current_profile = None  # Force profile change
                    await asyncio.sleep(random.uniform(15, 30))
                    return None
                elif response.status in [403, 406]:
                    # Blocked - change profile and retry
                    logger.warning(f"Blocked with status {response.status}, changing browser profile")
                    self.current_profile = None
                    await asyncio.sleep(random.uniform(10, 20))
                    return None
                else:
                    logger.warning(f"HTTP {response.status} for URL: {url}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning(f"Timeout for URL: {url}")
            return None
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def _build_search_url(self, query: str, page: int = 1, sort_by: str = 'default') -> str:
        """Build a realistic search URL"""
        # URL encode the query
        encoded_query = quote(query.replace(' ', '-'))
        
        # Select a random search endpoint pattern
        endpoint_pattern = random.choice(self.search_endpoints)
        endpoint = endpoint_pattern.format(query=encoded_query)
        
        # Build query parameters
        params = {
            'g': 'y',  # Required parameter
            'SearchText': query,
            'page': page,
        }
        
        # Add sorting if specified
        if sort_by != 'default':
            sort_mapping = {
                'price_low': 'price_asc',
                'price_high': 'price_desc',
                'orders': 'orders_desc',
                'rating': 'rating_desc'
            }
            if sort_by in sort_mapping:
                params['sortType'] = sort_mapping[sort_by]
        
        # Add random tracking parameters to look more human
        params.update({
            'spm': f'a2g0o.productlist.{random.randint(1000, 9999)}.{random.randint(1, 99)}',
            'algo_pvid': hashlib.md5(f"{query}{time.time()}".encode()).hexdigest()[:16],
            'algo_exp_id': random.randint(10000, 99999)
        })
        
        url = f"{self.base_url}{endpoint}"
        if params:
            url += '?' + urlencode(params)
        
        return url
    
    def _parse_search_results(self, html: str, max_results: int) -> List[Product]:
        """Parse search results from HTML"""
        products = []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Debug: Check if we got a valid HTML response
            if len(html) < 1000:
                logger.warning(f"HTML response too short ({len(html)} chars), might be blocked or redirected")
                return []
            
            # Multiple selectors to handle different page layouts
            product_selectors = [
                'div[data-item-id]',
                '.item-wrap',
                '.product-item',
                '.list-item',
                'div.item',
                '.list--gallery--C2f2tvm',  # Common AliExpress class
                '[data-product-id]'
            ]
            
            product_elements = []
            for selector in product_selectors:
                elements = soup.select(selector)
                if elements:
                    product_elements = elements
                    logger.debug(f"Found {len(elements)} products using selector: {selector}")
                    break
            
            if not product_elements:
                logger.warning("No product elements found - page structure may have changed")
                # Debug: Save HTML to see what we're getting
                try:
                    with open(f"debug_aliexpress_{int(time.time())}.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    logger.debug(f"Saved debug HTML to see page structure")
                except Exception as e:
                    logger.debug(f"Could not save debug HTML: {e}")
                return []
            
            logger.debug(f"Found {len(product_elements)} product elements")
            
            for element in product_elements[:max_results]:
                try:
                    product = self._parse_product_element(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Failed to parse product element: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(products)} products from AliExpress")
            return products
            
        except Exception as e:
            logger.error(f"Failed to parse search results: {e}")
            return []
    
    def _parse_product(self, element) -> Optional[Product]:
        """
        Parse a single product element from the page.
        Required implementation of abstract method from BaseScraper.
        
        Args:
            element: HTML element containing product data
            
        Returns:
            Product object or None if parsing fails
        """
        return self._parse_product_element(element)
    
    def _parse_product_element(self, element) -> Optional[Product]:
        """Parse a single product element from HTML"""
        try:
            # Extract title
            title_selectors = [
                'a[title]',
                '.item-title a',
                '.product-title',
                'h3 a',
                '.title a',
                '.product-title a',
                '[data-title]'
            ]
            
            title = None
            product_url = None
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get('title') or title_elem.get_text(strip=True)
                    product_url = title_elem.get('href')
                    break
            
            if not title:
                return None
            
            # Extract price
            price_selectors = [
                '.price .notranslate',
                '.price-current',
                '.product-price',
                '.price',
                '.notranslate',
                '.price-sale',
                '[data-price]'
            ]
            
            price = None
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract price number
                    price_match = re.search(r'[\d.,]+', price_text)
                    if price_match:
                        price = f"${price_match.group()}"
                        break
            
            # Extract image URL
            image_selectors = [
                'img',
                '.item-img img',
                '.product-img img',
                '.image img'
            ]
            
            image_url = None
            for selector in image_selectors:
                img_elem = element.select_one(selector)
                if img_elem:
                    image_url = img_elem.get('src') or img_elem.get('data-src')
                    if image_url and image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    break
            
            # Extract rating and sales info
            rating = 0.0
            sales = 0
            
            # Rating
            rating_elem = element.select_one('.rate-num, .rating, .stars, .evaluate-rate')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Sales
            sales_elem = element.select_one('.trade, .orders, .sales, .volume')
            if sales_elem:
                sales_text = sales_elem.get_text(strip=True)
                sales_match = re.search(r'(\d+)', sales_text.replace(',', ''))
                if sales_match:
                    sales = int(sales_match.group(1))
            
            # Ensure we have essential data
            if not title or len(title) < 3:
                return None
            
            # Fix relative URLs
            if product_url and product_url.startswith('/'):
                product_url = self.base_url + product_url
            
            return Product(
                title=title,
                price=price or "Price not available",
                rating=rating,
                sales=sales,
                image_url=image_url or "",
                product_url=product_url or "",
                source="AliExpress"
            )
            
        except Exception as e:
            logger.debug(f"Failed to parse product element: {e}")
            return None
    
    async def search(self, query: str, max_results: int = 50) -> List[Product]:
        """
        Search for products on AliExpress using human-like web scraping.
        No API credentials required.
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        try:
            logger.info(f"Searching AliExpress for: {query} (human-like scraping)")
            
            # Start with homepage visit to establish session (human-like behavior)
            homepage_url = self.base_url
            logger.debug("Visiting homepage to establish session")
            await self._make_request(homepage_url)
            
            # Build search URL
            search_url = self._build_search_url(query)
            logger.debug(f"Search URL: {search_url}")
            
            # Make search request with homepage as referer
            html_content = await self._make_request(search_url, referer=homepage_url)
            
            if html_content:
                products = self._parse_search_results(html_content, max_results)
                return products
            else:
                logger.warning("Failed to get search results")
                return []
                
        except Exception as e:
            logger.error(f"Failed to search AliExpress: {e}")
            return []
        finally:
            # Close session when done
            if self.session:
                await self.session.close()
                self.session = None
    
    async def get_product_details(self, product_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed product information from product page.
        
        Args:
            product_url: AliExpress product URL
            
        Returns:
            Product details or None if not found
        """
        try:
            if not self.session:
                self.session = await self._create_session()
            
            # Make request to product page
            html_content = await self._make_request(product_url)
            
            if html_content:
                return self._parse_product_details(html_content)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get product details: {e}")
            return None
    
    def _parse_product_details(self, html: str) -> Optional[Dict[str, Any]]:
        """Parse detailed product information from product page HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            details = {}
            
            # Extract detailed product information
            # This would include specifications, detailed description, etc.
            # Implementation depends on specific requirements
            
            return details
            
        except Exception as e:
            logger.error(f"Failed to parse product details: {e}")
            return None

    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.session:
            asyncio.create_task(self.session.close()) 