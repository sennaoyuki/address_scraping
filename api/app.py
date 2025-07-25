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
        <title>クリニック店舗情報スクレイパー</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <span class="navbar-brand mb-0 h1">
                    <i class="bi bi-hospital"></i> クリニック店舗情報スクレイパー
                </span>
            </div>
        </nav>

        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card shadow">
                        <div class="card-body">
                            <h2 class="card-title text-center mb-4">
                                <i class="bi bi-building"></i> クリニック店舗情報を自動収集
                            </h2>
                            
                            <div class="alert alert-info" role="alert">
                                <h5 class="alert-heading"><i class="bi bi-info-circle"></i> 店舗情報収集ツール</h5>
                                <p class="mb-0">
                                    クリニックの店舗名、住所、アクセス情報（駅からの分数）を自動収集し、<br>
                                    CSV形式でダウンロードできます。
                                </p>
                            </div>
                            
                            <div class="alert alert-success" role="alert">
                                <h5 class="alert-heading"><i class="bi bi-check-circle"></i> 対応サイト</h5>
                                <p class="mb-0">
                                    DIOクリニック、エミナルクリニック、フレイアクリニック、リゼクリニック、<br>
                                    その他多数のクリニックサイトに対応しています。
                                </p>
                            </div>

                            <form id="scrapeForm">
                                <div class="mb-3">
                                    <label for="urlInput" class="form-label">
                                        <i class="bi bi-link-45deg"></i> クリニックページのURL
                                    </label>
                                    <input type="url" class="form-control" id="urlInput" 
                                           placeholder="https://dioclinic.jp/clinic/" required>
                                    <div class="form-text">
                                        例: https://dioclinic.jp/clinic/
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
                                <li>クリニックの一覧ページまたは店舗ページのURLを入力</li>
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
        # 店舗名
        h1_elem = soup.find('h1')
        if h1_elem:
            clinic_info['name'] = h1_elem.get_text(strip=True)
        
        # テーブルから情報抽出
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
    """店舗一覧ページから各店舗のリンクを取得"""
    clinic_links = []
    domain = urlparse(base_url).netloc
    
    # 店舗リンクのパターン
    link_patterns = [
        r'/clinic/[^/]+/?$',
        r'/store/[^/]+/?$',
        r'/shop/[^/]+/?$',
        r'/access/[^/]+/?$',
        r'/locations/[^/]+/?$',  # リゼクリニック用
        r'/clinic/branch/[^/]+/?$',  # SBC湘南美容クリニック用
        r'/hifuka/[^/]+/?$',  # SBC湘南美容クリニック用
    ]
    
    # すべてのリンクを確認
    for a in soup.find_all('a', href=True):
        href = a['href']
        absolute_url = urljoin(base_url, href)
        
        # パターンマッチング
        for pattern in link_patterns:
            if re.search(pattern, href):
                # 一覧ページ自身へのリンクは除外
                if absolute_url.rstrip('/') != base_url.rstrip('/'):
                    clinic_links.append({
                        'url': absolute_url,
                        'name': a.get_text(strip=True)
                    })
                break
    
    # 重複を除去
    seen = set()
    unique_links = []
    for link in clinic_links:
        if link['url'] not in seen:
            seen.add(link['url'])
            unique_links.append(link)
    
    return unique_links  # 全店舗を処理

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """店舗情報をスクレイピング"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URLが指定されていません'})
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # ページを取得
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        clinic_data = []
        
        # まず現在のページから情報を抽出
        current_page_info = extract_clinic_info(soup, url)
        
        # 店舗情報が取得できた場合は追加
        if current_page_info['name'] and (current_page_info['address'] or current_page_info['access']):
            clinic_data.append(current_page_info)
        
        # 店舗一覧ページかチェック（複数の店舗リンクがある場合）
        clinic_links = find_clinic_links(soup, url)
        
        if len(clinic_links) > 3:  # 3つ以上のリンクがある場合は一覧ページと判断
            # 全店舗を処理
            for link in clinic_links:
                try:
                    # 各店舗ページを取得
                    clinic_response = requests.get(link['url'], headers=headers, timeout=10)
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
        writer = csv.DictWriter(output, fieldnames=['店舗名', '住所', 'アクセス', 'URL'])
        writer.writeheader()
        
        for clinic in clinic_data:
            writer.writerow({
                '店舗名': clinic['name'],
                '住所': clinic['address'],
                'アクセス': clinic['access'],
                'URL': clinic['url']
            })
        
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
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health')
def health():
    """ヘルスチェック"""
    return jsonify({'status': 'ok'})

# Vercel用のエクスポート
app = app