# Quick Start Guide

Get your Housing Notification System up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

## Step 2: Configure Your Search

Edit `config.json` with your preferences:

```json
{
  "search_criteria": {
    "location": "Your City, State",
    "price_range": {
      "min": 1000,
      "max": 2500
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

## Step 3: Test Your Setup

```bash
python test_setup.py
```

If all tests pass, you're ready to go!

## Step 4: Run the System

```bash
# First run (dry run to see what it finds)
python -m src.main --dry-run

# Actual run (saves to database and sends notifications)
python -m src.main
```

## Step 5: Schedule Regular Checks

### Mac/Linux (using cron)

```bash
# Edit crontab
crontab -e

# Add this line to run every 30 minutes
*/30 * * * * cd /path/to/HousingNotificationSystem && /path/to/venv/bin/python -m src.main
```

### Windows (using Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily, repeat every 30 minutes
4. Action: Start program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `-m src.main`
   - Start in: `C:\path\to\HousingNotificationSystem`

## Common Commands

```bash
# Run with more pages
python -m src.main --pages 5

# Show recent listings
python -m src.main --show-recent 20

# Show statistics
python -m src.main --stats

# Dry run (test without saving)
python -m src.main --dry-run
```

## Troubleshooting

**No listings found?**
- Check your location format in `config.json` (should be "City, State")
- Try running with `--dry-run` first
- Check the logs for errors

**Too many/few results?**
- Adjust your price range, bedroom, and bathroom filters in `config.json`
- Use `null` for unlimited (e.g., `"max": null` means no maximum)

**Need help?**
- See the full README.md for detailed documentation
- Check that all dependencies installed: `python test_setup.py`

## Next Steps

Once you have notifications working:

1. **Refine your filters** - Adjust `config.json` to get more relevant results
2. **Set up scheduling** - Automate checks every 30-60 minutes
3. **Add SMS notifications** - See README.md for Twilio integration

---

**Need more details?** Check out the full [README.md](README.md)
