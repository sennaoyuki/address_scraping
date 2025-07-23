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
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
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
                             <div class="mb-3">
                                 <button class="btn btn-success btn-sm" id="downloadAllBtn">
                                     <i class="bi bi-download"></i> 全画像を一括ダウンロード（個別）
                                 </button>
                                 <button class="btn btn-primary btn-sm ms-2" id="downloadZipBtn">
                                     <i class="bi bi-file-earmark-zip"></i> ZIPでダウンロード
                                 </button>
                             </div>
                             <div style="max-height: 300px; overflow-y: auto;">
                                 ${data.urls.map((url, i) => 
                                    `<div class="mb-2 d-flex align-items-center">
                                        <small class="text-muted me-2">${i+1}.</small>
                                        <a href="${url}" target="_blank" class="text-break flex-grow-1">${url}</a>
                                        <button class="btn btn-outline-primary btn-sm ms-2" onclick="downloadImage('${url}', '${i+1}')">
                                            <i class="bi bi-download"></i>
                                        </button>
                                     </div>`
                                 ).join('')}
                             </div>`;
                        resultArea.style.display = 'block';
                        
                        // 一括ダウンロードボタンにイベントリスナーを追加
                        document.getElementById('downloadAllBtn').addEventListener('click', function() {
                            downloadAllImages(data.urls);
                        });
                        
                        // ZIPダウンロードボタンにイベントリスナーを追加
                        document.getElementById('downloadZipBtn').addEventListener('click', function() {
                            downloadAsZip(data.urls, url);
                        });
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

            // 個別画像ダウンロード
            window.downloadImage = async function(imageUrl, index) {
                try {
                    // サーバー経由で画像を取得
                    const response = await fetch('/api/proxy-image', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: imageUrl })
                    });
                    
                    const data = await response.json();
                    
                    if (!data.success) {
                        throw new Error(data.error);
                    }
                    
                    // Base64データをダウンロード
                    const a = document.createElement('a');
                    a.href = data.data;
                    
                    // ファイル名を生成
                    const extension = imageUrl.split('.').pop() || 'jpg';
                    a.download = `clinic_image_${index.padStart(3, '0')}.${extension}`;
                    
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                } catch (error) {
                    alert('ダウンロードに失敗しました: ' + error.message);
                }
            };

            // 全画像一括ダウンロード
            window.downloadAllImages = async function(urls) {
                if (!urls || urls.length === 0) return;
                
                const button = document.getElementById('downloadAllBtn');
                const originalText = button.innerHTML;
                button.disabled = true;
                let downloaded = 0;
                
                for (let i = 0; i < urls.length; i++) {
                    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>ダウンロード中... (${downloaded + 1}/${urls.length})`;
                    
                    try {
                        await downloadImage(urls[i], (i + 1).toString());
                        downloaded++;
                        // 1秒間隔でダウンロード
                        if (i < urls.length - 1) {
                            await new Promise(resolve => setTimeout(resolve, 1000));
                        }
                    } catch (error) {
                        console.error('ダウンロードエラー:', error);
                    }
                }
                
                button.disabled = false;
                button.innerHTML = originalText;
                alert(`${downloaded}枚の画像をダウンロードしました！`);
            };

            // ZIP形式でダウンロード
            window.downloadAsZip = async function(urls, siteUrl) {
                if (!urls || urls.length === 0) return;
                
                const button = document.getElementById('downloadZipBtn');
                const originalText = button.innerHTML;
                button.disabled = true;
                
                const zip = new JSZip();
                let downloaded = 0;
                
                for (let i = 0; i < urls.length; i++) {
                    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>ZIP作成中... (${downloaded + 1}/${urls.length})`;
                    
                    try {
                        // サーバー経由で画像を取得
                        const response = await fetch('/api/proxy-image', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ url: urls[i] })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            // Base64データから画像データを抽出
                            const base64Data = data.data.split(',')[1];
                            const extension = urls[i].split('.').pop() || 'jpg';
                            const filename = `clinic_image_${(i + 1).toString().padStart(3, '0')}.${extension}`;
                            
                            // ZIPに追加
                            zip.file(filename, base64Data, {base64: true});
                            downloaded++;
                        }
                    } catch (error) {
                        console.error('画像取得エラー:', error);
                    }
                }
                
                // ZIPファイルを生成
                button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>ZIPファイル生成中...`;
                
                try {
                    const content = await zip.generateAsync({type: 'blob'});
                    
                    // ダウンロード
                    const a = document.createElement('a');
                    const url = window.URL.createObjectURL(content);
                    a.href = url;
                    
                    // ファイル名を生成（ドメイン名を使用）
                    const domain = new URL(siteUrl).hostname.replace('www.', '');
                    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
                    a.download = `${domain}_images_${timestamp}.zip`;
                    
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    alert(`${downloaded}枚の画像をZIPファイルとしてダウンロードしました！`);
                } catch (error) {
                    alert('ZIPファイルの生成に失敗しました: ' + error.message);
                }
                
                button.disabled = false;
                button.innerHTML = originalText;
            };
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
        
        # リゼクリニック専用パターン
        if 'rizeclinic' in domain:
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if '/assets/img/locations/' in src and 'img_gallery01.jpg' in src:
                    absolute_url = urljoin(url, src)
                    image_urls.append(absolute_url)
            
            # 追加パターン: 店舗画像
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if '/assets/img/locations/' in src and any(x in src for x in ['gallery', 'clinic', 'store']):
                    absolute_url = urljoin(url, src)
                    image_urls.append(absolute_url)
        
        # DR.スキンクリニック専用パターン
        elif 'drskinclinic' in domain:
            for img in soup.select('img[alt$="院"]'):
                if img.get('src'):
                    absolute_url = urljoin(url, img['src'])
                    image_urls.append(absolute_url)
        
        # フレイアクリニック専用パターン
        elif 'frey-a' in domain:
            for img in soup.find_all('img'):
                alt_text = img.get('alt', '')
                if 'フレイアクリニック' in alt_text and '院の院内風景' in alt_text:
                    if img.get('src'):
                        absolute_url = urljoin(url, img['src'])
                        image_urls.append(absolute_url)
            
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if '400x265' in src and 'media.frey-a.jp' in src:
                    absolute_url = urljoin(url, src)
                    image_urls.append(absolute_url)
        
        # リエートクリニック専用パターン
        elif 'lietoclinic' in domain:
            for i in range(1, 10):  # より多くのスライダーをチェック
                main_slider = soup.find(class_=f'js-clinic-mainslick_0{i}')
                if main_slider:
                    first_img = main_slider.find('img')
                    if first_img and first_img.get('src'):
                        absolute_url = urljoin(url, first_img['src'])
                        image_urls.append(absolute_url)
        
        # ビューティースキンクリニック専用パターン
        elif 'beautyskinclinic' in domain:
            for img in soup.find_all('img'):
                alt_text = img.get('alt', '')
                src = img.get('src', '')
                if 'ビューティースキンクリニック' in alt_text and '院' in alt_text and src.endswith('.webp'):
                    absolute_url = urljoin(url, src)
                    image_urls.append(absolute_url)
        
        # DIOクリニックパターン
        elif 'dioclinic' in domain:
            clinic_divs = soup.find_all('div', class_='p-clinic__item--img')
            for div in clinic_divs:
                img = div.find('img')
                if img and img.get('src'):
                    absolute_url = urljoin(url, img['src'])
                    if '/wp-content/uploads/' in absolute_url:
                        image_urls.append(absolute_url)
        
        # エミナルクリニックパターン
        elif 'eminal-clinic' in domain:
            clinic_imgs = soup.find_all('img', class_='p-clinic__clinic-card-img')
            for img in clinic_imgs:
                if img.get('src'):
                    absolute_url = urljoin(url, img['src'])
                    image_urls.append(absolute_url)
        
        # 一般的なパターン（上記に該当しない場合）
        else:
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

@app.route('/api/proxy-image', methods=['POST'])
def proxy_image():
    """画像をプロキシしてダウンロード"""
    try:
        data = request.json
        image_url = data.get('url')
        
        if not image_url:
            return jsonify({'success': False, 'error': 'URLが指定されていません'}), 400
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 画像を取得
        response = requests.get(image_url, headers=headers, timeout=8)
        response.raise_for_status()
        
        # Base64エンコード
        import base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        
        # Content-Typeを判定
        content_type = response.headers.get('Content-Type', 'image/jpeg')
        
        return jsonify({
            'success': True,
            'data': f'data:{content_type};base64,{image_base64}',
            'filename': image_url.split('/')[-1]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

app = app