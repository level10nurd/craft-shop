#!/usr/bin/env python3
"""
Lightspeed API Client for retrieving data from Lightspeed Retail (X-Series) API.
Handles authentication, rate limiting, and data fetching for all entity types.
"""

import os
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class LightspeedAPIError(Exception):
    """Custom exception for Lightspeed API errors."""
    pass

class LightspeedClient:
    """Client for interacting with Lightspeed Retail API."""
    
    def __init__(self, base_url: str, bearer_token: str):
        """Initialize the Lightspeed client."""
        self.base_url = base_url.rstrip('/')
        self.bearer_token = bearer_token
        self.session = requests.Session()
        
        # Set up authentication headers
        self.session.headers.update({
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Rate limiting - Lightspeed: 300 x registers + 50 per 5-minute window  
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests to be safe
        self.rate_limit_remaining = None
        
    def _rate_limit(self):
        """Implement basic rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the Lightspeed API with error handling."""
        self._rate_limit()
        
        url = f"{self.base_url}/api/{endpoint}"
        
        try:
            logger.debug(f"Making request to: {url}")
            response = self.session.get(url, params=params, timeout=30)
            
            # Check rate limit headers
            self.rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
            if self.rate_limit_remaining:
                logger.debug(f"Rate limit remaining: {self.rate_limit_remaining}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise LightspeedAPIError("Authentication failed - check bearer token")
            elif response.status_code == 429:
                # Rate limited - check Retry-After header
                retry_after = response.headers.get('Retry-After', '300')  # Default 5 minutes
                wait_time = int(retry_after)
                logger.warning(f"Rate limited, waiting {wait_time} seconds before retry")
                time.sleep(wait_time)
                
                response = self.session.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise LightspeedAPIError(f"Rate limit retry failed: {response.status_code}")
            else:
                raise LightspeedAPIError(f"API request failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise LightspeedAPIError(f"Network error: {str(e)}")
    
    def _get_paginated_data(self, endpoint: str, params: Optional[Dict] = None, use_version_pagination: bool = True) -> List[Dict]:
        """Fetch all pages of data from a paginated endpoint with proper pagination."""
        all_data = []
        
        if use_version_pagination and endpoint.startswith('2.0/'):
            # Use API 2.0 version-based pagination
            after_version = None
            
            # Log the parameters being used for debugging
            if params:
                logger.info(f"Fetching {endpoint} with params: {params}")
            
            while True:
                current_params = params.copy() if params else {}
                if after_version:
                    current_params['after'] = after_version
                
                logger.info(f"Fetching {endpoint} (after version: {after_version})")
                response = self._make_request(endpoint, current_params)
                
                data = response.get('data', [])
                if not data:  # Empty collection means we're done
                    break
                    
                all_data.extend(data)
                
                # Get the highest version number for next page
                versions = [item.get('version') for item in data if item.get('version')]
                if versions:
                    after_version = max(versions)
                else:
                    break
                    
                # Safety check to prevent infinite loops
                if len(all_data) > 100000:
                    logger.warning(f"Reached maximum record limit for {endpoint}")
                    break
        else:
            # Use traditional page-based pagination for API 0.x
            page = 1
            page_size = 200  # Maximum for 0.x API
            
            while True:
                current_params = params.copy() if params else {}
                current_params.update({
                    'page': page,
                    'page_size': page_size
                })
                
                logger.info(f"Fetching {endpoint} page {page}")
                response = self._make_request(endpoint, current_params)
                
                data = response.get('data', response)
                if isinstance(data, list):
                    if not data:  # Empty page means we're done
                        break
                    all_data.extend(data)
                    
                    # Check pagination metadata if available
                    pagination = response.get('pagination', {})
                    if pagination.get('page') >= pagination.get('pages', float('inf')):
                        break
                        
                    page += 1
                else:
                    # Single item response
                    all_data.append(data)
                    break
                    
                # Safety check to prevent infinite loops
                if page > 1000:
                    logger.warning(f"Reached maximum page limit for {endpoint}")
                    break
                
        logger.info(f"Fetched {len(all_data)} records from {endpoint}")
        return all_data
    
    def get_customers(self, after_version: Optional[int] = None) -> List[Dict]:
        """Fetch customer data using version-based pagination."""
        params = {}
        if after_version:
            params['after'] = after_version
            logger.info(f"Requesting customers after version: {after_version}")
            
        return self._get_paginated_data('2.0/customers', params)
    
    def get_outlets(self) -> List[Dict]:
        """Fetch outlet data."""
        return self._get_paginated_data('2.0/outlets')
    
    def get_products(self, after_version: Optional[int] = None) -> List[Dict]:
        """Fetch product data using version-based pagination."""
        params = {}
        if after_version:
            params['after'] = after_version
            logger.info(f"Requesting products after version: {after_version}")
            
        return self._get_paginated_data('2.0/products', params)
    
    def get_sales(self, after_version: Optional[int] = None) -> List[Dict]:
        """Fetch sales data using version-based pagination."""
        params = {}
        if after_version:
            params['after'] = after_version
            logger.info(f"Requesting sales after version: {after_version}")
            
        return self._get_paginated_data('2.0/sales', params)
    
    def get_inventory(self) -> List[Dict]:
        """Fetch inventory data."""
        return self._get_paginated_data('2.0/inventory')
    
    def test_connection(self) -> bool:
        """Test if the API connection is working."""
        try:
            # Try to fetch a single outlet to test connection
            self._make_request('2.0/outlets', {'per_page': 1})
            return True
        except LightspeedAPIError:
            return False

def create_lightspeed_client() -> LightspeedClient:
    """Create a Lightspeed client using environment variables."""
    base_url = os.environ.get('LIGHTSPEED_BASE_URL')
    bearer_token = os.environ.get('LIGHTSPEED_BEARER_TOKEN')
    
    if not base_url or not bearer_token:
        raise ValueError("Missing LIGHTSPEED_BASE_URL or LIGHTSPEED_BEARER_TOKEN environment variables")
    
    return LightspeedClient(base_url, bearer_token)