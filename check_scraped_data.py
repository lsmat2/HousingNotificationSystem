"""
Quick script to check what data the scraper is actually extracting.
"""

from src.config import Config
from src.scraper import ApartmentsScraper

config = Config('config.json')
scraper = ApartmentsScraper(config)

print("Scraping first page to check data quality...")
print("=" * 80)

listings = scraper.scrape_listings(max_pages=1)

print(f"\nTotal listings found: {len(listings)}")
print("\nFirst 5 listings:")
print("=" * 80)

for i, listing in enumerate(listings[:5], 1):
    print(f"\n#{i}:")
    print(f"  Title: {listing.get('title', 'N/A')}")
    print(f"  Address: {listing.get('address', 'N/A')}")
    print(f"  Price: ${listing.get('price', 'N/A')}")
    print(f"  Bedrooms: {listing.get('bedrooms', 'N/A')}")
    print(f"  Bathrooms: {listing.get('bathrooms', 'N/A')}")
    print(f"  URL: {listing.get('url', 'N/A')[:60]}...")

print("\n" + "=" * 80)
print("Data Quality Summary:")
print("=" * 80)

# Count how many have each field
total = len(listings)
has_price = sum(1 for l in listings if l.get('price'))
has_beds = sum(1 for l in listings if l.get('bedrooms') is not None)
has_baths = sum(1 for l in listings if l.get('bathrooms') is not None)

print(f"Listings with price: {has_price}/{total} ({has_price/total*100:.0f}%)")
print(f"Listings with bedrooms: {has_beds}/{total} ({has_beds/total*100:.0f}%)")
print(f"Listings with bathrooms: {has_baths}/{total} ({has_baths/total*100:.0f}%)")

# Show price and bedroom distribution
prices = [l['price'] for l in listings if l.get('price')]
beds = [l['bedrooms'] for l in listings if l.get('bedrooms') is not None]

if prices:
    print(f"\nPrice range: ${min(prices):,.0f} - ${max(prices):,.0f}")

if beds:
    from collections import Counter
    bed_counts = Counter(beds)
    print(f"\nBedroom distribution:")
    for bed_count in sorted(bed_counts.keys()):
        count = bed_counts[bed_count]
        bed_label = "Studio" if bed_count == 0 else f"{int(bed_count) if bed_count.is_integer() else bed_count} bed"
        print(f"  {bed_label}: {count} listings")
