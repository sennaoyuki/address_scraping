#!/usr/bin/env python3
"""
SBC湘南美容クリニックの簡単パターンテスト
"""

import re
from urllib.parse import urlparse

def test_sbc_patterns():
    print("=== SBC湘南美容クリニック パターンテスト ===")
    
    # テスト用のサンプルHTML（想定される構造）
    sample_html = """
    <html>
    <head><title>湘南美容クリニック 渋谷院</title></head>
    <body>
        <h1>湘南美容クリニック 渋谷院</h1>
        <div>
            住所：〒150-0041 東京都渋谷区神南1-22-8 渋谷東日本ビル8F
            JR渋谷駅ハチ公口から徒歩3分
        </div>
    </body>
    </html>
    """
    
    # ドメインテスト
    test_url = "https://www.s-b-c.net/clinic/branch/shibuya/"
    domain = urlparse(test_url).netloc
    print(f"URL: {test_url}")
    print(f"Domain: {domain}")
    print(f"SBCドメイン判定: {'s-b-c.net' in domain}")
    
    # パターンテスト
    text_content = sample_html
    
    # 住所パターン
    print("\n=== 住所パターンテスト ===")
    address_patterns = [
        r'〒\d{3}-\d{4}\s*[^\n]*?(?:市|区|町|村)[^\n]*?(?:丁目|番地|[0-9]+F?)',
        r'〒\d{3}-\d{4}[^\n]*',
        r'(?:東京都|大阪府|京都府|北海道|.*?県)[^\n]*?(?:市|区|町|村)[^\n]*?[0-9]',
    ]
    
    for i, pattern in enumerate(address_patterns):
        match = re.search(pattern, text_content)
        if match:
            address = match.group(0).strip()
            address = re.sub(r'\s+', ' ', address)
            print(f"パターン{i+1}: {address}")
        else:
            print(f"パターン{i+1}: 見つからず")
    
    # アクセスパターン
    print("\n=== アクセスパターンテスト ===")
    access_patterns = [
        r'([^\s]+駅)[^\n]*?(?:から|より)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
        r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
        r'アクセス[^\n]*?([^\s]+駅)[^\n]*?(\d+)分',
    ]
    
    found_station = None
    min_minutes = 999
    
    for i, pattern in enumerate(access_patterns):
        matches = re.findall(pattern, text_content)
        print(f"パターン{i+1}: {matches}")
        for match in matches:
            if len(match) == 2:
                station = match[0]
                try:
                    minutes = int(match[1])
                    if minutes < min_minutes:
                        min_minutes = minutes
                        found_station = f"{station}から徒歩約{minutes}分"
                except ValueError:
                    continue
    
    if found_station:
        print(f"最終結果: {found_station}")
    else:
        print("アクセス情報が見つかりませんでした")
    
    # リンクパターンテスト
    print("\n=== リンクパターンテスト ===")
    link_patterns = [
        r'/clinic/branch/[^/]+/?$',
        r'/hifuka/[^/]+/?$',
    ]
    
    test_links = [
        "/clinic/branch/shibuya/",
        "/clinic/branch/shinjuku/",
        "/hifuka/tokyo/",
        "/clinic/shibuya/",  # 通常のパターン
    ]
    
    for link in test_links:
        matched = False
        for pattern in link_patterns:
            if re.search(pattern, link):
                print(f"✅ {link} -> {pattern}")
                matched = True
                break
        if not matched:
            print(f"❌ {link} -> マッチしません")

if __name__ == "__main__":
    test_sbc_patterns()