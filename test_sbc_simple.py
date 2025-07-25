#!/usr/bin/env python3
"""
SBC湘南美容クリニックの簡単デバッグ
"""

from clinic_info_scraper import ClinicInfoScraper

def simple_sbc_test():
    print("=== SBC湘南美容クリニック 簡単テスト ===")
    
    url = "https://www.s-b-c.net/clinic/"
    scraper = ClinicInfoScraper()
    
    print(f"URL: {url}")
    print("スクレイピング実行中...")
    
    try:
        success = scraper.scrape_clinics(url)
        print(f"成功: {success}")
        print(f"取得した店舗数: {len(scraper.clinic_data)}")
        print(f"ステータス: {scraper.status}")
        print(f"現在のアクション: {scraper.current_action}")
        
        if scraper.clinic_data:
            print(f"\n最初の3店舗:")
            for i, clinic in enumerate(scraper.clinic_data[:3]):
                print(f"  {i+1}. {clinic['name']}")
                print(f"     住所: {clinic['address']}")
                print(f"     アクセス: {clinic['access']}")
        else:
            print("店舗データが取得できませんでした")
            
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    simple_sbc_test()