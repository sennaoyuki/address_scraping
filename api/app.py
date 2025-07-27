from flask import Flask, render_template_string, request, jsonify, Response
import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re
import csv
from datetime import datetime
import io
try:
    from universal_scraper import UniversalStoreScraper
    universal_scraper = UniversalStoreScraper()
except ImportError:
    print("Warning: universal_scraper not found, using legacy extraction only")
    universal_scraper = None

app = Flask(__name__)

@app.route('/')
def index():
    """メインページ"""
    return """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ユニバーサル店舗情報スクレイパー</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <span class="navbar-brand mb-0 h1">
                    <i class="bi bi-shop-window"></i> ユニバーサル店舗情報スクレイパー
                </span>
            </div>
        </nav>

        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card shadow">
                        <div class="card-body">
                            <h2 class="card-title text-center mb-4">
                                <i class="bi bi-building"></i> 店舗情報を自動収集
                            </h2>
                            
                            <div class="alert alert-info" role="alert">
                                <h5 class="alert-heading"><i class="bi bi-info-circle"></i> 店舗情報収集ツール</h5>
                                <p class="mb-0">
                                    店舗名、住所、アクセス情報（駅からの分数）、電話番号、営業時間を自動収集し、<br>
                                    CSV形式でダウンロードできます。
                                </p>
                            </div>
                            
                            <div class="alert alert-success" role="alert">
                                <h5 class="alert-heading"><i class="bi bi-check-circle"></i> ユニバーサル対応</h5>
                                <p class="mb-0">
                                    <strong>あらゆるウェブサイトに対応！</strong><br>
                                    インテリジェントなパターン認識により、クリニック、店舗、オフィスなど、<br>
                                    様々な店舗情報を自動的に抽出します。<br>
                                    <small class="text-muted">※ 従来対応サイト（DIO、エミナル、フレイア、リゼ等）も引き続き高精度で抽出</small>
                                </p>
                            </div>

                            <form id="scrapeForm">
                                <div class="mb-3">
                                    <label for="urlInput" class="form-label">
                                        <i class="bi bi-link-45deg"></i> 店舗ページのURL
                                    </label>
                                    <input type="url" class="form-control" id="urlInput" 
                                           placeholder="https://dioclinic.jp/clinic/" required>
                                    <div class="form-text">
                                        例: https://example.com/stores/ または個別店舗ページ
                                    </div>
                                </div>
                                
                                <button type="submit" class="btn btn-primary btn-lg w-100" id="submitBtn">
                                    <i class="bi bi-cloud-download"></i> スクレイピング開始
                                </button>
                            </form>

                            <!-- 進捗表示エリア -->
                            <div id="progressArea" class="mt-4" style="display: none;">
                                <h5><i class="bi bi-hourglass-split"></i> 処理状況</h5>
                                <div class="progress mb-3" style="height: 25px;">
                                    <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated" 
                                         role="progressbar" style="width: 0%">
                                        <span id="progressText">0%</span>
                                    </div>
                                </div>
                                <p id="statusText" class="text-muted">
                                    <i class="bi bi-gear-fill spinner"></i> <span id="statusMessage">準備中...</span>
                                </p>
                            </div>

                            <!-- 結果表示エリア -->
                            <div id="resultArea" class="mt-4" style="display: none;">
                                <div class="alert alert-success" role="alert">
                                    <h5 class="alert-heading"><i class="bi bi-check-circle"></i> 完了しました！</h5>
                                    <p id="resultMessage"></p>
                                    <hr>
                                    <button id="downloadBtn" class="btn btn-success">
                                        <i class="bi bi-file-earmark-csv"></i> CSVファイルをダウンロード
                                    </button>
                                </div>
                            </div>

                            <!-- エラー表示エリア -->
                            <div id="errorArea" class="mt-4" style="display: none;">
                                <div class="alert alert-danger" role="alert">
                                    <h5 class="alert-heading"><i class="bi bi-exclamation-triangle"></i> エラー</h5>
                                    <p id="errorMessage"></p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 使い方 -->
                    <div class="card mt-4">
                        <div class="card-body">
                            <h5 class="card-title"><i class="bi bi-question-circle"></i> 使い方</h5>
                            <ol>
                                <li>店舗一覧ページまたは個別店舗ページのURLを入力</li>
                                <li>「スクレイピング開始」ボタンをクリック</li>
                                <li>自動的に店舗情報（名前、住所、アクセス）を収集</li>
                                <li>完了後、CSVファイルでダウンロード</li>
                            </ol>
                            <p class="text-muted small mb-0">
                                ※ 一覧ページの場合は、自動的に各店舗の詳細ページを探索します
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let currentData = null;

            document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const url = document.getElementById('urlInput').value;
                const submitBtn = document.getElementById('submitBtn');
                
                // UIをリセット
                resetUI();
                
                // ボタンを無効化
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>処理中...';
                
                // 進捗エリアを表示
                document.getElementById('progressArea').style.display = 'block';
                
                try {
                    const response = await fetch('/api/scrape', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ url: url })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        currentData = data;
                        showResult(data);
                    } else {
                        showError(data.error || '処理を開始できませんでした。');
                    }
                } catch (error) {
                    showError('サーバーとの通信に失敗しました。');
                } finally {
                    // ボタンを有効化
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-cloud-download"></i> スクレイピング開始';
                }
            });

            function showResult(data) {
                const resultArea = document.getElementById('resultArea');
                const resultMessage = document.getElementById('resultMessage');
                
                resultMessage.textContent = `${data.clinic_count}件の店舗情報を取得しました！`;
                
                hideProgressArea();
                resultArea.style.display = 'block';
            }

            function showError(message) {
                const errorArea = document.getElementById('errorArea');
                const errorMessage = document.getElementById('errorMessage');
                
                errorMessage.textContent = message;
                
                hideProgressArea();
                errorArea.style.display = 'block';
            }

            function hideProgressArea() {
                document.getElementById('progressArea').style.display = 'none';
            }

            function resetUI() {
                document.getElementById('progressArea').style.display = 'none';
                document.getElementById('resultArea').style.display = 'none';
                document.getElementById('errorArea').style.display = 'none';
                
                // 進捗バーをリセット
                const progressBar = document.getElementById('progressBar');
                const progressText = document.getElementById('progressText');
                progressBar.style.width = '100%';
                progressText.textContent = '100%';
            }

            // CSVダウンロード
            document.getElementById('downloadBtn').addEventListener('click', () => {
                if (!currentData || !currentData.csv_data) return;
                
                // CSVデータをダウンロード
                const blob = new Blob([currentData.csv_data], { type: 'text/csv;charset=utf-8-sig' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = currentData.filename || 'clinic_info.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            });
        </script>
    </body>
    </html>
    """

