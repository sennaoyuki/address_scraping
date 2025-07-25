#!/usr/bin/env python3
"""
SBC湘南美容クリニックのスクレイピングデバッグ
"""

from clinic_info_scraper import ClinicInfoScraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def debug_sbc_clinic():
    print("=== SBC湘南美容クリニックのデバッグ ===")
    
    url = "https://www.s-b-c.net/clinic/"
    scraper = ClinicInfoScraper()
    
    print(f"URL: {url}")
    
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
            print("最初の10つのリンク:")
            for i, link in enumerate(clinic_links[:10]):
                print(f"  {i+1}. {link['name']} -> {link['url']}")
        
        # 手動でSBC特有のリンクパターンを探す
        print(f"\n=== 手動リンク分析 ===")
        
        all_links = soup.find_all('a', href=True)
        print(f"全リンク数: {len(all_links)}")
        
        # SBC特有のパターンを探す
        sbc_patterns = [
            r'/clinic/branch/[^/]+/?',
            r'/hifuka/[^/]+/?',
            r'/clinic/[^/]+/?',
        ]
        
        sbc_links = []
        for a in all_links:
            href = a['href']
            for pattern in sbc_patterns:
                if re.search(pattern, href):
                    absolute_url = urljoin(url, href)
                    if absolute_url.rstrip('/') != url.rstrip('/'):
                        sbc_links.append({
                            'href': href,
                            'absolute_url': absolute_url,
                            'text': a.get_text(strip=True)
                        })
                    break
        
        print(f"SBC関連リンク数: {len(sbc_links)}")
        for i, link in enumerate(sbc_links[:15]):  # 最初の15個
            print(f"  {i+1}. {link['href']} -> {link['text']}")
        
        # 実際にスクレイピングを実行
        print(f"\n=== 実際のスクレイピング実行 ===")
        success = scraper.scrape_clinics(url)
        print(f"成功: {success}")
        print(f"取得した店舗数: {len(scraper.clinic_data)}")
        
        if scraper.clinic_data:
            print("取得した店舗:")
            for i, clinic in enumerate(scraper.clinic_data[:5]):  # 最初の5店舗
                print(f"  {i+1}. {clinic['name']}")
                print(f"    住所: {clinic['address']}")
                print(f"    アクセス: {clinic['access']}")
        
        # 特定の店舗ページを直接テスト
        print(f"\n=== 個別店舗ページテスト ===")
        test_store_url = "https://www.s-b-c.net/clinic/branch/shibuya/"
        try:
            store_response = requests.get(test_store_url, headers=scraper.headers, timeout=10)
            store_response.raise_for_status()
            store_soup = BeautifulSoup(store_response.content, 'html.parser')
            
            store_info = scraper.extract_clinic_info(store_soup, test_store_url, "渋谷院")
            print(f"渋谷院テスト:")
            print(f"  名前: '{store_info['name']}'")
            print(f"  住所: '{store_info['address']}'")
            print(f"  アクセス: '{store_info['access']}'")
            
        except Exception as e:
            print(f"❌ 個別店舗ページエラー: {e}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sbc_clinic()