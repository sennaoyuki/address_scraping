#!/usr/bin/env python3
"""
フレイアクリニックのデバッグスクリプト
"""

from clinic_info_scraper import ClinicInfoScraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def debug_freya_clinic():
    print("=== フレイアクリニックのデバッグ ===")
    
    url = "https://frey-a.jp/clinic/"
    scraper = ClinicInfoScraper()
    
    print(f"URL: {url}")
    
    try:
        # ページを取得
        response = requests.get(url, headers=scraper.headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("✅ ページ取得成功")
        print(f"ステータスコード: {response.status_code}")
        
        # タイトルを確認
        title = soup.find('title')
        if title:
            print(f"ページタイトル: {title.get_text(strip=True)}")
        
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
            print("\n検出されたリンク:")
            for i, link in enumerate(clinic_links[:10]):
                print(f"  {i+1}. {link['name']} -> {link['url']}")
        
        # 手動でリンクパターンを分析
        print(f"\n=== 手動リンク分析 ===")
        all_links = soup.find_all('a', href=True)
        print(f"全リンク数: {len(all_links)}")
        
        # フレイアクリニック特有のパターンを探す
        freya_links = []
        for a in all_links:
            href = a['href']
            text = a.get_text(strip=True)
            
            # 店舗っぽいリンクを探す
            if ('clinic' in href or '院' in text or 'クリニック' in text) and href != '#' and href != '/clinic/':
                absolute_url = urljoin(url, href)
                if absolute_url not in [link['absolute_url'] for link in freya_links]:
                    freya_links.append({
                        'href': href,
                        'absolute_url': absolute_url,
                        'text': text
                    })
        
        print(f"\nフレイア関連リンク数: {len(freya_links)}")
        for i, link in enumerate(freya_links[:20]):
            print(f"  {i+1}. {link['href']} -> {link['text']}")
        
        # HTML構造を確認
        print(f"\n=== HTML構造分析 ===")
        
        # 店舗リストがあるか確認
        store_containers = soup.find_all(['div', 'ul', 'section'], class_=re.compile(r'(store|clinic|shop|branch)', re.I))
        print(f"店舗コンテナ候補: {len(store_containers)}")
        
        # 実際にスクレイピングを実行
        print(f"\n=== 実際のスクレイピング実行 ===")
        scraper.clinic_data = []  # リセット
        success = scraper.scrape_clinics(url)
        print(f"成功: {success}")
        print(f"取得した店舗数: {len(scraper.clinic_data)}")
        print(f"ステータス: {scraper.status}")
        print(f"現在のアクション: {scraper.current_action}")
        
        if scraper.clinic_data:
            print("\n取得した店舗（最初の5件）:")
            for i, clinic in enumerate(scraper.clinic_data[:5]):
                print(f"\n{i+1}. {clinic['name']}")
                print(f"   住所: {clinic['address']}")
                print(f"   アクセス: {clinic['access']}")
                print(f"   URL: {clinic['url']}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_freya_clinic()