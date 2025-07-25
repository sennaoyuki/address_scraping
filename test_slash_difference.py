#!/usr/bin/env python3
"""
末尾のスラッシュの違いをテスト
"""

from clinic_info_scraper import ClinicInfoScraper

# 末尾にスラッシュがない場合
test_url_no_slash = "https://www.rizeclinic.com/locations"
scraper1 = ClinicInfoScraper()

print("=== スラッシュなしの場合 ===")
print(f"URL: {test_url_no_slash}")
success1 = scraper1.scrape_clinics(test_url_no_slash)
print(f"成功: {success1}")
print(f"取得した店舗数: {len(scraper1.clinic_data)}")
print(f"ステータス: {scraper1.status}")
print(f"現在のアクション: {scraper1.current_action}")

print("\n" + "="*50 + "\n")

# 末尾にスラッシュがある場合
test_url_with_slash = "https://www.rizeclinic.com/locations/"
scraper2 = ClinicInfoScraper()

print("=== スラッシュありの場合 ===")
print(f"URL: {test_url_with_slash}")
success2 = scraper2.scrape_clinics(test_url_with_slash)
print(f"成功: {success2}")
print(f"取得した店舗数: {len(scraper2.clinic_data)}")
print(f"ステータス: {scraper2.status}")
print(f"現在のアクション: {scraper2.current_action}")