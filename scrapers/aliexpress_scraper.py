"""
AliExpress Open Platform API scraper implementation.
"""
import asyncio
import aiohttp
import hashlib
import hmac
import json
import time
from typing import List, Optional, Dict, Any
import logging
from urllib.parse import quote

from .base_scraper import BaseScraper, Product
from config import config

logger = logging.getLogger(__name__)

class AliExpressScraper(BaseScraper):
    """AliExpress Open Platform API scraper implementation."""
    
    def __init__(self):
        super().__init__(
            base_url="https://api-sg.aliexpress.com/sync",
            headers={
                'Content-Type': 'application/json;charset=utf-8',
                'User-Agent': 'ShopGenie/1.0'
            }
        )
        
        self.app_key = config.ALIEXPRESS_APP_KEY
        self.app_secret = config.ALIEXPRESS_APP_SECRET
        self.tracking_id = config.ALIEXPRESS_TRACKING_ID
        
        # Check if API credentials are configured
        if not self.app_key or not self.app_secret:
            logger.warning("AliExpress API credentials not configured. Please set ALIEXPRESS_APP_KEY and ALIEXPRESS_APP_SECRET environment variables.")
    
    def _generate_signature(self, method: str, params: Dict[str, Any]) -> str:
        """
        Generate API signature for AliExpress Open Platform.
        
        Args:
            method: API method name
            params: API parameters
            
        Returns:
            Generated signature
        """
        if not self.app_secret:
            return ""
            
        # Sort parameters by key
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = method
        for key, value in sorted_params:
            query_string += f"{key}{value}"
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        return signature
    
    def _build_request_params(self, method: str, api_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build request parameters with authentication.
        
        Args:
            method: API method name
            api_params: API-specific parameters
            
        Returns:
            Complete request parameters
        """
        timestamp = str(int(time.time() * 1000))
        
        params = {
            'app_key': self.app_key,
            'method': method,
            'timestamp': timestamp,
            'format': 'json',
            'v': '2.0',
            'sign_method': 'sha256'
        }
        
        # Add API-specific parameters
        params.update(api_params)
        
        # Generate signature
        signature = self._generate_signature(method, params)
        params['sign'] = signature
        
        return params
    
    async def search(self, query: str, max_results: int = 50) -> List[Product]:
        """
        Search for products on AliExpress using Open Platform API.
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        if not self.app_key or not self.app_secret:
            logger.error("AliExpress API credentials not configured")
            return []
        
        try:
            logger.info(f"Searching AliExpress for: {query}")
            
            # API parameters for product search
            api_params = {
                'keywords': query,
                'page_size': min(max_results, 50),  # AliExpress API max is usually 50
                'page_no': 1,
                'sort': 'SALE_PRICE_ASC',  # Sort by price ascending
                'target_currency': 'USD',
                'target_language': 'EN',
                'ship_to_country': 'US'
            }
            
            # Add tracking ID if available
            if self.tracking_id:
                api_params['tracking_id'] = self.tracking_id
            
            # Build complete request parameters
            params = self._build_request_params('aliexpress.affiliate.product.query', api_params)
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers=self.headers
            ) as session:
                
                for attempt in range(3):
                    try:
                        if attempt > 0:
                            await asyncio.sleep(1.0)
                        
                        async with session.post(self.base_url, json=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                return self._parse_search_results(data, max_results)
                            else:
                                logger.warning(f"HTTP {response.status} for AliExpress search")
                                
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
            logger.error(f"Failed to search AliExpress: {e}")
            return []
    
    def _parse_search_results(self, data: Dict[str, Any], max_results: int) -> List[Product]:
        """Parse search results from API response."""
        products = []
        
        try:
            # Check for API errors
            if not data.get('success', False):
                error_code = data.get('error_code', 'Unknown')
                error_msg = data.get('error_message', 'Unknown error')
                logger.error(f"AliExpress API error {error_code}: {error_msg}")
                return []
            
            # Extract products from response
            result = data.get('result', {})
            products_data = result.get('products', [])
            
            if not products_data:
                logger.info("No products found in AliExpress API response")
                return []
            
            logger.debug(f"Found {len(products_data)} products from AliExpress API")
            
            for product_data in products_data[:max_results]:
                try:
                    product = self._parse_product(product_data)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Failed to parse AliExpress product: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(products)} products from AliExpress")
            return products
            
        except Exception as e:
            logger.error(f"Failed to parse AliExpress search results: {e}")
            return []
    
    def _parse_product(self, product_data: Dict[str, Any]) -> Optional[Product]:
        """Parse a single product from API response."""
        try:
            # Extract basic product information
            title = product_data.get('product_title', 'Unknown Product')
            
            # Price information
            price_info = product_data.get('target_sale_price', {})
            if isinstance(price_info, dict):
                price = f"${price_info.get('amount', '0')}"
            else:
                price = f"${product_data.get('target_sale_price', '0')}"
            
            # Rating (AliExpress uses different rating system)
            rating = float(product_data.get('evaluate_rate', '0'))
            # Convert percentage to 5-star scale (e.g., 95% -> 4.75 stars)
            rating = min(rating / 20.0, 5.0) if rating > 5 else rating
            
            # Sales count
            sales = int(product_data.get('volume', 0))
            
            # Image URL
            image_url = product_data.get('product_main_image_url', '')
            
            # Product URL
            product_url = product_data.get('promotion_link', '')
            if not product_url:
                product_id = product_data.get('product_id', '')
                if product_id:
                    product_url = f"https://www.aliexpress.com/item/{product_id}.html"
            
            # Validate essential data
            if not title or len(title) < 3:
                return None
            
            return Product(
                title=title,
                price=price,
                rating=rating,
                sales=sales,
                image_url=image_url,
                product_url=product_url,
                source="AliExpress"
            )
            
        except Exception as e:
            logger.debug(f"Failed to parse AliExpress product: {e}")
            return None
    
    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed product information by product ID.
        
        Args:
            product_id: AliExpress product ID
            
        Returns:
            Product details or None if not found
        """
        if not self.app_key or not self.app_secret:
            logger.error("AliExpress API credentials not configured")
            return None
        
        try:
            api_params = {
                'product_ids': product_id,
                'target_currency': 'USD',
                'target_language': 'EN',
                'ship_to_country': 'US'
            }
            
            if self.tracking_id:
                api_params['tracking_id'] = self.tracking_id
            
            params = self._build_request_params('aliexpress.affiliate.product.detail.query', api_params)
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers=self.headers
            ) as session:
                
                async with session.post(self.base_url, json=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success', False):
                            result = data.get('result', {})
                            products = result.get('products', [])
                            return products[0] if products else None
                    
            return None
            
        except Exception as e:
            logger.error(f"Failed to get AliExpress product details: {e}")
            return None