"""
Manual HTML analyzer.

INSTRUCTIONS:
1. Open your browser and go to: https://www.apartments.com/chicago-il/
2. Right-click → "View Page Source" or "Inspect" → Copy the HTML
3. Save it as 'manual_page.html' in this directory
4. Run this script: python analyze_manual_html.py
"""

from bs4 import BeautifulSoup
import os


def analyze_manual_html():
    """Analyze manually saved HTML file."""

    if not os.path.exists('manual_page.html'):
        print("=" * 80)
        print("MANUAL HTML ANALYZER")
        print("=" * 80)
        print()
        print("❌ File 'manual_page.html' not found!")
        print()
        print("INSTRUCTIONS:")
        print("1. Open browser and visit:")
        print("   https://www.apartments.com/chicago-il/")
        print()
        print("2. Save the page:")
        print("   - Chrome: Ctrl+S / Cmd+S → Save as 'manual_page.html'")
        print("   - Or right-click → 'View Page Source' → Copy all → Save to 'manual_page.html'")
        print()
        print("3. Place 'manual_page.html' in this directory")
        print()
        print("4. Run this script again")
        return

    print("=" * 80)
    print("ANALYZING MANUAL HTML")
    print("=" * 80)
    print()

    with open('manual_page.html', 'r', encoding='utf-8') as f:
        html = f.read()

    print(f"✓ Loaded manual_page.html ({len(html):,} characters)")
    print()

    soup = BeautifulSoup(html, 'lxml')

    # Page title
    title = soup.find('title')
    print(f"Page Title: {title.get_text() if title else 'None'}")
    print()

    # Test selectors
    print("Testing CSS Selectors:")
    print("=" * 80)

    selectors = [
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
    ]

    results = []

    for selector in selectors:
        elements = soup.select(selector)
        count = len(elements)
        results.append((selector, count, elements))
        print(f"{selector:<35} → {count:>4} elements")

        if 0 < count < 50 and elements:
            # Show sample of first element
            sample = elements[0]
            classes = sample.get('class', [])
            if classes:
                print(f"  └─ Sample classes: {', '.join(classes[:3])}")

    print()

    # Find best match
    best = [(s, c, e) for s, c, e in results if 0 < c < 100]
    if best:
        best.sort(key=lambda x: x[1], reverse=True)
        selector, count, elements = best[0]

        print("=" * 80)
        print(f"BEST MATCH: {selector} ({count} elements)")
        print("=" * 80)
        print()

        # Analyze first 3 listings
        for i, elem in enumerate(elements[:3], 1):
            print(f"\nListing #{i}:")
            print("-" * 80)

            # Try to extract information
            info = {}

            # URL
            link = elem.select_one('a[href*="apartments.com"]')
            if link:
                info['url'] = link.get('href', 'N/A')

            # Title
            title = elem.select_one('.property-title, .property-name, h2, h3, [class*="title"]')
            if title:
                info['title'] = title.get_text(strip=True)

            # Price
            price_selectors = ['.price-range', '.rent', '.pricing', '[class*="price"]', '[class*="rent"]']
            for ps in price_selectors:
                price = elem.select_one(ps)
                if price:
                    info['price'] = price.get_text(strip=True)
                    break

            # Beds
            bed_selectors = ['.bed-range', '.beds', '[class*="bed"]']
            for bs in bed_selectors:
                beds = elem.select_one(bs)
                if beds:
                    info['beds'] = beds.get_text(strip=True)
                    break

            # Baths
            bath_selectors = ['.bath-range', '.baths', '[class*="bath"]']
            for bs in bath_selectors:
                baths = elem.select_one(bs)
                if baths:
                    info['baths'] = baths.get_text(strip=True)
                    break

            # Display what we found
            for key, value in info.items():
                print(f"  {key.capitalize()}: {value}")

            if not info:
                print("  ⚠️  Could not extract information")
                print(f"  Element classes: {elem.get('class', [])}")
                print(f"  Element HTML (first 200 chars):")
                print(f"  {str(elem)[:200]}...")

        print()
        print("=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print(f"\nUpdate scraper.py line ~111:")
        print(f"  listing_containers = soup.select('{selector}')")
        print()
        print("Also check the selectors for:")
        print("  - Price elements (class names containing 'price' or 'rent')")
        print("  - Bedroom elements (class names containing 'bed')")
        print("  - Bathroom elements (class names containing 'bath')")
        print()

    else:
        print("❌ No suitable listing containers found!")
        print()
        print("Let's look at all unique class names:")
        print("-" * 80)

        all_classes = set()
        for elem in soup.find_all(class_=True):
            classes = elem.get('class', [])
            if isinstance(classes, list):
                all_classes.update(classes)

        relevant = sorted([c for c in all_classes
                          if any(keyword in c.lower()
                                for keyword in ['property', 'listing', 'apartment', 'card', 'placard'])])

        for c in relevant[:30]:
            print(f"  {c}")

        if len(relevant) > 30:
            print(f"  ... and {len(relevant) - 30} more")


if __name__ == '__main__':
    analyze_manual_html()
