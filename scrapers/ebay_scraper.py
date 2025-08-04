"""
eBay scraper implementation.
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

class EbayScraper(BaseScraper):
    """eBay scraper implementation."""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.ebay.com",
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
        )
    
    async def search(self, query: str, max_results: int = 50) -> List[Product]:
        """
        Search for products on eBay.
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        try:
            # Encode query for URL
            encoded_query = quote(query)
            search_url = f"{self.base_url}/sch/i.html?_nkw={encoded_query}&_sacat=0&_ipg=60"
            
            logger.info(f"Searching eBay for: {query}")
            logger.debug(f"Search URL: {search_url}")
            
            # Add delays to avoid being flagged as bot
            await asyncio.sleep(2.0)
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers=self.headers
            ) as session:
                
                for attempt in range(3):
                    try:
                        if attempt > 0:
                            delay = 2.0 ** attempt  # Exponential backoff: 2s, 4s, 8s
                            logger.info(f"Waiting {delay}s before retry...")
                            await asyncio.sleep(delay)
                        
                        async with session.get(search_url) as response:
                            if response.status == 200:
                                html = await response.text()
                                
                                # Check if eBay is serving limited content
                                if 'bot' in html.lower() or len(html) < 100000:  # Normal eBay pages are much larger
                                    logger.warning("eBay may be serving limited content due to bot detection")
                                
                                products = self._parse_search_results(html, max_results)
                                
                                # If we get very few results, eBay might be limiting us
                                if len(products) == 0:
                                    logger.warning("eBay returned 0 products - possible anti-bot measures active")
                                    
                                return products
                            else:
                                logger.warning(f"HTTP {response.status} for eBay search")
                                
                    except asyncio.TimeoutError:
                        logger.warning(f"eBay request timeout on attempt {attempt + 1}")
                        if attempt == 2:
                            logger.error("eBay is not responding - service may be temporarily unavailable")
                            raise
                    except Exception as e:
                        logger.error(f"eBay error on attempt {attempt + 1}: {e}")
                        if attempt == 2:
                            raise
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to search eBay: {e}")
            return []
    
    def _parse_search_results(self, html: str, max_results: int) -> List[Product]:
        """Parse search results from HTML."""
        products = []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # eBay product selectors - try multiple patterns
            product_elements = soup.find_all('div', class_='s-item__wrapper')
            
            if not product_elements:
                # Fallback selectors in order of preference
                selectors = [
                    ('div', {'class': re.compile(r's-item__wrapper')}),
                    ('div', {'class': re.compile(r's-item')}),
                    ('div', {'data-view': 'mi:1686|iid:1'}),  # eBay item data
                    ('div', {'class': re.compile(r'item')}),
                    ('.s-item', None),  # CSS selector
                ]
                
                for selector_tag, selector_attrs in selectors:
                    if selector_attrs is None:
                        # CSS selector case
                        product_elements = soup.select(selector_tag)
                    else:
                        product_elements = soup.find_all(selector_tag, selector_attrs)
                    
                    if product_elements:
                        logger.debug(f"Found {len(product_elements)} elements using fallback selector: {selector_tag}")
                        break
            
            logger.debug(f"Found {len(product_elements)} product elements on eBay")
            
            for element in product_elements[:max_results]:
                try:
                    product = self._parse_product(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Failed to parse product element: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(products)} products from eBay")
            return products
            
        except Exception as e:
            logger.error(f"Failed to parse eBay search results: {e}")
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
            
            # Extract title - Multiple methods for better extraction
            title_methods = [
                # Method 1: Standard eBay title div with span
                lambda: element.find('div', class_='s-item__title'),
                # Method 2: Try h3 title elements
                lambda: element.find('h3', class_='s-item__title'),
                # Method 3: Try any link with title or text
                lambda: element.find('a', href=re.compile(r'/itm/')),
                # Method 4: Try data-testid selectors
                lambda: element.find('span', {'data-testid': 'item-title'}),
                # Method 5: Try any element with title-like classes
                lambda: element.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title')),
            ]
            
            for method in title_methods:
                try:
                    title_element = method()
                    if title_element:
                        # Try different text extraction approaches
                        text_sources = [
                            lambda: title_element.find('span', role='heading'),
                            lambda: title_element.find('span'),
                            lambda: title_element.find('a'),
                            lambda: title_element
                        ]
                        
                        for source_func in text_sources:
                            try:
                                source_elem = source_func()
                                if source_elem:
                                    extracted_text = self._clean_text(source_elem.get_text())
                                    if extracted_text and len(extracted_text) > 5:
                                        title = extracted_text
                                        logger.debug(f"Extracted title using method: {extracted_text}")
                                        break
                            except:
                                continue
                        
                        if title and len(title) > 5:
                            break
                except:
                    continue
            
            # If still no title, try extracting from any link in the element
            if not title or len(title) <= 5:
                all_links = element.find_all('a', href=True)
                for link in all_links:
                    link_text = self._clean_text(link.get_text())
                    if link_text and len(link_text) > 10:  # Reasonable title length
                        title = link_text
                        logger.debug(f"Extracted title from link: {title}")
                        break
            
            # Clean up common eBay title prefixes/suffixes
            if title:
                # Remove common prefixes
                prefixes_to_remove = ["New Listing", "SPONSORED", "Hot This Week"]
                for prefix in prefixes_to_remove:
                    if title.startswith(prefix):
                        title = title[len(prefix):].strip()
                
                # Remove trailing text like "| eBay"
                if "|" in title:
                    title = title.split("|")[0].strip()
                
                # Remove "Shop on eBay" suffix
                if title.endswith("Shop on eBay"):
                    title = title[:-12].strip()
            
            # Extract price
            price_element = element.find('span', class_='s-item__price')
            if price_element:
                price = self._clean_text(price_element.get_text())
                # Clean up price format
                if 'to' in price.lower():
                    # Handle price ranges - take the lower price
                    price_parts = price.split('to')
                    if len(price_parts) > 0:
                        price = price_parts[0].strip()
                # Remove shipping info
                if '+' in price:
                    price = price.split('+')[0].strip()
            
            # Extract rating (eBay uses different format)
            # Look for feedback score or seller rating
            rating_element = element.find('span', class_='s-item__reviews-count')
            if rating_element:
                rating_text = rating_element.get_text()
                # Extract number from text like "(123)" or "123 sold"
                rating_match = re.search(r'(\d+)', rating_text)
                if rating_match:
                    # Convert review count to a 1-5 rating scale
                    review_count = int(rating_match.group(1))
                    if review_count > 100:
                        rating = 5.0
                    elif review_count > 50:
                        rating = 4.5
                    elif review_count > 20:
                        rating = 4.0
                    elif review_count > 10:
                        rating = 3.5
                    elif review_count > 5:
                        rating = 3.0
                    else:
                        rating = 2.5
            
            # Extract sales count
            sold_element = element.find('span', class_='s-item__dynamic')
            if sold_element:
                sold_text = sold_element.get_text()
                sales_match = re.search(r'(\d+)\s*sold', sold_text)
                if sales_match:
                    sales = int(sales_match.group(1))
            
            # Extract image URL - Multiple methods for better image extraction
            img_element = element.find('img', class_='s-item__image')
            if img_element:
                # Try different image attributes in order of preference
                image_url = (
                    img_element.get('src') or 
                    img_element.get('data-src') or 
                    img_element.get('data-original') or
                    img_element.get('data-lazy')
                )
                
                # If still no image, try alternative selectors
                if not image_url:
                    alt_img_selectors = [
                        '.s-item__image img',
                        '.s-item__link img',
                        'img[src*="ebayimg"]'
                    ]
                    for selector in alt_img_selectors:
                        alt_img = element.select_one(selector)
                        if alt_img:
                            image_url = (
                                alt_img.get('src') or 
                                alt_img.get('data-src') or 
                                alt_img.get('data-original')
                            )
                            if image_url:
                                break
                
                # Clean up and validate image URL
                if image_url:
                    # Remove any query parameters that might cause issues
                    if '?' in image_url:
                        image_url = image_url.split('?')[0]
                    
                    # Ensure proper URL format
                    if not image_url.startswith('http'):
                        image_url = urljoin(self.base_url, image_url)
                    
                    # Replace small images with larger ones if possible
                    if 's-l' in image_url:
                        # Try to get larger image by replacing size parameter
                        image_url = image_url.replace('s-l64', 's-l300').replace('s-l140', 's-l300')
            
            # Extract product URL
            link_element = element.find('a', class_='s-item__link')
            if link_element:
                product_url = link_element.get('href')
                if product_url and not product_url.startswith('http'):
                    product_url = urljoin(self.base_url, product_url)
            
            # Filter out non-product elements and validate essential data
            if not title or title == "Unknown Item" or len(title) < 5:
                logger.debug(f"Rejected product: invalid title - '{title}'")
                return None
            
            # Filter out eBay promotional/ad elements
            ad_patterns = [
                "Shop on eBay",
                "Browse categories",
                "Sponsored",
                "Advertisement",
                "See more like this",
                "Trending at",
                "Related searches"
            ]
            
            if any(pattern.lower() in title.lower() for pattern in ad_patterns):
                logger.debug(f"Rejected product: appears to be ad/promo - '{title}'")
                return None
            
            return Product(
                title=title,
                price=price,
                rating=min(rating, 5.0),  # Cap rating at 5
                sales=sales,
                image_url=image_url or "",
                product_url=product_url or "",
                source="eBay"
            )
            
        except Exception as e:
            logger.debug(f"Failed to parse eBay product: {e}")
            return None