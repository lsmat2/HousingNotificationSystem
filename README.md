# Housing Notification System

A Python-based system that monitors Apartments.com for housing listings matching your criteria and sends notifications when new listings are found.

## Features

- **Automated Scraping**: Periodically scrapes Apartments.com for new listings
- **Neighborhood Targeting**: Search specific Chicago neighborhoods for more relevant results
- **Smart Filtering**: Filter by location, price range, bedrooms, and bathrooms
- **Web UI**: Simple browser interface to view, track, and favorite listings (NEW!)
- **Tracking Duration**: See how long each listing has been available
- **Deduplication**: Tracks seen listings to avoid duplicate notifications
- **Persistent Storage**: SQLite database for reliable listing history
- **Extensible Notifications**: Console output with framework for SMS integration
- **Configurable**: Easy-to-edit JSON configuration file
- **Command-line Interface**: Flexible CLI for various use cases

## Project Structure

```
HousingNotificationSystem/
├── src/
│   ├── main.py           # Main orchestrator
│   ├── scraper.py        # Apartments.com scraper
│   ├── filters.py        # Listing filter engine
│   ├── database.py       # SQLite database manager
│   ├── config.py         # Configuration management
│   └── notifications.py  # Notification system
├── data/
│   └── listings.db       # SQLite database (created automatically)
├── config.json           # Configuration file
├── requirements.txt      # Python dependencies
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd HousingNotificationSystem
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your search criteria**:
   Edit `config.json` with your preferences:
   ```json
   {
     "search_criteria": {
       "location": "San Francisco, CA",
       "price_range": {
         "min": 1500,
         "max": 3000
       },
       "bedrooms": {
         "min": 1,
         "max": 2
       },
       "bathrooms": {
         "min": 1,
         "max": null
       }
     }
   }
   ```

## Usage

### Basic Usage

Run a single scraping cycle:

```bash
python -m src.main
```

This will:
1. Scrape Apartments.com for listings matching your criteria
2. Filter results based on your preferences
3. Identify new listings not seen before
4. Display notifications in the console
5. Save listings to the database

### Web UI

View and manage your listings in a browser:

```bash
python src/web_ui.py
```

Then open http://127.0.0.1:5000 in your browser.

The web UI provides:
- **Visual listing cards** with all property details
- **Duration tracking** showing how long each listing has been available
- **Favorite system** to star listings you're interested in
- **Filtering** between all listings and favorites only
- **Sorting** by date or price
- **Expandable details** for full information on each listing

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for detailed usage instructions.

### Command-Line Options

```bash
# Run with custom config file
python -m src.main --config my_config.json

# Scrape more pages (default is 3)
python -m src.main --pages 5

# Dry run (don't save to database or send notifications)
python -m src.main --dry-run

# Show 10 most recent listings from database
python -m src.main --show-recent 10

