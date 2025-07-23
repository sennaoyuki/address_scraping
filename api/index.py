from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import threading
import time

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper_module import ClinicImageScraper

app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static'
)
CORS(app)

# スクレイパーインスタンスを保持
scrapers = {}

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    """スクレイピングを開始"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'URLが指定されていません'}), 400
    
    # セッションID（簡易的にタイムスタンプを使用）
    session_id = str(int(time.time() * 1000))
    
    # スクレイパーインスタンスを作成
    scraper = ClinicImageScraper()
    scrapers[session_id] = scraper
    
    # バックグラウンドでスクレイピングを実行
    def run_scrape():
        result = scraper.scrape_images(url)
        if result and result['success']:
            # セッション情報にダウンロード情報を追加
            scrapers[session_id] = {
                'scraper': scraper,
                'result': result
            }
    
    thread = threading.Thread(target=run_scrape)
    thread.start()
    
    return jsonify({
        'success': True,
        'session_id': session_id
    })

@app.route('/api/progress/<session_id>')
def get_progress(session_id):
    """進捗状況を取得"""
    if session_id not in scrapers:
        return jsonify({'error': 'セッションが見つかりません'}), 404
    
    scraper_data = scrapers[session_id]
    
    # 辞書の場合は完了している
    if isinstance(scraper_data, dict):
        progress = scraper_data['scraper'].get_progress()
        progress['completed'] = True
        progress['result'] = scraper_data['result']
        return jsonify(progress)
    else:
        # スクレイパーインスタンスの場合は進行中
        progress = scraper_data.get_progress()
        progress['completed'] = False
        return jsonify(progress)

@app.route('/download/<filename>')
def download_file(filename):
    """ファイルをダウンロード"""
    # Vercelでは/tmpディレクトリを使用
    file_path = os.path.join('/tmp', filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'ファイルが見つかりません'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """古いダウンロードファイルを削除"""
    # Vercelでは/tmpディレクトリを使用
    downloads_dir = '/tmp'
    if os.path.exists(downloads_dir):
        # 1時間以上古いファイルを削除
        current_time = time.time()
        for filename in os.listdir(downloads_dir):
            if filename.endswith('.zip'):
                file_path = os.path.join(downloads_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > 3600:  # 1時間
                        os.remove(file_path)
    
    return jsonify({'success': True})