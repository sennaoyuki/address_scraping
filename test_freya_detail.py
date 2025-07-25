#!/usr/bin/env python3
"""
フレイアクリニック個別ページの詳細分析
"""

import requests
from bs4 import BeautifulSoup
import re

def analyze_freya_page():
    # 札幌院のページを分析
    url = "https://frey-a.jp/clinic/sapporo/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"=== フレイアクリニック札幌院の分析 ===")
    print(f"URL: {url}")
    print(f"ステータス: {response.status_code}")
    
    # タイトル
    title = soup.find('title')
    print(f"\nタイトル: {title.get_text(strip=True) if title else 'なし'}")
    
    # h1タグ
    h1 = soup.find('h1')
    print(f"H1: {h1.get_text(strip=True) if h1 else 'なし'}")
    
    # テーブル構造を探す
    print("\n=== テーブル構造の分析 ===")
    tables = soup.find_all('table')
    print(f"テーブル数: {len(tables)}")
    
    for i, table in enumerate(tables[:3]):
        print(f"\nテーブル {i+1}:")
        # 各行を表示
        for tr in table.find_all('tr')[:5]:
            th = tr.find('th')
            td = tr.find('td')
            if th and td:
                print(f"  {th.get_text(strip=True)}: {td.get_text(strip=True)[:50]}...")
    
    # dl/dt/dd構造を探す
    print("\n=== 定義リスト構造の分析 ===")
    dls = soup.find_all('dl')
    print(f"定義リスト数: {len(dls)}")
    
    for i, dl in enumerate(dls[:3]):
        print(f"\n定義リスト {i+1}:")
        dts = dl.find_all('dt')
        dds = dl.find_all('dd')
        for dt, dd in zip(dts[:5], dds[:5]):
            print(f"  {dt.get_text(strip=True)}: {dd.get_text(strip=True)[:50]}...")
    
    # 住所っぽいテキストを探す
    print("\n=== 住所パターンの検索 ===")
    text_content = soup.get_text()
    
    # 郵便番号パターン
    postal_patterns = [
        r'〒\d{3}-\d{4}[^\n]*',
        r'〒\s*\d{3}-\d{4}[^\n]*',
    ]
    
    for pattern in postal_patterns:
        matches = re.findall(pattern, text_content)
        if matches:
            print(f"郵便番号パターン: {matches[:3]}")
            break
    
    # 住所パターン
    address_pattern = r'(北海道|.*?県|東京都|大阪府|京都府)[^\n]*?(市|区)[^\n]*?[0-9０-９]'
    address_matches = re.findall(address_pattern, text_content)
    if address_matches:
        print(f"住所パターン: {address_matches[:3]}")
    
    # アクセス情報を探す
    print("\n=== アクセス情報の検索 ===")
    access_patterns = [
        r'([^\s]+駅)[^\n]*?徒歩[^\n]*?(\d+)分',
        r'([^\s]+駅)[^\n]*?より[^\n]*?徒歩[^\n]*?(\d+)分',
        r'「([^\s]+駅)」[^\n]*?徒歩[^\n]*?(\d+)分',
    ]
    
    for pattern in access_patterns:
        matches = re.findall(pattern, text_content)
        if matches:
            print(f"アクセスパターン: {matches[:3]}")
    
    # 特定のクラスやIDを持つ要素を探す
    print("\n=== 特定要素の検索 ===")
    
    # addressクラスを持つ要素
    address_elems = soup.find_all(class_=re.compile(r'address', re.I))
    print(f"addressクラス要素: {len(address_elems)}")
    for elem in address_elems[:3]:
        print(f"  {elem.name}: {elem.get_text(strip=True)[:50]}...")
    
    # accessクラスを持つ要素
    access_elems = soup.find_all(class_=re.compile(r'access', re.I))
    print(f"accessクラス要素: {len(access_elems)}")
    for elem in access_elems[:3]:
        print(f"  {elem.name}: {elem.get_text(strip=True)[:50]}...")
    
    # infoクラスを持つ要素
    info_elems = soup.find_all(class_=re.compile(r'info', re.I))
    print(f"infoクラス要素: {len(info_elems)}")
    for elem in info_elems[:3]:
        print(f"  {elem.name}: {elem.get_text(strip=True)[:100]}...")

if __name__ == "__main__":
    analyze_freya_page()