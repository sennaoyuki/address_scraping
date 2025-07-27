#!/usr/bin/env python3
"""
API のローカルテスト（extract_clinic_info_legacy）
"""

import sys
sys.path.append('api')
from app import extract_clinic_info_legacy
import requests
from bs4 import BeautifulSoup

# フレイアクリニック札幌院をテスト
url = "https://frey-a.jp/clinic/sapporo/"
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.content, 'html.parser')

result = extract_clinic_info_legacy(soup, url, "テスト")

print(f"URL: {url}")
print(f"名前: {result['name']}")
print(f"住所: {result['address']}")
print(f"アクセス: {result['access']}")