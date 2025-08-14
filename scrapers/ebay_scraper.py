"""
eBay scraper implementation using eBay API.
"""
import asyncio
import logging
from typing import List, Optional
from ebaysdk.finding import Connection as FindingConnection
from ebaysdk.exception import ConnectionError as EbayConnectionError
from ebaysdk.trading import Connection as TradingConnection
from ebaysdk.response import ResponseDataObject

from .base_scraper import BaseScraper, Product
from config import config

logger = logging.getLogger(__name__)

class EbayScraper(BaseScraper):
    """eBay scraper implementation using eBay API."""
    
    def __init__(self):
        super().__init__(base_url="https://www.ebay.com")
        
        # Validate eBay API configuration
        if not config.EBAY_APP_ID or not config.EBAY_CERT_ID or not config.EBAY_DEV_ID:
            logger.warning("eBay API credentials not configured. eBay scraper will be disabled.")
            self.api_enabled = False
        else:
            self.api_enabled = True
            self.app_id = config.EBAY_APP_ID
            self.cert_id = config.EBAY_CERT_ID
            self.dev_id = config.EBAY_DEV_ID
            self.environment = config.EBAY_ENVIRONMENT
            self.site_id = config.EBAY_SITE_ID
            
            logger.info(f"eBay API initialized with environment: {self.environment}, site_id: {self.site_id}")
    
    async def search(self, query: str, max_results: int = 50) -> List[Product]:
        """
        Search for products on eBay using the eBay Finding API.
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        if not self.api_enabled:
            logger.warning("eBay API not configured. Returning empty results.")
            return []
        
        try:
            logger.info(f"Searching eBay API for: {query}")
            
            # Run the API call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            products = await loop.run_in_executor(
                None, 
                self._search_sync, 
                query, 
                max_results
            )
            
            logger.info(f"eBay API returned {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Failed to search eBay API: {e}")
            return []
    
    def _search_sync(self, query: str, max_results: int) -> List[Product]:
        """Synchronous search using eBay Finding API."""
        try:
            # Create Finding API connection
            api = FindingConnection(
                appid=self.app_id,
                config_file=None,
                domain='svcs.sandbox.ebay.com' if self.environment == 'sandbox' else 'svcs.ebay.com'
            )
            
            # Prepare search request
            request = {
                'keywords': query,
                'paginationInput': {
                    'entriesPerPage': min(max_results, 100),  # eBay API max is 100
                    'pageNumber': 1
                },
                'sortOrder': 'BestMatch'  # BestMatch, CurrentPriceHighest, CurrentPriceLowest, etc.
            }
            
            # Add site filter if specified
            if self.site_id is not None:
                request['siteId'] = self.site_id
            
            # Make API call
            response = api.execute('findItemsByKeywords', request)
            
            # Parse response
            products = self._parse_api_response(response, max_results)
            
            return products
            
        except EbayConnectionError as e:
            logger.error(f"eBay API connection error: {e}")
            return []
        except Exception as e:
            logger.error(f"eBay API error: {e}")
            return []
    
    def _parse_api_response(self, response: ResponseDataObject, max_results: int) -> List[Product]:
        """Parse eBay API response into Product objects."""
        products = []
        
        try:
            # Check if response has search results
            response_dict = response.dict() if hasattr(response, 'dict') else {}
            
            if 'searchResult' not in response_dict or not response_dict['searchResult']:
                logger.warning("No search results in eBay API response")
                return []
            
            # Get items from response
            search_result = response_dict['searchResult']
            items = search_result.get('item', [])
            if not items:
                logger.info("No items found in eBay search results")
                return []
            
            # Ensure items is a list
            if not isinstance(items, list):
                items = [items]
            
            logger.debug(f"Found {len(items)} items in eBay API response")
            
            for item in items[:max_results]:
                try:
                    product = self._parse_api_item(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Failed to parse eBay item: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(products)} products from eBay API")
            return products
            
        except Exception as e:
            logger.error(f"Failed to parse eBay API response: {e}")
            return []
    
    def _parse_api_item(self, item: dict) -> Optional[Product]:
        """Parse a single item from eBay API response."""
        try:
            # Extract basic information
            title = item.get('title', 'Unknown Item')
            item_id = item.get('itemId', '')
            
            # Extract price information
            price = "N/A"
            if 'sellingStatus' in item and 'currentPrice' in item['sellingStatus']:
                current_price = item['sellingStatus']['currentPrice']
                price_value = current_price.get('value', current_price.get('__value__', 'N/A'))
                price_currency = current_price.get('currencyId', current_price.get('@currencyId', 'USD'))
                price = f"{price_currency} {price_value}"
            
            # Extract rating (eBay doesn't provide direct ratings in Finding API)
            # We'll use seller feedback score as a proxy
            rating = 0.0
            if 'sellerInfo' in item and 'feedbackScore' in item['sellerInfo']:
                feedback_score = int(item['sellerInfo']['feedbackScore'])
                # Convert feedback score to rating (1-5 scale)
                if feedback_score > 10000:
                    rating = 5.0
                elif feedback_score > 5000:
                    rating = 4.5
                elif feedback_score > 1000:
                    rating = 4.0
                elif feedback_score > 500:
                    rating = 3.5
                elif feedback_score > 100:
                    rating = 3.0
                elif feedback_score > 50:
                    rating = 2.5
                else:
                    rating = 2.0
            
            # Extract sales count (not directly available in Finding API)
            sales = 0
            
            # Extract image URL
            image_url = ""
            if 'pictureURLLarge' in item:
                image_url = item['pictureURLLarge']
            elif 'galleryURL' in item:
                image_url = item['galleryURL']
            
            # Extract product URL
            product_url = ""
            if 'viewItemURL' in item:
                product_url = item['viewItemURL']
            
            # Extract additional information
            condition = item.get('condition', {}).get('conditionDisplayName', 'Unknown')
            location = item.get('location', 'Unknown')
            
            # Get seller information
            seller_name = ""
            if 'sellerInfo' in item:
                seller_name = item['sellerInfo'].get('sellerUserName', '')
            
            # Filter out invalid items
            if not title or title == "Unknown Item" or len(title) < 5:
                logger.debug(f"Rejected eBay item: invalid title - '{title}'")
                return None
            
            # Create Product object
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
            logger.debug(f"Failed to parse eBay API item: {e}")
            return None
    
    async def get_item_details(self, item_id: str) -> Optional[dict]:
        """
        Get detailed information about a specific eBay item using Trading API.
        
        Args:
            item_id: eBay item ID
            
        Returns:
            Dictionary with item details or None if failed
        """
        if not self.api_enabled:
            logger.warning("eBay API not configured. Cannot get item details.")
            return None
        
        try:
            logger.info(f"Getting eBay item details for: {item_id}")
            
            # Run the API call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            details = await loop.run_in_executor(
                None, 
                self._get_item_details_sync, 
                item_id
            )
            
            return details
            
        except Exception as e:
            logger.error(f"Failed to get eBay item details: {e}")
            return None
    
    def _get_item_details_sync(self, item_id: str) -> Optional[dict]:
        """Synchronous call to get item details using eBay Trading API."""
        try:
            # Create Trading API connection
            api = TradingConnection(
                appid=self.app_id,
                devid=self.dev_id,
                certid=self.cert_id,
                config_file=None,
                domain=f'api.{self.environment}.ebay.com'
            )
            
            # Prepare request
            request = {
                'ItemID': item_id,
                'DetailLevel': 'ReturnAll'
            }
            
            # Make API call
            response = api.execute('GetItem', request)
            
            # Extract relevant information
            item = response.dict()['Item']
            
            details = {
                'title': item.get('Title', ''),
                'description': item.get('Description', ''),
                'price': item.get('StartPrice', {}).get('value', 'N/A'),
                'currency': item.get('StartPrice', {}).get('currencyID', 'USD'),
                'condition': item.get('ConditionDisplayName', 'Unknown'),
                'location': item.get('Location', 'Unknown'),
                'seller': item.get('Seller', {}).get('UserID', ''),
                'listing_type': item.get('ListingType', ''),
                'end_time': item.get('EndTime', ''),
                'primary_category': item.get('PrimaryCategory', {}).get('CategoryName', ''),
                'pictures': [],
                'shipping_info': {}
            }
            
            # Extract pictures
            if 'PictureDetails' in item and 'PictureURL' in item['PictureDetails']:
                pictures = item['PictureDetails']['PictureURL']
                if isinstance(pictures, list):
                    details['pictures'] = pictures
                else:
                    details['pictures'] = [pictures]
            
            # Extract shipping information
            if 'ShippingDetails' in item:
                shipping = item['ShippingDetails']
                details['shipping_info'] = {
                    'type': shipping.get('ShippingType', ''),
                    'service': shipping.get('ShippingServiceOptions', {}).get('ShippingServiceName', ''),
                    'cost': shipping.get('ShippingServiceOptions', {}).get('ShippingServiceCost', {}).get('value', 'N/A')
                }
            
            return details
            
        except EbayConnectionError as e:
            logger.error(f"eBay Trading API connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"eBay Trading API error: {e}")
            return None
    
    def _parse_product(self, element) -> Optional[Product]:
        """
        Parse a single product element from HTML (for compatibility with BaseScraper).
        This method is not used in the API-based implementation but required by the abstract base class.
        
        Args:
            element: HTML element containing product data (not used in API implementation)
            
        Returns:
            None (this method is not used in API-based scraping)
        """
        # This method is not used in the API-based implementation
        # It's only here to satisfy the abstract base class requirement
        logger.warning("_parse_product called on API-based eBay scraper - this method is not used")
        return None