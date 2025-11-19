"""
Debug script to analyze Apartments.com requests and responses.
"""

import requests
from bs4 import BeautifulSoup
import re
from src.config import Config


def test_url_building():
    """Test what URL is being generated."""
    print("=" * 80)
    print("TESTING URL BUILDING")
    print("=" * 80)

    config = Config('config.json')
    location = config.location

    # Simulate the URL building logic
    location_slug = location.lower()
    location_slug = re.sub(r'[^\w\s-]', '', location_slug)
    location_slug = re.sub(r'[\s_]+', '-', location_slug)

    url = f"https://www.apartments.com/{location_slug}/"

    print(f"Location: {location}")
    print(f"URL Slug: {location_slug}")
    print(f"Full URL: {url}")
    print()

    return url


def fetch_and_analyze(url):
    """Fetch the page and analyze its structure."""
    print("=" * 80)
    print("FETCHING PAGE")
    print("=" * 80)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Size: {len(response.text)} characters")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print()

        if response.status_code != 200:
            print(f"❌ Non-200 status code!")
            return None

        return response.text

    except Exception as e:
        print(f"❌ Error fetching page: {e}")
        return None


def analyze_html_structure(html):
    """Analyze the HTML structure to find listing elements."""
    print("=" * 80)
    print("ANALYZING HTML STRUCTURE")
    print("=" * 80)

    soup = BeautifulSoup(html, 'lxml')

    # Save a sample of the HTML for inspection
    with open('debug_page_sample.html', 'w', encoding='utf-8') as f:
        f.write(html[:50000])  # First 50KB
    print("✓ Saved first 50KB of HTML to: debug_page_sample.html")
    print()

    # Check page title
    title = soup.find('title')
    print(f"Page Title: {title.get_text() if title else 'None'}")
    print()

    # Try to find listing containers with various selectors
    print("Testing different CSS selectors for listings:")
    print("-" * 80)

    selectors_to_test = [
        'article.placard',
        'li.mortar-wrapper',
        'div.property-item',
        '[data-listingid]',
        '[data-listing-id]',
        'article',
        'li.placard',
        'div.placard',
        '.property',
        '.propertyCard',
        '[class*="property"]',
        '[class*="listing"]',
        '[class*="placard"]',
    ]

    found_any = False
    for selector in selectors_to_test:
        elements = soup.select(selector)
        print(f"  {selector:<35} → Found {len(elements)} elements")
        if len(elements) > 0 and not found_any:
            found_any = True
            print(f"    ✓ First match! Sample classes: {elements[0].get('class', [])}")
            print(f"    ✓ Sample element:")
            print(f"    {str(elements[0])[:300]}...")
            print()

    if not found_any:
        print("\n❌ No listing elements found with standard selectors!")
        print("    The page structure may have changed or may be JavaScript-rendered.")

    print()

    # Check for common class names
    print("Common class names in the HTML:")
    print("-" * 80)
    all_classes = set()
    for element in soup.find_all(class_=True):
        if isinstance(element.get('class'), list):
            all_classes.update(element['class'])

    # Filter for property/listing/apartment related classes
    relevant_classes = [c for c in all_classes if any(keyword in c.lower()
                       for keyword in ['property', 'listing', 'apartment', 'placard', 'card', 'item'])]

    for i, class_name in enumerate(sorted(relevant_classes)[:20]):
        print(f"  {class_name}")
        if i >= 19:
            print(f"  ... and {len(relevant_classes) - 20} more")
            break

    print()

    # Check for JavaScript/React apps
    print("Checking for JavaScript rendering:")
    print("-" * 80)
    if 'react' in html.lower() or '__next' in html.lower() or 'vue' in html.lower():
        print("⚠️  Page appears to use JavaScript framework (React/Next.js/Vue)")
        print("    May require Selenium for dynamic content")
    else:
        print("✓ Page appears to be server-side rendered")

    print()


def main():
    """Run all debug tests."""
    print("\n" + "=" * 80)
    print("APARTMENTS.COM SCRAPER DEBUG")
    print("=" * 80)
    print()

    # Step 1: Test URL building
    url = test_url_building()

    # Step 2: Fetch the page
    html = fetch_and_analyze(url)

    if not html:
        print("❌ Could not fetch page. Exiting.")
        return

    # Step 3: Analyze HTML structure
    analyze_html_structure(html)

    print("=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Check debug_page_sample.html to inspect the actual HTML")
    print("2. Look for the correct CSS selectors for listings")
    print("3. Update scraper.py with the correct selectors")
    print()


if __name__ == '__main__':
    main()
