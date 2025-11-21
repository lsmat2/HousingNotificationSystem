"""
Web UI for viewing and managing scraped housing listings.
Simple Flask application for tracking and favoriting listings.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from typing import List, Dict
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import ListingDatabase
from src.config import Config

# Get the parent directory (project root) for templates and static files
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(parent_dir, 'templates')
static_dir = os.path.join(parent_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize database
config = Config()
db = ListingDatabase(config.db_path)


def calculate_duration(first_seen_str: str) -> Dict:
    """
    Calculate how long a listing has been tracked.

    Returns dict with human-readable duration and color code.
    """
    first_seen = datetime.fromisoformat(first_seen_str)
    now = datetime.now()
    delta = now - first_seen

    # Calculate duration
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    # Format human-readable string
    if days > 0:
        duration_str = f"{days} day{'s' if days != 1 else ''} ago"
        color = "old" if days > 7 else "medium"
    elif hours > 0:
        duration_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
        color = "new"
    else:
        duration_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        color = "new"

    return {
        'text': duration_str,
        'color': color,
        'days': days,
        'hours': hours
    }


@app.route('/')
def index():
    """Main listings page."""
    # Get filter and sort parameters
    show_favorites = request.args.get('favorites', 'false') == 'true'
    sort_by = request.args.get('sort', 'newest')

    # Get listings
    if show_favorites:
        listings = db.get_favorited_listings()
    else:
        listings = db.get_all_listings()

    # Sort listings
    if sort_by == 'newest':
        listings.sort(key=lambda x: x['first_seen'], reverse=True)
    elif sort_by == 'oldest':
        listings.sort(key=lambda x: x['first_seen'])
    elif sort_by == 'price_high':
        listings.sort(key=lambda x: x['price'] or 0, reverse=True)
    elif sort_by == 'price_low':
        listings.sort(key=lambda x: x['price'] or 0)

    # Add duration to each listing
    for listing in listings:
        listing['duration'] = calculate_duration(listing['first_seen'])

    # Group listings by neighborhood
    neighborhoods = {}
    for listing in listings:
        neighborhood = listing.get('neighborhood') or 'Unknown'
        if neighborhood not in neighborhoods:
            neighborhoods[neighborhood] = []
        neighborhoods[neighborhood].append(listing)

    # Get stats
    stats = db.get_stats()

    return render_template(
        'index.html',
        neighborhoods=neighborhoods,
        stats=stats,
        show_favorites=show_favorites,
        sort_by=sort_by
    )


@app.route('/toggle_favorite/<listing_id>', methods=['POST'])
def toggle_favorite(listing_id):
    """Toggle favorite status of a listing."""
    new_status = db.toggle_favorite(listing_id)
    return jsonify({'success': True, 'favorited': new_status})


@app.route('/stats')
def stats():
    """Get current statistics."""
    stats = db.get_stats()
    return jsonify(stats)


def run_web_ui(host='127.0.0.1', port=5000, debug=True):
    """Run the Flask web UI."""
    print("=" * 80)
    print("Housing Listings Tracker - Web UI")
    print("=" * 80)
    print(f"\nStarting web server at: http://{host}:{port}")
    print("Press Ctrl+C to stop")
    print()

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_web_ui()
