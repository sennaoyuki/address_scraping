#!/usr/bin/env python3
"""
リゼクリニックのリンク抽出デバッグ
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

url = "https://www.rizeclinic.com/locations/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

print("=== デバッグ: リンク検出 ===")

# パターンに一致するリンクを探す
link_pattern = r'/locations/[^/]+/?$'
found_links = []

for a in soup.find_all('a', href=True):
    href = a['href']
    if re.search(link_pattern, href):
        absolute_url = urljoin(url, href)
        text = a.get_text(strip=True)
        print(f"Found: {href}")
        print(f"  Text: {text}")
        print(f"  Absolute URL: {absolute_url}")
        print(f"  Same as base? {absolute_url.rstrip('/') == url.rstrip('/')}")
        found_links.append({
            'url': absolute_url,
            'text': text,
            'href': href
        })

print(f"\n総リンク数: {len(found_links)}")

# 最初のいくつかのリンクを表示
print("\n=== 最初の5つのリンク ===")
for i, link in enumerate(found_links[:5]):
    print(f"{i+1}. {link['href']} -> {link['text']}")