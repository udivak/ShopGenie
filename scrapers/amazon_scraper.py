"""
Amazon scraper implementation.
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
import re
from urllib.parse import urljoin, quote

from .base_scraper import BaseScraper, Product

logger = logging.getLogger(__name__)

class AmazonScraper(BaseScraper):
    """Amazon scraper implementation."""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.amazon.com",
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            }
        )
    
    async def search(self, query: str, max_results: int = 50) -> List[Product]:
        """
        Search for products on Amazon.
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        try:
            # Encode query for URL
            encoded_query = quote(query)
            search_url = f"{self.base_url}/s?k={encoded_query}&ref=nb_sb_noss"
            
            logger.info(f"Searching Amazon for: {query}")
            logger.debug(f"Search URL: {search_url}")
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers=self.headers
            ) as session:
                
                for attempt in range(3):
                    try:
                        if attempt > 0:
                            await asyncio.sleep(1.0)
                        
                        async with session.get(search_url) as response:
                            if response.status == 200:
                                html = await response.text()
                                return self._parse_search_results(html, max_results)
                            else:
                                logger.warning(f"HTTP {response.status} for Amazon search")
                                
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout on attempt {attempt + 1}")
                        if attempt == 2:
                            raise
                    except Exception as e:
                        logger.error(f"Error on attempt {attempt + 1}: {e}")
                        if attempt == 2:
                            raise
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to search Amazon: {e}")
            return []
    
    def _parse_search_results(self, html: str, max_results: int) -> List[Product]:
        """Parse search results from HTML."""
        products = []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Amazon product selectors
            product_elements = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            if not product_elements:
                # Fallback selector
                product_elements = soup.find_all('div', class_=re.compile(r's-result-item'))
            
            logger.debug(f"Found {len(product_elements)} product elements on Amazon")
            
            for element in product_elements[:max_results]:
                try:
                    product = self._parse_product(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Failed to parse product element: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(products)} products from Amazon")
            return products
            
        except Exception as e:
            logger.error(f"Failed to parse Amazon search results: {e}")
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
            
            # Extract title - Updated selectors for current Amazon structure
            # Method 1: Try data-cy="title-recipe" (most reliable)
            title_element = element.find(attrs={'data-cy': 'title-recipe'})
            if title_element:
                title = self._clean_text(title_element.get_text())
            
            # Method 2: Try h2 with updated class patterns
            if not title or title == "Unknown Item":
                title_element = element.find('h2', class_=re.compile(r'a-size-mini|a-size-base-plus'))
                if title_element:
                    title_link = title_element.find('a')
                    if title_link:
                        title = self._clean_text(title_link.get_text())
            
            # Method 3: Try finding product links directly
            if not title or title == "Unknown Item":
                all_links = element.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    if ('/dp/' in href or '/gp/' in href):
                        link_text = self._clean_text(link.get_text())
                        if link_text and len(link_text) > 15:  # Reasonable title length
                            title = link_text
                            break
            
            # Method 4: Fallback selectors
            if not title or title == "Unknown Item":
                title_selectors = [
                    'h2 a span',
                    'h2 span',
                    '[data-cy="title-recipe-link"]',
                    'a[href*="/dp/"]'
                ]
                for selector in title_selectors:
                    title_element = element.select_one(selector)
                    if title_element:
                        title = self._clean_text(title_element.get_text())
                        if title and len(title) > 5:
                            break
            
            # Extract price
            price_element = element.find('span', class_='a-price-whole')
            if price_element:
                fraction = element.find('span', class_='a-price-fraction')
                price_text = price_element.get_text().rstrip('.')  # Remove trailing dots
                if fraction:
                    fraction_text = fraction.get_text()
                    price_text += "." + fraction_text
                price = f"${price_text}"
            else:
                # Try alternative price selectors
                price_selectors = [
                    '.a-price .a-offscreen',
                    '.a-price-range',
                    'span[data-a-color="price"]'
                ]
                for selector in price_selectors:
                    price_element = element.select_one(selector)
                    if price_element:
                        price = self._clean_text(price_element.get_text())
                        break
            
            # Extract rating
            rating_element = element.find('span', class_='a-icon-alt')
            if rating_element:
                rating_text = rating_element.get_text()
                rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Extract review count as sales proxy
            reviews_element = element.find('a', class_='a-link-normal')
            if reviews_element and reviews_element.get_text():
                review_text = reviews_element.get_text()
                sales_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
                if sales_match:
                    sales = int(sales_match.group(1))
            
            # Extract image URL
            img_element = element.find('img', class_='s-image')
            if img_element:
                image_url = img_element.get('src') or img_element.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
            
            # Extract product URL - Updated for current Amazon structure
            # First try to find product links directly
            all_links = element.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                if href and ('/dp/' in href or '/gp/' in href):
                    product_url = href
                    if not product_url.startswith('http'):
                        product_url = urljoin(self.base_url, product_url)
                    break
            
            # Fallback: try h2 elements with updated classes
            if not product_url:
                link_element = element.find('h2', class_=re.compile(r'a-size-mini|a-size-base-plus'))
                if link_element:
                    link = link_element.find('a')
                    if link:
                        product_url = link.get('href')
                        if product_url:
                            if not product_url.startswith('http'):
                                product_url = urljoin(self.base_url, product_url)
            
            # Validate that we have essential data
            if not title or title == "Unknown Item" or len(title) < 5:
                return None
            
            return Product(
                title=title,  # Use full title from Amazon
                price=price,
                rating=min(rating, 5.0),  # Cap rating at 5
                sales=sales,
                image_url=image_url or "",
                product_url=product_url or "",
                source="Amazon"
            )
            
        except Exception as e:
            logger.debug(f"Failed to parse Amazon product: {e}")
            return None