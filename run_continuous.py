"""
Continuous monitoring script for the Housing Notification System.
Runs the system in a loop with configurable intervals.
"""

import time
import argparse
import logging
from datetime import datetime
from src.main import HousingNotificationSystem


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_continuous(interval_minutes: int = 30, max_pages: int = 3, config_path: str = "config.json"):
    """
    Run the housing notification system continuously.

    Args:
        interval_minutes: Minutes to wait between checks
        max_pages: Maximum pages to scrape per run
        config_path: Path to configuration file
    """
    logger.info("=" * 80)
    logger.info("Starting Housing Notification System in CONTINUOUS mode")
    logger.info(f"Check interval: {interval_minutes} minutes")
    logger.info(f"Press Ctrl+C to stop")
    logger.info("=" * 80)
    print()

    system = HousingNotificationSystem(config_path=config_path)
    run_count = 0

    try:
        while True:
            run_count += 1
            logger.info(f"\n{'=' * 80}")
            logger.info(f"Run #{run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'=' * 80}\n")

            try:
                system.run(max_pages=max_pages, dry_run=False)
            except Exception as e:
                logger.error(f"Error during run #{run_count}: {e}", exc_info=True)
                logger.info("Continuing to next scheduled run...")

            # Wait for the specified interval
            logger.info(f"\n{'=' * 80}")
            logger.info(f"Waiting {interval_minutes} minutes until next check...")
            logger.info(f"Next run at: {datetime.fromtimestamp(time.time() + interval_minutes * 60).strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'=' * 80}\n")

            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        logger.info("\n\n" + "=" * 80)
        logger.info("Stopping continuous monitoring (Ctrl+C detected)")
        logger.info(f"Total runs completed: {run_count}")
        logger.info("=" * 80)


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Run Housing Notification System continuously'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Minutes between checks (default: 30)'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=3,
        help='Maximum pages to scrape per run (default: 3)'
    )

    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )

    args = parser.parse_args()

    # Validate interval
    if args.interval < 1:
        logger.error("Interval must be at least 1 minute")
        return

    if args.interval < 10:
        logger.warning(f"⚠️  Warning: {args.interval} minute interval is quite frequent.")
        logger.warning("   Consider using a longer interval (30-60 minutes) to be respectful")
        logger.warning("   of the website's resources and avoid potential rate limiting.")
        print()

        try:
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                logger.info("Cancelled by user")
                return
        except KeyboardInterrupt:
            logger.info("\nCancelled by user")
            return

    run_continuous(
        interval_minutes=args.interval,
        max_pages=args.pages,
        config_path=args.config
    )


if __name__ == '__main__':
    main()
