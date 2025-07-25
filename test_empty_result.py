#!/usr/bin/env python3
"""
空の結果になる場合のテスト
"""

from clinic_info_scraper import ClinicInfoScraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# ブラウザと完全に同じURLを使用
test_url = "https://www.rizeclinic.com/locations/"

scraper = ClinicInfoScraper()
headers = scraper.headers

# ページ取得
response = requests.get(test_url, headers=headers, timeout=10)
soup = BeautifulSoup(response.content, 'html.parser')

# 現在のページから情報を抽出
current_page_info = scraper.extract_clinic_info(soup, test_url)
print("=== 現在のページ情報 ===")
print(f"名前: '{current_page_info['name']}'")
print(f"住所: '{current_page_info['address']}'")
print(f"アクセス: '{current_page_info['access']}'")
print(f"条件チェック: name={bool(current_page_info['name'])}, address or access={bool(current_page_info['address'] or current_page_info['access'])}")

# 条件を満たすか確認
if current_page_info['name'] and (current_page_info['address'] or current_page_info['access']):
    print("→ 現在のページ情報がリストに追加されます")
else:
    print("→ 現在のページ情報はリストに追加されません")

# リンクを検出
clinic_links = scraper.find_clinic_links(soup, test_url)
print(f"\n=== リンク検出 ===")
print(f"検出されたリンク数: {len(clinic_links)}")
print(f"3つ以上?: {len(clinic_links) > 3}")

if len(clinic_links) > 3:
    print("→ 一覧ページとして処理されます")
else:
    print("→ 一覧ページとして処理されません")

# 最終的な結果
if not current_page_info['name'] and len(clinic_links) <= 3:
    print("\n*** 0件になる条件が成立しています ***")