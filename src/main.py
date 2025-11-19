"""
Main orchestrator for the Housing Notification System.
Coordinates scraping, filtering, storage, and notifications.
"""

import argparse
import logging
import sys
from typing import List, Dict

from src.config import Config
from src.database import ListingDatabase
from src.scraper import ApartmentsScraper
from src.filters import ListingFilter
from src.notifications import NotificationService


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HousingNotificationSystem:
    """Main system coordinator."""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the housing notification system.

        Args:
            config_path: Path to configuration file.
        """
        try:
            self.config = Config(config_path)
            self.config.validate()
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)

        self.db = ListingDatabase(self.config.db_path)
        self.scraper = ApartmentsScraper(self.config)
        self.filter = ListingFilter(self.config)
        self.notifier = NotificationService(self.config)

    def run(self, max_pages: int = 3, dry_run: bool = False):
        """
        Run the complete notification cycle.

        Args:
            max_pages: Maximum number of pages to scrape.
            dry_run: If True, don't save to database or send notifications.
        """
        logger.info("=" * 80)
        logger.info("Starting Housing Notification System")
        logger.info("=" * 80)

        # Display search criteria
        logger.info(f"Search Criteria: {self.filter.get_filter_summary()}")
        logger.info("")

        # Step 1: Scrape listings
        logger.info("Step 1: Scraping Apartments.com...")
        raw_listings = self.scraper.scrape_listings(max_pages=max_pages)

        if not raw_listings:
            logger.warning("No listings found. The scraper may need adjustment.")
            return

        logger.info(f"Found {len(raw_listings)} total listings")

        # Step 2: Filter listings
        logger.info("\nStep 2: Applying filters...")
        filtered_listings = self.filter.filter_listings(raw_listings)
        filtered_out_count = len(raw_listings) - len(filtered_listings)

        logger.info(f"Listings matching criteria: {len(filtered_listings)}")
        logger.info(f"Listings filtered out: {filtered_out_count}")

        if not filtered_listings:
            logger.info("No listings match your criteria.")
            return

        # Step 3: Check for new listings
        logger.info("\nStep 3: Checking for new listings...")
        new_listings = self._identify_new_listings(filtered_listings, dry_run)

        logger.info(f"New listings (not seen before): {len(new_listings)}")

        # Step 4: Send notifications
        if new_listings and not dry_run:
            logger.info("\nStep 4: Sending notifications...")
            notified_count = self.notifier.send_notifications(new_listings)

            # Mark listings as notified
            for listing in new_listings[:notified_count]:
                self.db.mark_as_notified(listing['listing_id'])

            logger.info(f"Notifications sent for {notified_count} listings")
        elif new_listings and dry_run:
            logger.info("\nStep 4: [DRY RUN] Would send notifications for:")
            for listing in new_listings[:5]:  # Show first 5
                logger.info(f"  - {listing.get('title', 'Unknown')} - ${listing.get('price', 'N/A')}")
            if len(new_listings) > 5:
                logger.info(f"  ... and {len(new_listings) - 5} more")
        else:
            logger.info("\nStep 4: No new listings to notify about")

        # Step 5: Cleanup old data
        if not dry_run:
            logger.info("\nStep 5: Cleaning up old listings...")
            deleted_count = self.db.cleanup_old_listings(self.config.retention_days)
            logger.info(f"Removed {deleted_count} listings older than {self.config.retention_days} days")

        # Display statistics
        self._display_statistics()

        logger.info("\n" + "=" * 80)
        logger.info("Housing Notification System completed")
        logger.info("=" * 80)

    def _identify_new_listings(self, listings: List[Dict], dry_run: bool = False) -> List[Dict]:
        """
        Identify which listings are new (not in database).

        Args:
            listings: List of filtered listings.
            dry_run: If True, don't add to database.

        Returns:
            List of new listings.
        """
        new_listings = []

        for listing in listings:
            if dry_run:
                # In dry run, just check without adding
                if not self.db.listing_exists(listing['listing_id']):
                    new_listings.append(listing)
            else:
                # Add to database, returns True if new
                is_new = self.db.add_listing(listing)
                if is_new:
                    new_listings.append(listing)

        return new_listings

    def _display_statistics(self):
        """Display database statistics."""
        stats = self.db.get_stats()

        logger.info("\n" + "-" * 80)
        logger.info("Database Statistics:")
        logger.info(f"  Total listings tracked: {stats['total_listings']}")
        logger.info(f"  Previously notified: {stats['notified_listings']}")
        logger.info(f"  Pending notification: {stats['unnotified_listings']}")
        logger.info("-" * 80)

    def show_recent_listings(self, limit: int = 10):
        """Display recent listings from database."""
        listings = self.db.get_all_listings(limit=limit)

        if not listings:
            print("No listings in database yet.")
            return

        print(f"\n{'=' * 80}")
        print(f"Recent Listings (last {limit})")
        print(f"{'=' * 80}\n")

        for i, listing in enumerate(listings, 1):
            print(f"{i}. {listing.get('title', 'Unknown')}")
            print(f"   Price: ${listing.get('price', 0):,.0f} | "
                  f"Beds: {listing.get('bedrooms', 'N/A')} | "
                  f"Baths: {listing.get('bathrooms', 'N/A')}")
            print(f"   First seen: {listing['first_seen']}")
            print(f"   Notified: {'Yes' if listing['notified'] else 'No'}")
            print(f"   URL: {listing['url']}")
            print()


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Housing Notification System - Monitor apartment listings'
    )

    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=3,
        help='Maximum number of pages to scrape (default: 3)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without saving to database or sending notifications'
    )

    parser.add_argument(
        '--show-recent',
        type=int,
        metavar='N',
        help='Show N most recent listings from database and exit'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics and exit'
    )

    args = parser.parse_args()

    # Initialize system
    system = HousingNotificationSystem(config_path=args.config)

    # Handle different modes
    if args.show_recent:
        system.show_recent_listings(limit=args.show_recent)
    elif args.stats:
        system._display_statistics()
    else:
        system.run(max_pages=args.pages, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
