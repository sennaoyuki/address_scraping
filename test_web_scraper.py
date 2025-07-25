#!/usr/bin/env python3
"""
ウェブアプリと同じ方法でスクレイパーをテスト
"""

from clinic_info_scraper import ClinicInfoScraper

# ウェブアプリで使われているURLを正確に使用
test_url = "https://www.rizeclinic.com/locations/"

scraper = ClinicInfoScraper()

print(f"URL: {test_url}")
print("スクレイピングを開始...")

success = scraper.scrape_clinics(test_url)

print(f"\n=== 結果 ===")
print(f"成功: {success}")
print(f"ステータス: {scraper.status}")
print(f"現在のアクション: {scraper.current_action}")
print(f"取得した店舗数: {len(scraper.clinic_data)}")

# 検出されたリンクを直接確認
import requests
from bs4 import BeautifulSoup

response = requests.get(test_url, headers=scraper.headers)
soup = BeautifulSoup(response.content, 'html.parser')

# まず現在のページから情報を抽出
current_page_info = scraper.extract_clinic_info(soup, test_url)
print(f"\n現在のページの情報:")
print(f"  名前: {current_page_info['name']}")
print(f"  住所: {current_page_info['address']}")
print(f"  アクセス: {current_page_info['access']}")

# リンクを検出
clinic_links = scraper.find_clinic_links(soup, test_url)
print(f"\n検出されたリンク数: {len(clinic_links)}")
if clinic_links:
    print("最初の5つ:")
    for i, link in enumerate(clinic_links[:5]):
        print(f"  {i+1}. {link['name']} -> {link['url']}")

# 最初のページと同じページか確認
print(f"\n最初のページと同じか?: ")
for i, link in enumerate(clinic_links[:3]):
    same = link['url'].rstrip('/') == test_url.rstrip('/')
    print(f"  {link['url']} == {test_url} ? {same}")