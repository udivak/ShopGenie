# ShopGenie Tests

This directory contains all test files for the ShopGenie project.

## Test Files

- **`test_bot.py`** - Comprehensive bot functionality tests
- **`test_bot_startup.py`** - Quick bot startup verification
- **`test_ebay_api.py`** - eBay API integration tests
- **`test_aliexpress_integration.py`** - AliExpress API integration tests
- **`test_human_scraper.py`** - Human-like AliExpress scraper tests
- **`run_all_tests.py`** - Test runner to execute all tests

## Running Tests

### Run All Tests
```bash
cd tests
python run_all_tests.py
```

### Run Individual Tests
```bash
# Bot tests
python tests/test_bot.py
python tests/test_bot_startup.py

# API integration tests
python tests/test_ebay_api.py
python tests/test_aliexpress_integration.py

# Scraper tests
python tests/test_human_scraper.py
```

### From Project Root
```bash
# Run all tests
python tests/run_all_tests.py

# Run individual tests
python tests/test_bot_startup.py
```

## Test Requirements

Before running tests, ensure you have:

1. **Environment variables configured** in your `.env` file:
   - `TELEGRAM_BOT_TOKEN` for bot tests
   - `ALIEXPRESS_APP_KEY` and `ALIEXPRESS_APP_SECRET` for AliExpress tests
   - `EBAY_APP_ID`, `EBAY_CERT_ID`, `EBAY_DEV_ID` for eBay tests

2. **Dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Virtual environment activated** (if using one):
   ```bash
   source shopgenie_env/bin/activate
   ```

## Test Categories

### 🔧 Configuration Tests
- Verify environment variables are set
- Check configuration loading
- Validate API credentials

### 🤖 Bot Tests
- Bot creation and initialization
- Message handling
- Command processing
- Error handling

### 🔍 Scraper Tests
- API integration verification
- Search functionality
- Product data extraction
- Error handling and retries

### 🌐 Platform Tests
- AliExpress API integration
- eBay API integration
- Human-like scraping (no API required)

## Adding New Tests

When adding new test files:

1. Follow the naming convention: `test_*.py`
2. Update import paths to use the parent directory:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   ```
3. Add the test function to `run_all_tests.py` if it should be included in the test suite
4. Update this README with the new test description

## Troubleshooting

### Import Errors
If you encounter import errors, ensure:
- You're running tests from the project root directory
- The virtual environment is activated
- All dependencies are installed

### Configuration Errors
If tests fail due to missing configuration:
- Check your `.env` file exists and has required variables
- Verify API credentials are valid
- Ensure the environment is properly set up

### Network Errors
Some tests require internet connectivity:
- AliExpress and eBay API tests need internet access
- Human scraper tests may be rate-limited
- Consider using mock data for offline testing
