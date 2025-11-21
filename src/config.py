"""
Configuration module for managing application settings.
Loads settings from config.json and provides easy access to configuration values.
"""

import json
import os
from typing import Dict, Any, Optional


class Config:
    """Manages application configuration loaded from JSON file."""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration from JSON file.

        Args:
            config_path: Path to the configuration JSON file.
        """
        self.config_path = config_path
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                "Please create a config.json file based on the template."
            )

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def reload(self):
        """Reload configuration from file."""
        self.config_data = self._load_config()

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Example:
            config.get('search_criteria.location')
            config.get('scraper_settings.timeout_seconds', default=30)

        Args:
            key_path: Dot-separated path to the configuration value.
            default: Default value if key doesn't exist.

        Returns:
            Configuration value or default.
        """
        keys = key_path.split('.')
        value = self.config_data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    # Search Criteria Properties
    @property
    def location(self) -> str:
        """Get search location."""
        return self.get('search_criteria.location', '')

    @property
    def neighborhoods(self) -> list:
        """Get list of neighborhoods to search within."""
        return self.get('search_criteria.neighborhoods', [])

    @property
    def min_price(self) -> Optional[float]:
        """Get minimum price."""
        return self.get('search_criteria.price_range.min')

    @property
    def max_price(self) -> Optional[float]:
        """Get maximum price."""
        return self.get('search_criteria.price_range.max')

    @property
    def min_bedrooms(self) -> Optional[int]:
        """Get minimum bedrooms."""
        return self.get('search_criteria.bedrooms.min')

    @property
    def max_bedrooms(self) -> Optional[int]:
        """Get maximum bedrooms."""
        return self.get('search_criteria.bedrooms.max')

    @property
    def min_bathrooms(self) -> Optional[float]:
        """Get minimum bathrooms."""
        return self.get('search_criteria.bathrooms.min')

    @property
    def max_bathrooms(self) -> Optional[float]:
        """Get maximum bathrooms."""
        return self.get('search_criteria.bathrooms.max')

    @property
    def min_square_feet(self) -> Optional[int]:
        """Get minimum square feet."""
        return self.get('search_criteria.square_feet.min')

    @property
    def max_square_feet(self) -> Optional[int]:
        """Get maximum square feet."""
        return self.get('search_criteria.square_feet.max')

    # Scraper Settings Properties
    @property
    def check_interval_minutes(self) -> int:
        """Get check interval in minutes."""
        return self.get('scraper_settings.check_interval_minutes', 30)

    @property
    def max_retries(self) -> int:
        """Get maximum number of retries."""
        return self.get('scraper_settings.max_retries', 3)

    @property
    def timeout_seconds(self) -> int:
        """Get request timeout in seconds."""
        return self.get('scraper_settings.timeout_seconds', 30)

    @property
    def user_agent(self) -> str:
        """Get user agent string."""
        return self.get(
            'scraper_settings.user_agent',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

    @property
    def headless(self) -> bool:
        """Get headless browser mode setting."""
        return self.get('scraper_settings.headless', True)

    @property
    def parallel_neighborhoods(self) -> bool:
        """Get parallel neighborhood scraping setting."""
        return self.get('scraper_settings.parallel_neighborhoods', True)

    @property
    def detail_page_delay_min(self) -> int:
        """Get minimum delay between detail page requests (seconds)."""
        return self.get('scraper_settings.detail_page_delay_min', 5)

    @property
    def detail_page_delay_max(self) -> int:
        """Get maximum delay between detail page requests (seconds)."""
        return self.get('scraper_settings.detail_page_delay_max', 10)

    # Notification Settings Properties
    @property
    def notifications_enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self.get('notification_settings.enabled', True)

    @property
    def notification_type(self) -> str:
        """Get notification type (console, sms, etc.)."""
        return self.get('notification_settings.notification_type', 'console')

    @property
    def max_listings_per_notification(self) -> int:
        """Get maximum listings per notification."""
        return self.get('notification_settings.max_listings_per_notification', 10)

    # Database Settings Properties
    @property
    def db_path(self) -> str:
        """Get database file path."""
        return self.get('database_settings.db_path', 'data/listings.db')

    @property
    def retention_days(self) -> int:
        """Get data retention period in days."""
        return self.get('database_settings.retention_days', 30)

    def validate(self) -> bool:
        """
        Validate configuration settings.

        Returns:
            True if configuration is valid.

        Raises:
            ValueError if configuration is invalid.
        """
        errors = []

        # Validate location
        if not self.location:
            errors.append("Location is required in search_criteria")

        # Validate price range
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                errors.append("min_price cannot be greater than max_price")

        # Validate bedrooms
        if self.min_bedrooms is not None and self.max_bedrooms is not None:
            if self.min_bedrooms > self.max_bedrooms:
                errors.append("min_bedrooms cannot be greater than max_bedrooms")

        # Validate bathrooms
        if self.min_bathrooms is not None and self.max_bathrooms is not None:
            if self.min_bathrooms > self.max_bathrooms:
                errors.append("min_bathrooms cannot be greater than max_bathrooms")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(errors))

        return True

    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(location={self.location}, price={self.min_price}-{self.max_price})"
