from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import base64
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
        <title>クリニック画像スクレイパー</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-body">
                            <h1 class="card-title text-center">🏥 クリニック画像スクレイパー</h1>
                            
                            <div class="alert alert-success mt-4">
                                <h6><i class="bi bi-check-circle"></i> Vercel対応版</h6>
                                <p class="mb-0">画像URLのリストを取得できます（実行時間制限: 10秒）</p>
                            </div>

                            <form id="scrapeForm">
                                <div class="mb-3">
                                    <label for="urlInput" class="form-label">
                                        <i class="bi bi-link-45deg"></i> クリニックページのURL
                                    </label>
                                    <input type="url" class="form-control" id="urlInput" 
                                           placeholder="https://dioclinic.jp/clinic/" required>
                                </div>
                                
                                <button type="submit" class="btn btn-primary w-100" id="submitBtn">
                                    <i class="bi bi-search"></i> 画像URLを検索
                                </button>
                            </form>

                            <div id="resultArea" class="mt-4" style="display: none;">
                                <div class="alert alert-success">
                                    <h5><i class="bi bi-check-circle"></i> 検索完了</h5>
                                    <div id="resultContent"></div>
                                </div>
                            </div>

                            <div id="errorArea" class="mt-4" style="display: none;">
                                <div class="alert alert-danger">
                                    <h5><i class="bi bi-exclamation-triangle"></i> エラー</h5>
                                    <div id="errorContent"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const url = document.getElementById('urlInput').value;
                const submitBtn = document.getElementById('submitBtn');
                const resultArea = document.getElementById('resultArea');
                const errorArea = document.getElementById('errorArea');
                
                // UIリセット
                resultArea.style.display = 'none';
                errorArea.style.display = 'none';
                
                // ボタン無効化
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>検索中...';
                
                try {
                    const response = await fetch('/api/scrape', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        document.getElementById('resultContent').innerHTML = 
                            `<p><strong>${data.count}枚</strong>の画像URLを発見しました：</p>
                             <div style="max-height: 300px; overflow-y: auto;">
                                 ${data.urls.map((url, i) => 
                                    `<div class="mb-2">
                                        <small class="text-muted">${i+1}.</small>
                                        <a href="${url}" target="_blank" class="text-break">${url}</a>
                                     </div>`
                                 ).join('')}
                             </div>`;
                        resultArea.style.display = 'block';
                    } else {
                        document.getElementById('errorContent').textContent = data.error;
                        errorArea.style.display = 'block';
                    }
                } catch (error) {
                    document.getElementById('errorContent').textContent = 'サーバーとの通信に失敗しました。';
                    errorArea.style.display = 'block';
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-search"></i> 画像URLを検索';
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """画像URLを検索"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URLが指定されていません'})
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # ページを取得
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 画像URLを検出
        image_urls = []
        domain = urlparse(url).netloc
        
        # DIOクリニックパターン
        clinic_divs = soup.find_all('div', class_='p-clinic__item--img')
        for div in clinic_divs:
            img = div.find('img')
            if img and img.get('src'):
                absolute_url = urljoin(url, img['src'])
                if '/wp-content/uploads/' in absolute_url:
                    image_urls.append(absolute_url)
        
        # エミナルクリニックパターン
        clinic_imgs = soup.find_all('img', class_='p-clinic__clinic-card-img')
        for img in clinic_imgs:
            if img.get('src'):
                absolute_url = urljoin(url, img['src'])
                image_urls.append(absolute_url)
        
        # 一般的なパターン
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if any(keyword in src.lower() for keyword in ['clinic', 'store', 'shop', 'facility']):
                absolute_url = urljoin(url, src)
                if not any(exclude in absolute_url for exclude in ['logo', 'icon', 'banner']):
                    image_urls.append(absolute_url)
        
        # 重複削除
        image_urls = list(set(image_urls))
        
        # 画像形式のみフィルタ
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        filtered_urls = [url for url in image_urls if any(url.lower().endswith(ext) for ext in valid_extensions)]
        
        return jsonify({
            'success': True,
            'count': len(filtered_urls),
            'urls': filtered_urls[:20]  # 最大20個まで表示
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health')
def health():
    """ヘルスチェック"""
    return jsonify({'status': 'ok'})

app = app