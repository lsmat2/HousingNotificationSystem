"""
Notification module for alerting users about new listings.
Currently supports console output, designed to be extended for SMS/email.
"""

import logging
from typing import List, Dict
from datetime import datetime
from src.config import Config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    """Manages notifications for new housing listings."""

    def __init__(self, config: Config):
        """
        Initialize notification service.

        Args:
            config: Configuration object with notification settings.
        """
        self.config = config

    def send_notifications(self, listings: List[Dict]) -> int:
        """
        Send notifications for new listings.

        Args:
            listings: List of listing dictionaries to notify about.

        Returns:
            Number of successful notifications sent.
        """
        if not self.config.notifications_enabled:
            logger.info("Notifications are disabled in config")
            return 0

        if not listings:
            logger.info("No new listings to notify about")
            return 0

        # Limit number of listings per notification
        max_listings = self.config.max_listings_per_notification
        listings_to_notify = listings[:max_listings]

        notification_type = self.config.notification_type

        if notification_type == 'console':
            return self._send_console_notification(listings_to_notify)
        elif notification_type == 'sms':
            return self._send_sms_notification(listings_to_notify)
        else:
            logger.warning(f"Unknown notification type: {notification_type}")
            return 0

    def _send_console_notification(self, listings: List[Dict]) -> int:
        """
        Send console/stdout notification.

        Args:
            listings: List of listings to display.

        Returns:
            Number of listings notified.
        """
        print("\n" + "=" * 80)
        print(f"🏠 NEW HOUSING LISTINGS FOUND - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")

        for i, listing in enumerate(listings, 1):
            print(f"Listing #{i}")
            print("-" * 80)

            if listing.get('title'):
                print(f"Property: {listing['title']}")

            if listing.get('address'):
                print(f"Address: {listing['address']}")

            if listing.get('price'):
                print(f"Price: ${listing['price']:,.0f}/month")

            # Bedrooms and Bathrooms
            bed_bath = []
            if listing.get('bedrooms') is not None:
                beds = listing['bedrooms']
                if beds == 0:
                    bed_bath.append("Studio")
                else:
                    bed_bath.append(f"{int(beds) if beds.is_integer() else beds} bed")

            if listing.get('bathrooms') is not None:
                baths = listing['bathrooms']
                bed_bath.append(f"{baths} bath")

            if bed_bath:
                print(f"Layout: {', '.join(bed_bath)}")

            if listing.get('square_feet'):
                print(f"Size: {listing['square_feet']:,.0f} sq ft")

            if listing.get('availability_date'):
                print(f"Available: {listing['availability_date']}")

            if listing.get('url'):
                print(f"URL: {listing['url']}")

            print()

        print("=" * 80)
        print(f"Total new listings: {len(listings)}")
        print("=" * 80 + "\n")

        return len(listings)

    def _send_sms_notification(self, listings: List[Dict]) -> int:
        """
        Send SMS notification (placeholder for future implementation).

        Args:
            listings: List of listings to send via SMS.

        Returns:
            Number of listings notified.
        """
        # TODO: Implement SMS notifications using Twilio or similar service
        # This is a placeholder for future SMS integration

        logger.warning("SMS notifications not yet implemented")
        logger.info("To implement SMS:")
        logger.info("1. Install twilio: pip install twilio")
        logger.info("2. Add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to .env")
        logger.info("3. Implement send_sms() method below")

        # For now, fall back to console notification
        logger.info("Falling back to console notification...")
        return self._send_console_notification(listings)

    def format_listing_for_sms(self, listing: Dict) -> str:
        """
        Format a single listing for SMS (compact format).

        Args:
            listing: Listing dictionary.

        Returns:
            Formatted string for SMS.
        """
        parts = []

        if listing.get('title'):
            parts.append(listing['title'])

        if listing.get('price'):
            parts.append(f"${listing['price']:,.0f}/mo")

        # Bed/bath info
        bed_bath = []
        if listing.get('bedrooms') is not None:
            beds = listing['bedrooms']
            bed_bath.append(f"{int(beds) if beds == int(beds) else beds}bd")

        if listing.get('bathrooms') is not None:
            bed_bath.append(f"{listing['bathrooms']}ba")

        if bed_bath:
            parts.append(' '.join(bed_bath))

        if listing.get('url'):
            parts.append(listing['url'])

        return ' | '.join(parts)

    def send_summary_notification(self, total_checked: int, new_found: int, filtered_out: int):
        """
        Send a summary notification after a scraping run.

        Args:
            total_checked: Total listings checked
            new_found: Number of new listings found
            filtered_out: Number of listings filtered out
        """
        print("\n" + "-" * 80)
        print(f"📊 SCRAPING SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 80)
        print(f"Total listings checked: {total_checked}")
        print(f"New listings found: {new_found}")
        print(f"Filtered out (didn't match criteria): {filtered_out}")
        print(f"Listings meeting criteria: {new_found - filtered_out}")
        print("-" * 80 + "\n")


# Example future SMS implementation with Twilio (commented out):
"""
from twilio.rest import Client
import os

def send_sms_via_twilio(message: str, to_number: str):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_=from_number,
        to=to_number
    )

    return message.sid
"""
