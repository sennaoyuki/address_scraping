#!/usr/bin/env python3
"""
リゼクリニックの店舗情報スクレイピングテスト
"""

from clinic_info_scraper import ClinicInfoScraper

# リゼクリニックの店舗一覧URL
test_url = "https://www.rizeclinic.com/locations/"

scraper = ClinicInfoScraper()

print("リゼクリニックの店舗情報をスクレイピング中...")
success = scraper.scrape_clinics(test_url)

if success and scraper.clinic_data:
    csv_file = scraper.save_to_csv()
    print(f"\nCSVファイルを保存しました: {csv_file}")
    print(f"取得した店舗数: {len(scraper.clinic_data)}")
    
    # 結果を表示
    for clinic in scraper.clinic_data:
        print(f"\n店舗名: {clinic['name']}")
        print(f"住所: {clinic['address']}")
        print(f"アクセス: {clinic['access']}")
        print(f"URL: {clinic['url']}")
else:
    print("スクレイピングに失敗しました")