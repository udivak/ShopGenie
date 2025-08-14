#!/usr/bin/env python3
"""
Test runner for all ShopGenie tests.
Run this script to execute all test files in the tests directory.
"""
import asyncio
import sys
import os
from pathlib import Path
import importlib.util

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test_file(test_file):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Import and run the test module
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if the module has a main function or async main
        if hasattr(module, 'test_bot_creation'):
            # For test_bot_startup.py
            result = asyncio.run(module.test_bot_creation())
            return result
        elif hasattr(module, 'test_ebay_api'):
            # For test_ebay_api.py
            asyncio.run(module.test_ebay_api())
            return True
        elif hasattr(module, 'test_human_scraper'):
            # For test_human_scraper.py
            asyncio.run(module.test_human_scraper())
            return True
        elif hasattr(module, 'test_aliexpress_integration'):
            # For test_aliexpress_integration.py
            result = asyncio.run(module.test_aliexpress_integration())
            return result
        elif hasattr(module, 'BotTester'):
            # For test_bot.py
            tester = module.BotTester()
            # Run basic tests
            config_ok = tester.test_configuration()
            if config_ok:
                print("✅ Basic bot tests passed")
                return True
            else:
                print("❌ Basic bot tests failed")
                return False
        else:
            print(f"⚠️  No known test function found in {test_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all test files in the tests directory."""
    print("🧪 ShopGenie Test Suite")
    print("=" * 60)
    
    # Get all test files
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found!")
        return
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  • {test_file.name}")
    
    # Run each test
    results = []
    for test_file in test_files:
        if test_file.name != "run_all_tests.py":  # Skip this file
            result = run_test_file(test_file)
            results.append((test_file.name, result))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1
    
    print(f"\n🎯 Total: {len(results)} tests")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