# Show database statistics
python -m src.main --stats
```

### Scheduling Automatic Runs

To check for new listings periodically, use cron (Linux/Mac) or Task Scheduler (Windows).

#### Using Cron (Linux/Mac)

1. Open crontab editor:
   ```bash
   crontab -e
   ```

2. Add a line to run every 30 minutes:
   ```bash
   */30 * * * * cd /path/to/HousingNotificationSystem && /path/to/venv/bin/python -m src.main >> logs/cron.log 2>&1
   ```

3. Create logs directory:
   ```bash
   mkdir -p logs
   ```

#### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create a new Basic Task
3. Set trigger to repeat every 30 minutes
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `-m src.main`
   - Start in: `C:\path\to\HousingNotificationSystem`

## Configuration Options

### Search Criteria

| Setting | Description | Example |
|---------|-------------|---------|
| `location` | City and state to search | `"Seattle, WA"` |
| `neighborhoods` | Specific neighborhoods to search (optional) | `["lincoln-park", "wicker-park"]` |
| `price_range.min` | Minimum monthly rent | `1200` |
| `price_range.max` | Maximum monthly rent | `2500` |
| `bedrooms.min` | Minimum bedrooms | `1` |
| `bedrooms.max` | Maximum bedrooms | `3` |
| `bathrooms.min` | Minimum bathrooms | `1` |
| `bathrooms.max` | Maximum bathrooms | `2.5` |

**Notes:**
- Use `null` for any range value to make it unlimited (e.g., "at least 2 bedrooms, no maximum")
- Leave `neighborhoods` as an empty array `[]` to search the entire city
- Use neighborhood slugs (lowercase with hyphens): `"lincoln-park"` not `"Lincoln Park"`
- See [CHICAGO_NEIGHBORHOODS.md](CHICAGO_NEIGHBORHOODS.md) for a full list of Chicago neighborhoods

### Scraper Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `check_interval_minutes` | How often to check (for scheduling) | `30` |
| `max_retries` | Number of retry attempts on failure | `3` |
| `timeout_seconds` | HTTP request timeout | `30` |
| `user_agent` | Browser user agent string | Chrome UA |

### Notification Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `enabled` | Enable/disable notifications | `true` |
| `notification_type` | Notification method (`console` or `sms`) | `"console"` |
| `max_listings_per_notification` | Max listings to show | `10` |

### Database Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `db_path` | Path to SQLite database | `"data/listings.db"` |
| `retention_days` | Days to keep old listings | `30` |

## Database Schema

The system uses SQLite with the following schema:

```sql
CREATE TABLE listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    address TEXT,
    price REAL,
    bedrooms INTEGER,
    bathrooms REAL,
    square_feet INTEGER,
    availability_date TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notified BOOLEAN DEFAULT FALSE
);
```

## Future Enhancements: SMS Notifications

To add SMS notifications via Twilio:

1. **Install Twilio**:
   ```bash
   pip install twilio
   ```

2. **Add credentials to `.env`**:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   TWILIO_TO_NUMBER=+1987654321
   ```

3. **Update config.json**:
   ```json
   "notification_settings": {
     "notification_type": "sms"
   }
   ```

4. **Implement SMS in `notifications.py`** (see comments in the file for example code)

## Troubleshooting

### No listings found

The Apartments.com HTML structure may have changed. Check `scraper.py:parse_listings()` and update the CSS selectors if needed.

To debug:
```bash
python -m src.main --dry-run
```

Look at the logs to see what's being scraped.

### Listings not matching criteria

Check your `config.json` filters. Run with `--dry-run` to see what's being filtered out:

```bash
python -m src.main --dry-run
```

### Database errors

If you encounter database issues, you can reset by deleting the database file:

```bash
rm data/listings.db
```

The system will create a new database on the next run.

### Rate limiting

If you're being rate-limited by Apartments.com:

1. Reduce the number of pages scraped: `--pages 1`
2. Increase delays in `scraper.py` (currently 2 seconds between pages)
3. Run less frequently (every hour instead of every 30 minutes)

## Legal Considerations

- **Robots.txt**: Check Apartments.com's robots.txt and respect their crawling policies
- **Rate Limiting**: Be respectful with request frequency to avoid overloading their servers
- **Terms of Service**: Review Apartments.com's ToS regarding automated access
- **Personal Use**: This tool is designed for personal, non-commercial use

## Contributing

To extend this system:

1. **Add new data sources**: Create new scraper classes following the pattern in `scraper.py`
2. **Add notification channels**: Extend `notifications.py` with new notification types
3. **Add filters**: Enhance `filters.py` with additional filtering criteria
4. **Improve parsing**: Update selectors in `scraper.py` if website structure changes

## License

This is a personal project for educational and personal use. Use responsibly and in accordance with Apartments.com's terms of service.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Verify your `config.json` is valid JSON
4. Ensure all dependencies are installed

---

**Happy apartment hunting!** 🏠