def extract_clinic_info(soup, url, clinic_name=""):
    """ページから店舗情報を抽出"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    
    # デバッグログ
    print(f"[DEBUG] extract_clinic_info - URL: {url}, Domain: {domain}")
    
    # 特定のサイトの場合はレガシー抽出を使用
    legacy_domains = ['dioclinic', 'eminal-clinic', 'frey-a', 'seishin-biyou', 'rizeclinic', 's-b-c.net']
    
    for legacy_domain in legacy_domains:
        if legacy_domain in domain:
            print(f"[DEBUG] Using legacy extraction for {legacy_domain}")
            return extract_clinic_info_legacy(soup, url, clinic_name)
    
    # それ以外は汎用スクレイパーを使用（利用可能な場合）
    if universal_scraper:
        result = universal_scraper.extract_store_info(soup, url, clinic_name)
        
        # Transform to the expected format
        clinic_info = {
            'name': result.get('name', clinic_name),
            'address': result.get('address', ''),
            'access': result.get('access', ''),
            'url': url
        }
        
        # Add additional fields if available
        if 'phone' in result and result['phone']:
            clinic_info['phone'] = result['phone']
        if 'hours' in result and result['hours']:
            clinic_info['hours'] = result['hours']
        
        return clinic_info
    else:
        # 汎用スクレイパーが利用できない場合は基本的な抽出
        return extract_clinic_info_legacy(soup, url, clinic_name)

def extract_clinic_info_legacy(soup, url, clinic_name=""):
    """Legacy extraction method (kept for reference)"""
    clinic_info = {
        'name': clinic_name,
        'address': '',
        'access': '',
        'url': url
    }
    
    domain = urlparse(url).netloc
    
    # DIOクリニック
    if 'dioclinic' in domain:
        # 店舗名
        name_elem = soup.find('h2', class_='clinic-name')
        if name_elem:
            clinic_info['name'] = name_elem.get_text(strip=True)
        
        # 住所
        address_elem = soup.find('div', class_='address')
        if address_elem:
            clinic_info['address'] = address_elem.get_text(strip=True)
        
        # アクセス
        access_elem = soup.find('div', class_='access')
        if access_elem:
            clinic_info['access'] = access_elem.get_text(strip=True)
    
    # エミナルクリニック
    elif 'eminal-clinic' in domain:
        # 店舗情報テーブルから抽出
        for tr in soup.find_all('tr'):
            th = tr.find('th')
            td = tr.find('td')
            if th and td:
                header = th.get_text(strip=True)
                if '院名' in header:
                    clinic_info['name'] = td.get_text(strip=True)
                elif '住所' in header:
                    clinic_info['address'] = td.get_text(strip=True)
                elif 'アクセス' in header:
                    clinic_info['access'] = td.get_text(strip=True)
    
    # フレイアクリニック
    elif 'frey-a' in domain:
        print(f"[DEBUG] Processing Freya clinic - URL: {url}")
        
        # 店舗名 - h1タグから取得し、不要な部分を削除
        h1_elem = soup.find('h1')
        if h1_elem:
            name = h1_elem.get_text(strip=True)
            # "札幌で医療脱毛するなら" のような前置きを削除
            if '医療脱毛するなら' in name:
                name = name.split('医療脱毛するなら')[-1].strip()
            clinic_info['name'] = name
            print(f"[DEBUG] Freya name found: {clinic_info['name']}")
        
        # dl/dt/dd構造から情報抽出（フレイアクリニックの現在の構造）
        dl_elems = soup.find_all('dl')
        print(f"[DEBUG] Found {len(dl_elems)} dl elements")
        for dl in dl_elems:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            
            for dt, dd in zip(dts, dds):
                header = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                
                if 'クリニック住所' in header or '住所' in header:
                    # 住所から余分な情報を削除
                    address = value.split('当院には')[0].strip()
                    clinic_info['address'] = address
                    print(f"[DEBUG] Freya address found: {clinic_info['address']}")
                elif '最寄り駅' in header or 'アクセス' in header:
                    # アクセス情報から最も近い駅を抽出
                    access_text = value.split('出口まで')[0].strip()
                    # 複数の駅情報から最初のものを使用
                    access_lines = access_text.split('\n')
                    if access_lines:
                        clinic_info['access'] = access_lines[0].strip()
                        print(f"[DEBUG] Freya access found: {clinic_info['access']}")
        
        # もしdl構造で見つからない場合は、テーブルから情報抽出（旧構造対応）
        if not clinic_info['address']:
            for tr in soup.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    header = th.get_text(strip=True)
                    if '所在地' in header:
                        clinic_info['address'] = td.get_text(strip=True)
                    elif 'アクセス' in header:
                        clinic_info['access'] = td.get_text(strip=True)
    
    # 聖心美容クリニック
    elif 'seishin-biyou' in domain:
        # 店舗名 - h1タグまたはページタイトルから取得
        h1_elem = soup.find('h1')
        if h1_elem:
            clinic_info['name'] = h1_elem.get_text(strip=True)
        
        # 住所の抽出 - より広範囲の検索
        text_content = soup.get_text()
        
        # 住所パターンの改良
        address_patterns = [
            r'〒\d{3}-\d{4}\s*[^\n]*?(?:市|区|町|村)[^\n]*?(?:丁目|番地|[0-9]+F?)',
            r'〒\d{3}-\d{4}[^\n]*',
            r'(?:東京都|大阪府|京都府|北海道|.*?県)[^\n]*?(?:市|区|町|村)[^\n]*?[0-9]',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text_content)
            if match:
                address = match.group(0).strip()
                # 余分な改行や空白を除去
                address = re.sub(r'\s+', ' ', address)
                clinic_info['address'] = address
                break
        
        # アクセス情報の抽出 - 聖心美容クリニック専用パターン
        access_patterns = [
            r'([^\s]+駅)[^\n]*?(?:から|より)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            r'アクセス[^\n]*?([^\s]+駅)[^\n]*?(\d+)分',
        ]
        
        found_station = None
        min_minutes = 999
        
        for pattern in access_patterns:
            matches = re.findall(pattern, text_content)
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
            clinic_info['access'] = found_station
        
        # もしアクセス情報が見つからない場合、「○○駅」だけでも検索
        if not clinic_info['access']:
            simple_station_pattern = r'([^\s]+駅)'
            matches = re.findall(simple_station_pattern, text_content)
            if matches:
                # 最初に見つかった駅を使用
                clinic_info['access'] = f"{matches[0]}最寄り"
    
    # SBC湘南美容クリニック
    elif 's-b-c.net' in domain:
        # 店舗名 - h1タグから取得
        h1_elem = soup.find('h1')
        if h1_elem:
            clinic_info['name'] = h1_elem.get_text(strip=True)
        
        # タイトルからも店舗名を取得試行
        if not clinic_info['name']:
            title_elem = soup.find('title')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if '院' in title_text or 'クリニック' in title_text:
                    clinic_info['name'] = title_text
        
        # 住所の抽出
        text_content = soup.get_text()
        address_patterns = [
            r'〒\d{3}-\d{4}\s*[^\n]*?(?:市|区|町|村)[^\n]*?(?:丁目|番地|[0-9]+F?)',
            r'〒\d{3}-\d{4}[^\n]*',
            r'(?:東京都|大阪府|京都府|北海道|.*?県)[^\n]*?(?:市|区|町|村)[^\n]*?[0-9]',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text_content)
            if match:
                address = match.group(0).strip()
                address = re.sub(r'\s+', ' ', address)
                clinic_info['address'] = address
                break
        
        # アクセス情報の抽出
        access_patterns = [
            r'([^\s]+駅)[^\n]*?(?:から|より)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            r'アクセス[^\n]*?([^\s]+駅)[^\n]*?(\d+)分',
        ]
        
        found_station = None
        min_minutes = 999
        
        for pattern in access_patterns:
            matches = re.findall(pattern, text_content)
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
            clinic_info['access'] = found_station
        
        # アクセス情報が見つからない場合、駅名だけでも検索
        if not clinic_info['access']:
            simple_station_pattern = r'([^\s]+駅)'
            matches = re.findall(simple_station_pattern, text_content)
            if matches:
                clinic_info['access'] = f"{matches[0]}最寄り"
    
    # リゼクリニック
    elif 'rizeclinic' in domain:
        # 店舗名 - h1タグから取得
        h1_elem = soup.find('h1')
        if h1_elem:
            clinic_info['name'] = h1_elem.get_text(strip=True)
        
        # テーブルから住所を取得
        info_table = soup.find('table')
        if info_table:
            for tr in info_table.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    header = th.get_text(strip=True)
                    if '住所' in header:
                        clinic_info['address'] = td.get_text(strip=True)
        
        # アクセス情報は正規表現で抽出
        text_content = soup.get_text()
        # 複数の駅情報パターンを探す
        station_patterns = [
            r'「([^\s]+駅)」[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            r'「([^\s]+停留場)」[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
        ]
        
        found_station = None
        min_minutes = 999
        
        # 最も近い駅を探す
        for pattern in station_patterns:
            matches = re.findall(pattern, text_content)
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
            clinic_info['access'] = found_station
    
    # 汎用的な抽出（上記以外のサイト）
    else:
        # 店舗名の抽出（h1, h2タグ）
        if not clinic_info['name']:
            for tag in ['h1', 'h2']:
                elem = soup.find(tag)
                if elem:
                    text = elem.get_text(strip=True)
                    if '院' in text or 'クリニック' in text:
                        clinic_info['name'] = text
                        break
        
        # 住所の抽出（住所っぽいパターン）
        address_patterns = [
            r'〒\d{3}-\d{4}.*?(?:都|道|府|県).*?(?:市|区|町|村)',
            r'(?:東京都|大阪府|京都府|北海道|.*?県).*?(?:市|区|町|村).*?\d+',
        ]
        
        text_content = soup.get_text()
        for pattern in address_patterns:
            match = re.search(pattern, text_content)
            if match:
                clinic_info['address'] = match.group(0)
                break
        
        # アクセス情報の抽出（駅名と徒歩分数）
        access_patterns = [
            r'([^\s]+駅).*?(?:徒歩|歩いて).*?(\d+)分',
            r'([^\s]+停留場).*?(?:徒歩|歩いて).*?(\d+)分',
        ]
        
        found_station = None
        min_minutes = 999
        
        for pattern in access_patterns:
            matches = re.findall(pattern, text_content)
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
            clinic_info['access'] = found_station
    
    return clinic_info

def find_clinic_links(soup, base_url):
    """店舗一覧ページから各店舗のリンクを取得 - 改良版"""
    clinic_links = []
    domain = urlparse(base_url).netloc
    base_path = urlparse(base_url).path
    
    # Enhanced store link patterns
    link_patterns = [
        # Common patterns
        r'/(?:clinic|store|shop|branch|location|office|outlet)[s]?/[^/]+/?$',
        r'/(?:tenpo|mise)/[^/]+/?$',  # Japanese patterns
        r'/access/[^/]+/?$',
        r'/map/[^/]+/?$',
        
        # Specific patterns for known sites
        r'/locations/[^/]+/?$',  # リゼクリニック用
        r'/clinic/branch/[^/]+/?$',  # SBC湘南美容クリニック用
        r'/hifuka/[^/]+/?$',  # SBC湘南美容クリニック用
        
        # Generic patterns that might be store pages
        r'/[^/]+[-_](?:store|shop|clinic|branch)/?$',
        r'/(?:area|region)/[^/]+/[^/]+/?$',  # Area-based URLs
    ]
    
    # Keywords that suggest a store/branch link
    store_keywords = [
        '店', '院', 'クリニック', '支店', '営業所', '店舗',
        'store', 'shop', 'clinic', 'branch', 'location', 'office'
    ]
    
    # Collect all links
    all_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        absolute_url = urljoin(base_url, href)
        
        # Skip if it's the same page or external domain
        if absolute_url.rstrip('/') == base_url.rstrip('/'):
            continue
        if urlparse(absolute_url).netloc != domain:
            continue
        
        # Check pattern matching
        pattern_matched = False
        for pattern in link_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                pattern_matched = True
                break
        
        # Check if link text contains store keywords
        keyword_matched = any(keyword in text for keyword in store_keywords)
        
        # Calculate confidence score
        confidence = 0
        if pattern_matched:
            confidence += 50
        if keyword_matched:
            confidence += 30
        if len(text) < 50:  # Short text is more likely to be a store name
            confidence += 10
        if re.search(r'[都道府県市区町村]', text):  # Contains location kanji
            confidence += 10
        
        if confidence >= 40:  # Threshold for inclusion
            all_links.append({
                'url': absolute_url,
                'name': text,
                'confidence': confidence
            })
    
    # Sort by confidence and deduplicate
    all_links.sort(key=lambda x: x['confidence'], reverse=True)
    
    seen = set()
    unique_links = []
    for link in all_links:
        if link['url'] not in seen:
            seen.add(link['url'])
            unique_links.append({
                'url': link['url'],
                'name': link['name']
            })
    
    # Additional heuristic: if we find many links with similar patterns, they're likely store pages
    if len(unique_links) < 3:
        # Try to find links that share common patterns
        link_groups = {}
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(base_url, href)
            
            # Extract the pattern (e.g., /something/VARIABLE/)
            path_parts = urlparse(absolute_url).path.strip('/').split('/')
            if len(path_parts) >= 2:
                pattern_key = '/'.join(path_parts[:-1])
                if pattern_key not in link_groups:
                    link_groups[pattern_key] = []
                link_groups[pattern_key].append({
                    'url': absolute_url,
                    'name': a.get_text(strip=True)
                })
        
        # Find groups with multiple similar links
        for pattern, links in link_groups.items():
            if len(links) >= 3:  # Found a pattern with multiple links
                for link in links:
                    if link['url'] not in seen and link['url'].rstrip('/') != base_url.rstrip('/'):
                        seen.add(link['url'])
                        unique_links.append(link)
    
    return unique_links

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """店舗情報をスクレイピング"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URLが指定されていません'})
        
        # SBCサイトのデバッグ情報
        if 's-b-c.net' in url:
            print(f"[DEBUG] SBC site detected: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # ページを取得（SBCサイト用のタイムアウト調整）
        timeout_seconds = 5 if 's-b-c.net' in url else 10
        response = requests.get(url, headers=headers, timeout=timeout_seconds)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        clinic_data = []
        
        # 店舗一覧ページかチェック（複数の店舗リンクがある場合）
        clinic_links = find_clinic_links(soup, url)
        is_list_page = len(clinic_links) > 3
        
        # まず現在のページから情報を抽出
        current_page_info = extract_clinic_info(soup, url)
        
        # 一覧ページではない、または個別店舗ページの場合のみ追加
        # 一覧ページの判定: "一覧"、"クリニック一覧"、"店舗一覧" などのタイトル
        is_individual_store = not any(keyword in current_page_info['name'] for keyword in ['一覧', 'リスト', 'List'])
        
        # 店舗情報が取得できた場合は追加
        if current_page_info['name'] and (current_page_info['address'] or current_page_info['access']) and (not is_list_page or is_individual_store):
            clinic_data.append(current_page_info)
        
        if len(clinic_links) > 3:  # 3つ以上のリンクがある場合は一覧ページと判断
            # 全店舗を処理
            for link in clinic_links:
                try:
                    # 各店舗ページを取得（SBCサイト用のタイムアウト調整）
                    clinic_timeout = 3 if 's-b-c.net' in link['url'] else 10
                    clinic_response = requests.get(link['url'], headers=headers, timeout=clinic_timeout)
                    clinic_response.raise_for_status()
                    clinic_soup = BeautifulSoup(clinic_response.content, 'html.parser')
                    
                    # 店舗情報を抽出
                    clinic_info = extract_clinic_info(clinic_soup, link['url'], link['name'])
                    if clinic_info['name']:
                        clinic_data.append(clinic_info)
                    
                except Exception:
                    continue
        
        # CSVデータを生成
        output = io.StringIO()
        
        # Determine which fields are available
        has_phone = any('phone' in clinic and clinic['phone'] for clinic in clinic_data)
        has_hours = any('hours' in clinic and clinic['hours'] for clinic in clinic_data)
        
        # Build fieldnames dynamically
        fieldnames = ['店舗名', '住所', 'アクセス']
        if has_phone:
            fieldnames.append('電話番号')
        if has_hours:
            fieldnames.append('営業時間')
        fieldnames.append('URL')
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for clinic in clinic_data:
            row = {
                '店舗名': clinic['name'],
                '住所': clinic['address'],
                'アクセス': clinic['access'],
                'URL': clinic['url']
            }
            if has_phone:
                row['電話番号'] = clinic.get('phone', '')
            if has_hours:
                row['営業時間'] = clinic.get('hours', '')
            
            writer.writerow(row)
        
        csv_data = output.getvalue()
        
        # ファイル名を生成
        domain = urlparse(url).netloc
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{domain}_clinics_{timestamp}.csv"
        
        return jsonify({
            'success': True,
            'clinic_count': len(clinic_data),
            'csv_data': csv_data,
            'filename': filename
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False, 
            'error': 'アクセスタイムアウト: このサイトは現在アクセスできない可能性があります（アクセス制限またはサーバー負荷）'
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False, 
            'error': f'ネットワークエラー: {str(e)}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health')
def health():
    """ヘルスチェック"""
    return jsonify({'status': 'ok'})

# Vercel用のエクスポート
app = app