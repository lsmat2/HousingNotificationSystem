"""
Database module for managing listing storage and retrieval.
Uses SQLite for lightweight, local storage.
"""

import sqlite3
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ListingDatabase:
    """Manages SQLite database operations for housing listings."""

    def __init__(self, db_path: str = "data/listings.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path

        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    address TEXT,
                    neighborhood TEXT,
                    price REAL,
                    bedrooms INTEGER,
                    bathrooms REAL,
                    square_feet INTEGER,
                    availability_date TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notified BOOLEAN DEFAULT FALSE,
                    favorited BOOLEAN DEFAULT FALSE
                )
            """)

            # Create index on listing_id for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_listing_id
                ON listings(listing_id)
            """)

            # Create index on first_seen for cleanup operations
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_first_seen
                ON listings(first_seen)
            """)

            conn.commit()

        # Add columns if they don't exist (for existing databases)
        self._add_favorited_column_if_needed()
        self._add_neighborhood_column_if_needed()

    def _add_favorited_column_if_needed(self):
        """Add favorited column to existing databases."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Check if column exists
            cursor.execute("PRAGMA table_info(listings)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'favorited' not in columns:
                logger.info("Adding 'favorited' column to existing database")
                cursor.execute("ALTER TABLE listings ADD COLUMN favorited BOOLEAN DEFAULT FALSE")
                conn.commit()

    def _add_neighborhood_column_if_needed(self):
        """Add neighborhood column to existing databases."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Check if column exists
            cursor.execute("PRAGMA table_info(listings)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'neighborhood' not in columns:
                logger.info("Adding 'neighborhood' column to existing database")
                cursor.execute("ALTER TABLE listings ADD COLUMN neighborhood TEXT")
                conn.commit()

    def listing_exists(self, listing_id: str) -> bool:
        """Check if a listing already exists in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM listings WHERE listing_id = ?",
                (listing_id,)
            )
            count = cursor.fetchone()[0]
            return count > 0

    def add_listing(self, listing: Dict) -> bool:
        """
        Add a new listing to the database.

        Returns:
            True if listing was added (new), False if it already existed.
        """
        if self.listing_exists(listing['listing_id']):
            # Update last_seen timestamp
            self._update_last_seen(listing['listing_id'])
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO listings (
                    listing_id, url, title, address, neighborhood, price,
                    bedrooms, bathrooms, square_feet, availability_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                listing['listing_id'],
                listing['url'],
                listing.get('title'),
                listing.get('address'),
                listing.get('neighborhood'),
                listing.get('price'),
                listing.get('bedrooms'),
                listing.get('bathrooms'),
                listing.get('square_feet'),
                listing.get('availability_date')
            ))
            conn.commit()
            return True

    def _update_last_seen(self, listing_id: str):
        """Update the last_seen timestamp for an existing listing."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE listings SET last_seen = CURRENT_TIMESTAMP WHERE listing_id = ?",
                (listing_id,)
            )
            conn.commit()

    def mark_as_notified(self, listing_id: str):
        """Mark a listing as having been notified to the user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE listings SET notified = TRUE WHERE listing_id = ?",
                (listing_id,)
            )
            conn.commit()

    def get_unnotified_listings(self) -> List[Dict]:
        """Retrieve all listings that haven't been notified yet."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM listings
                WHERE notified = FALSE
                ORDER BY first_seen DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_all_listings(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve all listings from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM listings ORDER BY first_seen DESC"
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def cleanup_old_listings(self, retention_days: int = 30):
        """Remove listings older than the specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM listings WHERE first_seen < ?",
                (cutoff_date.isoformat(),)
            )
            deleted_count = cursor.rowcount
            conn.commit()

        return deleted_count

    def get_stats(self) -> Dict:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM listings")
            total_listings = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM listings WHERE notified = TRUE")
            notified_listings = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM listings WHERE notified = FALSE")
            unnotified_listings = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM listings WHERE favorited = TRUE")
            favorited_listings = cursor.fetchone()[0]

            return {
                'total_listings': total_listings,
                'notified_listings': notified_listings,
                'unnotified_listings': unnotified_listings,
                'favorited_listings': favorited_listings
            }

    def toggle_favorite(self, listing_id: str) -> bool:
        """
        Toggle the favorite status of a listing.

        Returns:
            New favorite status (True if now favorited, False if unfavorited)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get current status
            cursor.execute(
                "SELECT favorited FROM listings WHERE listing_id = ?",
                (listing_id,)
            )
            result = cursor.fetchone()

            if not result:
                return False

            new_status = not result[0]

            # Update status
            cursor.execute(
                "UPDATE listings SET favorited = ? WHERE listing_id = ?",
                (new_status, listing_id)
            )
            conn.commit()

            return new_status

    def get_favorited_listings(self) -> List[Dict]:
        """Retrieve all favorited listings."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM listings
                WHERE favorited = TRUE
                ORDER BY first_seen DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
