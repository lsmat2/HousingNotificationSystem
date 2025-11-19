"""
Debug script v2 - Uses Selenium to handle JavaScript rendering.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
from src.config import Config


def test_with_selenium():
    """Test scraping with Selenium (handles JavaScript)."""
    print("=" * 80)
    print("APARTMENTS.COM SCRAPER DEBUG (using Selenium)")
    print("=" * 80)
    print()

    # Load config
    config = Config('config.json')
    location = config.location

    # Build URL
    location_slug = location.lower()
    location_slug = re.sub(r'[^\w\s-]', '', location_slug)
    location_slug = re.sub(r'[\s_]+', '-', location_slug)
    url = f"https://www.apartments.com/{location_slug}/"

    print(f"Location: {location}")
    print(f"URL: {url}")
    print()

    # Setup Selenium with Chrome
    print("Setting up Selenium...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✓ Chrome driver initialized")
    except Exception as e:
        print(f"❌ Error initializing Chrome driver: {e}")
        print("\nYou may need to install ChromeDriver:")
        print("  brew install chromedriver")
        print("  or download from: https://chromedriver.chromium.org/")
        return

    try:
        # Load the page
        print(f"\nFetching: {url}")
        driver.get(url)

        # Wait for content to load
        print("Waiting for page to load...")
        time.sleep(5)  # Give JavaScript time to render

        # Get page source
        html = driver.page_source
        print(f"✓ Page loaded ({len(html)} characters)")
        print()

        # Save the HTML
        with open('debug_selenium_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ Saved full HTML to: debug_selenium_page.html")
        print()

        # Analyze with BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')

        # Get page title
        title = soup.find('title')
        print(f"Page Title: {title.get_text() if title else 'None'}")
        print()

        # Test various selectors
        print("Testing CSS selectors:")
        print("-" * 80)

        selectors = [
            ('article.placard', 'Original selector from code'),
            ('li.mortar-wrapper', 'Alternative from code'),
            ('[data-listingid]', 'Data attribute'),
            ('article', 'All articles'),
            ('.property', 'Property class'),
            ('.propertyCard', 'Property card'),
            ('[class*="property"]', 'Any property class'),
        ]

        best_selector = None
        best_count = 0

        for selector, description in selectors:
            elements = soup.select(selector)
            count = len(elements)
            print(f"  {selector:<30} → {count:>3} elements ({description})")

            if count > best_count and count < 100:  # Reasonable number
                best_selector = selector
                best_count = count

                # Show sample
                if count > 0:
                    sample = elements[0]
                    print(f"    Sample classes: {sample.get('class', [])}")
                    print(f"    Sample IDs: {sample.get('id', 'none')}")

                    # Try to find key info
                    price = sample.select_one('[class*="price"], [class*="rent"]')
                    beds = sample.select_one('[class*="bed"]')

                    if price:
                        print(f"    Price found: {price.get_text(strip=True)[:50]}")
                    if beds:
                        print(f"    Beds found: {beds.get_text(strip=True)[:50]}")

                    print()

        print()
        print("=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        if best_count > 0:
            print(f"✓ Best selector appears to be: {best_selector}")
            print(f"  Found {best_count} listings")
            print()
            print("To fix the scraper:")
            print(f"1. Update parse_listings() in scraper.py")
            print(f"2. Use selector: {best_selector}")
            print(f"3. Inspect debug_selenium_page.html for exact class names")
        else:
            print("❌ No listings found!")
            print("   Possible issues:")
            print("   - Location URL format is wrong")
            print("   - Apartments.com blocking automated access")
            print("   - Page structure has changed significantly")
            print()
            print("Check debug_selenium_page.html to see what was loaded")

        print()

    finally:
        driver.quit()
        print("✓ Browser closed")


if __name__ == '__main__':
    test_with_selenium()
