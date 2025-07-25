#!/usr/bin/env python3
"""
Test script for Universal Store Information Scraper
Demonstrates the scraper's ability to extract store information from various websites
"""

import requests
from bs4 import BeautifulSoup
from universal_scraper import UniversalStoreScraper
import json


def test_url(url, description):
    """Test the universal scraper with a given URL"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Use the universal scraper
        scraper = UniversalStoreScraper()
        result = scraper.extract_store_info(soup, url)
        
        # Display results
        print("\nExtracted Information:")
        print(f"  Store Name: {result['name']}")
        print(f"  Address: {result['address']}")
        print(f"  Access: {result['access']}")
        print(f"  Phone: {result.get('phone', 'Not found')}")
        print(f"  Hours: {result.get('hours', 'Not found')}")
        
        if 'confidence_scores' in result:
            print("\nConfidence Scores:")
            for field, score in result['confidence_scores'].items():
                print(f"  {field}: {score}%")
        
    except Exception as e:
        print(f"Error: {str(e)}")


def main():
    """Main test function"""
    print("Universal Store Information Scraper Test")
    print("This demonstrates the scraper's ability to work with any website")
    
    # Test URLs (replace with actual URLs you want to test)
    test_cases = [
        # You can add test URLs here
        # ("https://example.com/store", "Example Store"),
    ]
    
    if not test_cases:
        print("\nTo test the scraper, add URLs to the test_cases list in the main() function.")
        print("Example:")
        print('  test_cases = [')
        print('      ("https://example.com/store", "Example Store"),')
        print('      ("https://clinic.example.com/locations", "Example Clinic"),')
        print('  ]')
        
        # Interactive mode
        while True:
            url = input("\nEnter a URL to test (or 'quit' to exit): ").strip()
            if url.lower() == 'quit':
                break
            if url:
                test_url(url, "User-provided URL")
    else:
        for url, description in test_cases:
            test_url(url, description)


if __name__ == "__main__":
    main()