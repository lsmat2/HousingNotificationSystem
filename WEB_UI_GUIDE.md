# Web UI Guide

## Quick Start

### Starting the Web UI

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the web server
python src/web_ui.py
```

The server will start at: **http://127.0.0.1:5000**

Open this URL in your web browser to view the interface.

### To Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## Features

### 1. **View All Listings**
- Shows all scraped housing listings in a clean, card-based layout
- Each card displays:
  - Property title
  - Price per month
  - Number of bedrooms and bathrooms
  - **How long it's been tracked** (color-coded by age)

### 2. **Track Duration**
The tracking duration is automatically calculated and displayed for each listing:
- **Green badge**: Recently added (< 1 day)
- **Yellow badge**: Medium age (1-7 days)
- **Red badge**: Older listings (> 7 days)

Examples:
- "3 days ago"
- "2 hours ago"
- "45 minutes ago"

### 3. **Favorite Listings**
- Click the **☆ (star) button** on any listing to mark it as a favorite
- Favorited listings show a **⭐ (filled star)**
- Click again to unfavorite
- Filter view to show only favorites

### 4. **Expand for Details**
- Click the **▼ arrow** to expand a listing card
- Shows full details:
  - Complete address
  - Square footage
  - Availability date
  - First seen / Last seen timestamps
  - Whether you've been notified
  - Direct link to Apartments.com listing

### 5. **Filtering**
- **All Listings**: View everything in the database
- **Favorites**: Show only your starred listings

### 6. **Sorting**
Sort listings by:
- **Newest First**: Most recently added listings first
- **Oldest First**: Longest tracked listings first
- **Price (High to Low)**: Most expensive first
- **Price (Low to High)**: Cheapest first

## Stats Header

The header shows quick statistics:
- **Total**: Total number of listings tracked
- **Favorites**: Number of favorited listings
- **New**: Unnotified listings (not yet shown in previous notifications)

## Tips

1. **Favorites are persistent**: Your favorites are saved in the database and will persist across sessions

2. **Refresh for updates**: If you run the scraper while the web UI is open, refresh the page to see new listings

3. **Mobile friendly**: The interface is responsive and works on mobile devices

4. **Background running**: You can keep the web server running in the background:
   ```bash
   # Start in background
   python src/web_ui.py &

   # Or use nohup for persistent background running
   nohup python src/web_ui.py > web_ui.log 2>&1 &
   ```

## Workflow

### Typical Usage:

1. **Run the scraper** to collect new listings:
   ```bash
   python -m src.main
   ```

2. **Start the web UI** to view and manage listings:
   ```bash
   python src/web_ui.py
   ```

3. **Open browser** to http://127.0.0.1:5000

4. **Browse listings**, favorite ones you like

5. **Visit favorites** to review your shortlist

6. **Click "View on Apartments.com"** to see full details and apply

## Database

All favorites and tracking data are stored in your SQLite database (`data/listings.db`). The web UI automatically:
- Adds the `favorited` column if it doesn't exist (for existing databases)
- Updates favorites in real-time when you click the star button
- Preserves all existing scraper functionality

## Troubleshooting

**"Address already in use" error:**
- Another process is using port 5000
- Kill the existing process or use a different port:
  ```bash
  # Custom port
  python -c "from src.web_ui import run_web_ui; run_web_ui(port=5001)"
  ```

**"No listings found" message:**
- Run the scraper first: `python -m src.main`
- Make sure your database has data

**Favorites not saving:**
- Check database permissions
- Ensure `data/listings.db` is writable

## Next Steps

Once you've identified promising listings:
1. Click "View on Apartments.com" to see full details
2. Contact landlords/property managers directly
3. Schedule viewings
4. Keep the web UI open to track which listings persist over time (may indicate vacancy)
