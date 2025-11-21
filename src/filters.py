"""
Filter module for applying search criteria to housing listings.
Filters listings based on price, bedrooms, bathrooms, and other criteria.
"""

from typing import List, Dict, Optional
from src.config import Config


class ListingFilter:
    """Filters housing listings based on user-defined criteria."""

    def __init__(self, config: Config):
        """
        Initialize filter with configuration.

        Args:
            config: Configuration object with search criteria.
        """
        self.config = config

    def matches_criteria(self, listing: Dict) -> bool:
        """
        Check if a listing matches all filter criteria.

        Args:
            listing: Dictionary containing listing information.

        Returns:
            True if listing matches all criteria, False otherwise.
        """
        # Price filter
        if not self._matches_price(listing.get('price')):
            return False

        # Bedrooms filter
        if not self._matches_bedrooms(listing.get('bedrooms')):
            return False

        # Bathrooms filter
        if not self._matches_bathrooms(listing.get('bathrooms')):
            return False

        # Square feet filter
        if not self._matches_square_feet(listing.get('square_feet')):
            return False

        return True

    def _matches_price(self, price: Optional[float]) -> bool:
        """Check if price is within the configured range."""
        # Allow listings without price - they'll be enriched in Phase 2
        if price is None:
            return True

        min_price = self.config.min_price
        max_price = self.config.max_price

        if min_price is not None and price < min_price:
            return False

        if max_price is not None and price > max_price:
            return False

        return True

    def _matches_bedrooms(self, bedrooms: Optional[int]) -> bool:
        """Check if bedrooms count is within the configured range."""
        # Allow listings without bedroom info - they'll be enriched in Phase 2
        if bedrooms is None:
            return True

        min_bedrooms = self.config.min_bedrooms
        max_bedrooms = self.config.max_bedrooms

        if min_bedrooms is not None and bedrooms < min_bedrooms:
            return False

        if max_bedrooms is not None and bedrooms > max_bedrooms:
            return False

        return True

    def _matches_bathrooms(self, bathrooms: Optional[float]) -> bool:
        """Check if bathrooms count is within the configured range."""
        # Bathroom data is rarely shown on search pages, so we allow None values
        # This means we can't filter by bathrooms effectively from search results alone
        if bathrooms is None:
            return True  # Allow listings without bathroom info

        min_bathrooms = self.config.min_bathrooms
        max_bathrooms = self.config.max_bathrooms

        if min_bathrooms is not None and bathrooms < min_bathrooms:
            return False

        if max_bathrooms is not None and bathrooms > max_bathrooms:
            return False

        return True

    def _matches_square_feet(self, square_feet: Optional[int]) -> bool:
        """Check if square feet is within the configured range."""
        # Allow listings without square feet - they may be enriched in Phase 2
        if square_feet is None:
            return True

        min_square_feet = self.config.min_square_feet
        max_square_feet = self.config.max_square_feet

        if min_square_feet is not None and square_feet < min_square_feet:
            return False

        if max_square_feet is not None and square_feet > max_square_feet:
            return False

        return True

    def filter_listings(self, listings: List[Dict]) -> List[Dict]:
        """
        Filter a list of listings based on criteria.

        Args:
            listings: List of listing dictionaries.

        Returns:
            List of listings that match all criteria.
        """
        return [
            listing for listing in listings
            if self.matches_criteria(listing)
        ]

    def get_filter_summary(self) -> str:
        """Get a human-readable summary of active filters."""
        parts = []

        # Location
        parts.append(f"Location: {self.config.location}")

        # Price
        if self.config.min_price and self.config.max_price:
            parts.append(f"Price: ${self.config.min_price:,.0f} - ${self.config.max_price:,.0f}")
        elif self.config.min_price:
            parts.append(f"Price: ${self.config.min_price:,.0f}+")
        elif self.config.max_price:
            parts.append(f"Price: Up to ${self.config.max_price:,.0f}")

        # Bedrooms
        if self.config.min_bedrooms and self.config.max_bedrooms:
            parts.append(f"Bedrooms: {self.config.min_bedrooms} - {self.config.max_bedrooms}")
        elif self.config.min_bedrooms:
            parts.append(f"Bedrooms: {self.config.min_bedrooms}+")
        elif self.config.max_bedrooms:
            parts.append(f"Bedrooms: Up to {self.config.max_bedrooms}")

        # Bathrooms
        if self.config.min_bathrooms and self.config.max_bathrooms:
            parts.append(f"Bathrooms: {self.config.min_bathrooms} - {self.config.max_bathrooms}")
        elif self.config.min_bathrooms:
            parts.append(f"Bathrooms: {self.config.min_bathrooms}+")
        elif self.config.max_bathrooms:
            parts.append(f"Bathrooms: Up to {self.config.max_bathrooms}")

        # Square Feet
        if self.config.min_square_feet and self.config.max_square_feet:
            parts.append(f"Sq Ft: {self.config.min_square_feet:,} - {self.config.max_square_feet:,}")
        elif self.config.min_square_feet:
            parts.append(f"Sq Ft: {self.config.min_square_feet:,}+")
        elif self.config.max_square_feet:
            parts.append(f"Sq Ft: Up to {self.config.max_square_feet:,}")

        return " | ".join(parts)
