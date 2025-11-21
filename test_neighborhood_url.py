"""
Test neighborhood URL to see what's actually being returned.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Test URL with Lincoln Park
test_url = "https://www.apartments.com/chicago-il/lincoln-park/3-to-5-bedrooms/?min-1500-max-4500"

print("Testing URL:", test_url)
print("=" * 80)

# Setup Selenium
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get(test_url)
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    print(f"Page loaded: {len(html):,} characters")
    print()

    # Check title
    title = soup.find('title')
    print(f"Page title: {title.get_text() if title else 'None'}")
    print()

    # Check for "no results" message
    no_results = soup.find(string=lambda text: text and ('no results' in text.lower() or 'no apartments' in text.lower() or 'did not match' in text.lower()))
    if no_results:
        print("❌ 'No results' message found!")
        print(f"   Message: {no_results.strip()}")
        print()

    # Check for listings
    selectors_to_try = [
        'article.placard',
        '[data-listingid]',
        'li.mortar-wrapper',
        '.property-information',
        '[class*="property"]'
    ]

    print("Checking selectors:")
    for selector in selectors_to_try:
        elements = soup.select(selector)
        print(f"  {selector:<30} → {len(elements)} elements")

    print()

    # Save HTML for inspection
    with open('test_neighborhood_page.html', 'w') as f:
        f.write(html)
    print("✓ Saved HTML to: test_neighborhood_page.html")

    # Look for redirect or error messages
    print()
    print("Checking for common issues:")

    # Check if redirected to different page
    current_url = driver.current_url
    if current_url != test_url:
        print(f"⚠️  Page redirected to: {current_url}")

    # Check for error messages
    error_keywords = ['404', 'not found', 'error', 'invalid']
    body_text = soup.get_text().lower()
    for keyword in error_keywords:
        if keyword in body_text:
            print(f"⚠️  Found '{keyword}' in page text")

finally:
    driver.quit()

print()
print("=" * 80)
print("Check test_neighborhood_page.html to see what was returned")
