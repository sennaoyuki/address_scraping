#!/usr/bin/env python3
"""
聖心美容クリニックのスクレイピングデバッグ
"""

from clinic_info_scraper import ClinicInfoScraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def debug_seishin_clinic():
    print("=== 聖心美容クリニックのデバッグ ===")
    
    url = "https://www.seishin-biyou.jp/clinic/"
    scraper = ClinicInfoScraper()
    
    print(f"URL: {url}")
    
    # ページを取得
    try:
        response = requests.get(url, headers=scraper.headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("✅ ページ取得成功")
        
        # 現在のページから情報を抽出
        current_page_info = scraper.extract_clinic_info(soup, url)
        print(f"\n=== 現在のページ情報 ===")
        print(f"名前: '{current_page_info['name']}'")
        print(f"住所: '{current_page_info['address']}'")
        print(f"アクセス: '{current_page_info['access']}'")
        
        # リンクを検出
        clinic_links = scraper.find_clinic_links(soup, url)
        print(f"\n=== リンク検出結果 ===")
        print(f"検出されたリンク数: {len(clinic_links)}")
        
        if clinic_links:
            print("最初の5つのリンク:")
            for i, link in enumerate(clinic_links[:5]):
                print(f"  {i+1}. {link['name']} -> {link['url']}")
        
        # 手動でリンクパターンをテスト
        print(f"\n=== 手動リンク検証 ===")
        
        # 既存のパターン
        existing_patterns = [
            r'/clinic/[^/]+/?$',
            r'/store/[^/]+/?$',
            r'/shop/[^/]+/?$',
            r'/access/[^/]+/?$',
            r'/locations/[^/]+/?$',
        ]
        
        # 新しいパターン候補
        new_patterns = [
            r'/clinic/[^/]+/?$',  # 実際に必要なパターン
        ]
        
        all_links = soup.find_all('a', href=True)
        print(f"全リンク数: {len(all_links)}")
        
        seishin_links = []
        for a in all_links:
            href = a['href']
            if '/clinic/' in href and href != '/clinic/':
                absolute_url = urljoin(url, href)
                seishin_links.append({
                    'href': href,
                    'absolute_url': absolute_url,
                    'text': a.get_text(strip=True)
                })
        
        print(f"聖心クリニック関連リンク数: {len(seishin_links)}")
        for link in seishin_links[:10]:  # 最初の10個
            print(f"  {link['href']} -> {link['text']}")
        
        # 実際にスクレイピングを実行
        print(f"\n=== 実際のスクレイピング実行 ===")
        success = scraper.scrape_clinics(url)
        print(f"成功: {success}")
        print(f"取得した店舗数: {len(scraper.clinic_data)}")
        
        if scraper.clinic_data:
            print("取得した店舗:")
            for clinic in scraper.clinic_data:
                print(f"  - {clinic['name']}")
                print(f"    住所: {clinic['address']}")
                print(f"    アクセス: {clinic['access']}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_seishin_clinic()