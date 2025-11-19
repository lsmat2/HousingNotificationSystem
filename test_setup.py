"""
Simple test script to verify the Housing Notification System setup.
Run this to check if all dependencies are installed and configuration is valid.
"""

import sys
import os


def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    errors = []

    try:
        import requests
        print("✓ requests")
    except ImportError:
        errors.append("requests")
        print("✗ requests - MISSING")

    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4")
    except ImportError:
        errors.append("beautifulsoup4")
        print("✗ beautifulsoup4 - MISSING")

    try:
        import lxml
        print("✓ lxml")
    except ImportError:
        errors.append("lxml")
        print("✗ lxml - MISSING")

    try:
        import selenium
        print("✓ selenium")
    except ImportError:
        errors.append("selenium")
        print("✗ selenium - MISSING")

    try:
        import sqlite3
        print("✓ sqlite3 (built-in)")
    except ImportError:
        errors.append("sqlite3")
        print("✗ sqlite3 - MISSING (should be built-in)")

    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError:
        errors.append("python-dotenv")
        print("✗ python-dotenv - MISSING")

    if errors:
        print(f"\n❌ Missing dependencies: {', '.join(errors)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True


def test_config():
    """Test if configuration file exists and is valid."""
    print("\nTesting configuration...")

    if not os.path.exists('config.json'):
        print("✗ config.json not found")
        return False

    print("✓ config.json exists")

    try:
        from src.config import Config
        config = Config('config.json')
        print("✓ Configuration loaded successfully")

        config.validate()
        print("✓ Configuration is valid")

        print(f"\nCurrent search criteria:")
        print(f"  Location: {config.location}")
        print(f"  Price: ${config.min_price or 'any'} - ${config.max_price or 'any'}")
        print(f"  Bedrooms: {config.min_bedrooms or 'any'} - {config.max_bedrooms or 'any'}")
        print(f"  Bathrooms: {config.min_bathrooms or 'any'} - {config.max_bathrooms or 'any'}")

        return True

    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_database():
    """Test database initialization."""
    print("\nTesting database...")

    try:
        from src.database import ListingDatabase

        # Use a test database
        test_db_path = "data/test_listings.db"
        db = ListingDatabase(test_db_path)
        print("✓ Database initialized successfully")

        # Test basic operations
        test_listing = {
            'listing_id': 'test123',
            'url': 'https://example.com/listing/test123',
            'title': 'Test Apartment',
            'address': '123 Test St',
            'price': 2000,
            'bedrooms': 2,
            'bathrooms': 1.5,
            'square_feet': 900,
            'availability_date': 'Now'
        }

        db.add_listing(test_listing)
        print("✓ Database write operation successful")

        exists = db.listing_exists('test123')
        if exists:
            print("✓ Database read operation successful")
        else:
            print("✗ Database read operation failed")
            return False

        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print("✓ Test database cleaned up")

        return True

    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_src_modules():
    """Test if all source modules can be imported."""
    print("\nTesting source modules...")
    errors = []

    modules = [
        'src.config',
        'src.database',
        'src.scraper',
        'src.filters',
        'src.notifications',
        'src.main'
    ]

    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            errors.append(f"{module}: {e}")
            print(f"✗ {module} - ERROR: {e}")

    if errors:
        print(f"\n❌ Module import errors found")
        return False
    else:
        print("\n✅ All source modules imported successfully!")
        return True


def main():
    """Run all tests."""
    print("=" * 80)
    print("Housing Notification System - Setup Test")
    print("=" * 80)
    print()

    results = []

    results.append(("Dependencies", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Source Modules", test_src_modules()))
    results.append(("Database", test_database()))

    print("\n" + "=" * 80)
    print("Test Summary:")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("Run the system with: python -m src.main")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
