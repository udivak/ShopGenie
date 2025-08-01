"""
AliExpress scraper implementation.
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
import re
from urllib.parse import urljoin, quote

from .base_scraper import BaseScraper, Product
from config import config

logger = logging.getLogger(__name__)

class AliExpressScraper(BaseScraper):
    """AliExpress scraper implementation."""
    
    def __init__(self):
        super().__init__(
            base_url=config.ALIEXPRESS_BASE_URL,
            headers={
                'User-Agent': config.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
    
    async def search(self, query: str, max_results: int = 10) -> List[Product]:
        """
        Search for products on AliExpress.
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        try:
            # Encode query for URL
            encoded_query = quote(query)
            search_url = f"{config.ALIEXPRESS_SEARCH_URL}?SearchText={encoded_query}&SortType=total_tranpro_desc"
            
            logger.info(f"Searching AliExpress for: {query}")
            logger.debug(f"Search URL: {search_url}")
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT),
                headers=self.headers
            ) as session:
                
                for attempt in range(config.MAX_RETRY_ATTEMPTS):
                    try:
                        await asyncio.sleep(config.DELAY_BETWEEN_REQUESTS)
                        
                        async with session.get(search_url) as response:
                            if response.status == 200:
                                html = await response.text()
                                return self._parse_search_results(html, max_results)
                            else:
                                logger.warning(f"HTTP {response.status} for AliExpress search")
                                
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout on attempt {attempt + 1}")
                        if attempt == config.MAX_RETRY_ATTEMPTS - 1:
                            raise
                    except Exception as e:
                        logger.error(f"Error on attempt {attempt + 1}: {e}")
                        if attempt == config.MAX_RETRY_ATTEMPTS - 1:
                            raise
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to search AliExpress: {e}")
            return []
    
    def _parse_search_results(self, html: str, max_results: int) -> List[Product]:
        """Parse search results from HTML."""
        products = []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Try different selectors as AliExpress structure may vary
            selectors = [
                'div[data-widget-cid="module_item_list_square"] div._1k5Jn',
                'div.list-item',
                'div.item',
                'div[data-widget-cid] div.item-info',
                'a[href*="/item/"]',
            ]
            
            product_elements = []
            for selector in selectors:
                product_elements = soup.select(selector)
                if product_elements:
                    logger.debug(f"Found {len(product_elements)} products with selector: {selector}")
                    break
            
            if not product_elements:
                # Fallback: look for any links containing "/item/"
                product_elements = soup.find_all('a', href=re.compile(r'/item/'))
                logger.debug(f"Fallback: Found {len(product_elements)} product links")
            
            for element in product_elements[:max_results]:
                try:
                    product = self._parse_product(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Failed to parse product element: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(products)} products from AliExpress")
            return products
            
        except Exception as e:
            logger.error(f"Failed to parse AliExpress search results: {e}")
            return []
    
    def _parse_product(self, element) -> Optional[Product]:
        """Parse a single product from HTML element."""
        try:
            # Initialize default values
            title = "Unknown Item"
            price = "N/A"
            rating = 0.0
            sales = 0
            image_url = ""
            product_url = ""
            
            # Extract title
            title_selectors = [
                'h3', 'h2', 'h1', '.item-title', 
                'a[title]', '[title]', '.title',
                'span.item-title-label'
            ]
            
            for selector in title_selectors:
                title_element = element.select_one(selector)
                if title_element:
                    title = self._clean_text(title_element.get('title') or title_element.get_text())
                    if title and len(title) > 5:  # Ensure meaningful title
                        break
            
            # Extract price
            price_selectors = [
                '.price', '.item-price', '.price-current',
                'span[class*="price"]', 'div[class*="price"]',
                'span.notranslate'
            ]
            
            for selector in price_selectors:
                price_element = element.select_one(selector)
                if price_element:
                    price_text = self._clean_text(price_element.get_text())
                    if price_text and ('$' in price_text or '€' in price_text or '£' in price_text):
                        price = price_text
                        break
            
            # Extract rating
            rating_selectors = [
                '.rate-star', '.rating', '.stars',
                '[data-rating]', '.item-rating'
            ]
            
            for selector in rating_selectors:
                rating_element = element.select_one(selector)
                if rating_element:
                    rating_text = rating_element.get('data-rating') or rating_element.get_text()
                    rating = self._extract_number(rating_text)
                    if rating > 0:
                        break
            
            # Extract sales/orders
            sales_selectors = [
                '.item-sales', '.sold', '.orders',
                'span[class*="sold"]', 'span[class*="order"]'
            ]
            
            for selector in sales_selectors:
                sales_element = element.select_one(selector)
                if sales_element:
                    sales_text = self._clean_text(sales_element.get_text())
                    sales = int(self._extract_number(sales_text))
                    if sales > 0:
                        break
            
            # Extract image URL
            img_element = element.find('img')
            if img_element:
                image_url = img_element.get('src') or img_element.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
            
            # Extract product URL
            link_element = element if element.name == 'a' else element.find('a')
            if link_element:
                product_url = link_element.get('href')
                if product_url and not product_url.startswith('http'):
                    product_url = urljoin(self.base_url, product_url)
            
            # Validate that we have essential data
            if not title or title == "Unknown Item" or not product_url:
                return None
            
            return Product(
                title=title[:100],  # Limit title length
                price=price,
                rating=min(rating, 5.0),  # Cap rating at 5
                sales=sales,
                image_url=image_url or "",
                product_url=product_url,
                source="AliExpress"
            )
            
        except Exception as e:
            logger.debug(f"Failed to parse product: {e}")
            return None