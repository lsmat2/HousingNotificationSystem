"""
Web scraper module for Apartments.com.
Fetches and parses housing listings based on search criteria.
Uses Selenium for JavaScript-rendered content.
"""

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin
import re
import hashlib

from src.config import Config


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApartmentsScraper:
    """Scraper for Apartments.com housing listings."""

    BASE_URL = "https://www.apartments.com"

    def __init__(self, config: Config):
        """
        Initialize scraper with configuration.

        Args:
            config: Configuration object with scraper settings.
        """
        self.config = config
        self.driver = None

    def _init_driver(self):
        """Initialize Undetected Chrome WebDriver (bypasses bot detection)."""
        if self.driver is not None:
            return

        chrome_options = uc.ChromeOptions()
        # Note: headless mode can trigger detection, using visible browser
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        try:
            # Use undetected_chromedriver to avoid bot detection
            # headless=False for better compatibility (window runs in background on macOS)
            # use_subprocess=True for better stability
            self.driver = uc.Chrome(
                options=chrome_options,
                version_main=None,
                headless=False,
                use_subprocess=True
            )
            logger.info("✓ Undetected Chrome WebDriver initialized")
            # Give driver a moment to stabilize
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            logger.error("Make sure Chrome browser is installed")
            raise

    def _close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("✓ Chrome WebDriver closed")

    def build_search_url(self, location: str, page: int = 1, neighborhood: str = None) -> str:
        """
        Build Apartments.com search URL from location string.
        Includes bedroom and price filters from config in URL path.

        Args:
            location: Location string (e.g., "San Francisco, CA")
            page: Page number for pagination
            neighborhood: Optional neighborhood name (e.g., "lincoln-park", "wicker-park")

        Returns:
            Full search URL with filters in path
        """
        # Clean and format location for URL
        location_slug = location.lower()
        location_slug = re.sub(r'[^\w\s-]', '', location_slug)
        location_slug = re.sub(r'[\s_]+', '-', location_slug)

        # If neighborhood is specified, Apartments.com format is:
        # /neighborhood-city-state/ (e.g., /lincoln-park-chicago-il/)
        # Otherwise just: /city-state/ (e.g., /chicago-il/)
        if neighborhood:
            neighborhood_slug = neighborhood.lower()
            neighborhood_slug = re.sub(r'[^\w\s-]', '', neighborhood_slug)
            neighborhood_slug = re.sub(r'[\s_]+', '-', neighborhood_slug)
            # Combine neighborhood with location
            base_location = f"{neighborhood_slug}-{location_slug}"
        else:
            base_location = location_slug

        # Start with the base location
        path_parts = [base_location]

        # Build filter path segments
        filter_parts = []

        # Add bedroom filter as path segment
        # Apartments.com format: /3-bedrooms/ or /3-to-5-bedrooms/
        if self.config.min_bedrooms is not None:
            if self.config.max_bedrooms and self.config.max_bedrooms != self.config.min_bedrooms:
                filter_parts.append(f"{self.config.min_bedrooms}-to-{self.config.max_bedrooms}-bedrooms")
            else:
                filter_parts.append(f"{self.config.min_bedrooms}-bedrooms")

        # Add filters to path
        path_parts.extend(filter_parts)

        # Add page number if > 1
        if page > 1:
            path_parts.append(str(page))

        # Build final path
        path = "/".join(path_parts) + "/"

        # Add price as query parameters (these typically work as query params)
        query_params = []
        if self.config.min_price is not None or self.config.max_price is not None:
            price_parts = []
            if self.config.min_price:
                price_parts.append(f"min-{int(self.config.min_price)}")
            if self.config.max_price:
                price_parts.append(f"max-{int(self.config.max_price)}")
            if price_parts:
                query_params.append("-".join(price_parts))

        url = f"{self.BASE_URL}/{path}"
        if query_params:
            url += "?" + "&".join(query_params)

        return url

    def fetch_page(self, url: str, retry_count: int = 0) -> Optional[str]:
        """
        Fetch a web page using Selenium with retry logic.

        Args:
            url: URL to fetch
            retry_count: Current retry attempt

        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            self._init_driver()

            self.driver.get(url)

            # Wait for JavaScript to render (listings are dynamically loaded)
            logger.info("Waiting for page to render...")
            time.sleep(5)  # Give JavaScript time to load

            html = self.driver.page_source
            logger.info(f"✓ Page loaded ({len(html):,} characters)")

            return html

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")

            # Close the driver if it's in a bad state
            self._close_driver()

            if retry_count < self.config.max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return self.fetch_page(url, retry_count + 1)

            return None

    def parse_listings(self, html: str, base_url: str) -> List[Dict]:
        """
        Parse listings from HTML content.

        Args:
            html: HTML content from Apartments.com
            base_url: Base URL for resolving relative links

        Returns:
            List of parsed listing dictionaries
        """
        soup = BeautifulSoup(html, 'lxml')
        listings = []

        # Apartments.com uses article.placard for listing containers
        listing_containers = soup.select('article.placard')

        if not listing_containers:
            logger.warning("No listing containers found. HTML structure may have changed.")
            # Try alternative selectors
            listing_containers = soup.select('[data-listingid], li.mortar-wrapper')

        logger.info(f"Found {len(listing_containers)} potential listings")

        for container in listing_containers:
            try:
                listing = self._parse_single_listing(container, base_url)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.error(f"Error parsing listing: {e}")
                continue

        return listings

    def _parse_single_listing(self, container, base_url: str) -> Optional[Dict]:
        """
        Parse a single listing from its HTML container.

        Args:
            container: BeautifulSoup element containing listing data
            base_url: Base URL for resolving relative links

        Returns:
            Listing dictionary or None if parsing failed
        """
        listing = {}

        # Extract URL
        url_elem = container.select_one('a.property-link')
        if url_elem and url_elem.get('href'):
            listing['url'] = urljoin(base_url, url_elem['href'])
        else:
            logger.warning("No URL found for listing, skipping")
            return None

        # Generate listing ID from URL (unique identifier)
        listing['listing_id'] = self._generate_listing_id(listing['url'])

        # Extract title/property name
        title_elem = container.select_one('.property-title')
        listing['title'] = title_elem.get_text(strip=True) if title_elem else None

        # Extract address
        address_elem = container.select_one('.property-address')
        listing['address'] = address_elem.get_text(strip=True) if address_elem else None

        # Extract price - Apartments.com uses .priceTextBox for prices
        # There may be multiple prices for different bedroom counts
        price_elems = container.select('.priceTextBox')
        if price_elems:
            # Get the first (usually lowest) price
            price_text = price_elems[0].get_text(strip=True)
            listing['price'] = self._parse_price(price_text)
        else:
            listing['price'] = None

        # Extract bedrooms - Apartments.com uses .bedTextBox
        bed_elems = container.select('.bedTextBox')
        if bed_elems:
            # Get the first bedroom count
            bed_text = bed_elems[0].get_text(strip=True)
            listing['bedrooms'] = self._parse_number(bed_text)
        else:
            listing['bedrooms'] = None

        # Extract bathrooms - Less commonly displayed on listing cards
        bath_elem = container.select_one('.bath-range, .baths, [class*="bath"]')
        if bath_elem:
            bath_text = bath_elem.get_text(strip=True)
            listing['bathrooms'] = self._parse_number(bath_text)
        else:
            listing['bathrooms'] = None

        # Extract square feet
        sqft_elem = container.select_one('.sqft, .square-feet, [class*="sqft"]')
        if sqft_elem:
            sqft_text = sqft_elem.get_text(strip=True)
            listing['square_feet'] = self._parse_number(sqft_text)
        else:
            listing['square_feet'] = None

        # Extract availability date
        avail_elem = container.select_one('.availability, .available-date, [class*="avail"]')
        listing['availability_date'] = avail_elem.get_text(strip=True) if avail_elem else None

        return listing

    def _generate_listing_id(self, url: str) -> str:
        """Generate a unique listing ID from URL."""
        # Extract any existing ID from URL
        # Apartments.com URLs look like: /property-name-city-state/listing-id/
        id_match = re.search(r'/([a-z0-9]+)/?$', url)
        if id_match:
            return id_match.group(1)

        # Fallback: hash the URL
        return hashlib.md5(url.encode()).hexdigest()[:16]

    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price from text string.

        Examples: "$1,500", "$1,500+", "$1500/mo"

        Returns the minimum price if a range is given.
        """
        # Remove non-numeric characters except digits and decimal points
        cleaned = re.sub(r'[^\d.]', '', price_text)

        # Find all numbers
        numbers = re.findall(r'\d+\.?\d*', cleaned)

        if numbers:
            # Return the first (minimum) price
            return float(numbers[0])

        return None

    def _parse_number(self, text: str) -> Optional[float]:
        """
        Parse a number from text (bedrooms, bathrooms, square feet).

        Examples: "2 Beds", "1.5 Baths", "Studio", "800 sq ft"
        """
        # Handle "Studio" as 0 bedrooms
        if 'studio' in text.lower():
            return 0

        # Find the first number (including decimals)
        match = re.search(r'\d+\.?\d*', text)
        if match:
            return float(match.group())

        return None

    def scrape_listings(self, max_pages: int = 3) -> List[Dict]:
        """
        Scrape listings from Apartments.com.
        If neighborhoods are configured, searches each neighborhood separately.

        Args:
            max_pages: Maximum number of pages to scrape per neighborhood

        Returns:
            List of all scraped listings
        """
        all_listings = []
        location = self.config.location
        neighborhoods = self.config.neighborhoods

        # Determine search targets
        if neighborhoods:
            logger.info(f"Starting scrape for {len(neighborhoods)} neighborhoods in {location}")
            search_targets = [(location, neighborhood) for neighborhood in neighborhoods]
        else:
            logger.info(f"Starting scrape for location: {location} (all neighborhoods)")
            search_targets = [(location, None)]

        try:
            # Scrape each neighborhood (or entire city if no neighborhoods specified)
            for location, neighborhood in search_targets:
                if neighborhood:
                    logger.info(f"Scraping neighborhood: {neighborhood}")

                neighborhood_listings = []

                for page in range(1, max_pages + 1):
                    url = self.build_search_url(location, page, neighborhood)
                    html = self.fetch_page(url)

                    if not html:
                        logger.warning(f"Failed to fetch page {page}, stopping pagination")
                        break

                    listings = self.parse_listings(html, url)

                    if not listings:
                        logger.info(f"No listings found on page {page}, stopping pagination")
                        break

                    neighborhood_listings.extend(listings)
                    logger.info(f"Page {page}: Found {len(listings)} listings")

                    # Be respectful with rate limiting between pages
                    if page < max_pages:
                        time.sleep(3)

                # Log neighborhood summary
                if neighborhood:
                    logger.info(f"Neighborhood '{neighborhood}': {len(neighborhood_listings)} listings found")

                all_listings.extend(neighborhood_listings)

                # Wait between neighborhoods
                if len(search_targets) > 1 and (location, neighborhood) != search_targets[-1]:
                    logger.info("Waiting before next neighborhood...")
                    time.sleep(5)

        finally:
            # Always close the browser
            self._close_driver()

        logger.info(f"Scraping complete. Total listings found: {len(all_listings)}")
        return all_listings
