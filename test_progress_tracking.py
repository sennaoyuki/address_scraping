#!/usr/bin/env python3
"""
進捗状況の追跡をテスト
"""

from clinic_info_scraper import ClinicInfoScraper
import time

test_url = "https://www.rizeclinic.com/locations/"

scraper = ClinicInfoScraper()

print("=== スクレイピング開始前 ===")
print(f"Progress: {scraper.get_progress()}")

# スクレイピングを開始
print("\n=== スクレイピング実行 ===")
success = scraper.scrape_clinics(test_url)

print("\n=== スクレイピング完了後 ===")
print(f"Success: {success}")
print(f"Progress: {scraper.get_progress()}")
print(f"Clinic data count: {len(scraper.clinic_data)}")

# 最初の3件のデータを表示
if scraper.clinic_data:
    print("\n=== 最初の3件のデータ ===")
    for i, clinic in enumerate(scraper.clinic_data[:3]):
        print(f"{i+1}. {clinic['name']}")
        print(f"   住所: {clinic['address']}")
        print(f"   アクセス: {clinic['access']}")