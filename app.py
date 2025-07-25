#!/usr/bin/env python3
"""
クリニック店舗情報スクレイパー ウェブアプリケーション
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import threading
from clinic_info_scraper import ClinicInfoScraper
import time

app = Flask(__name__)
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
    scraper = ClinicInfoScraper()
    scrapers[session_id] = scraper
    
    # バックグラウンドでスクレイピングを実行
    def run_scrape():
        success = scraper.scrape_clinics(url)
        if success:
            # CSVファイルを保存
            csv_filename = scraper.save_to_csv()
            # セッション情報にダウンロード情報を追加
            scrapers[session_id] = {
                'scraper': scraper,
                'result': {
                    'success': True,
                    'filename': os.path.basename(csv_filename),
                    'download_url': f'/download/{os.path.basename(csv_filename)}',
                    'clinic_count': len(scraper.clinic_data)
                }
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
    file_path = os.path.join('downloads', filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'ファイルが見つかりません'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """古いダウンロードファイルを削除"""
    downloads_dir = 'downloads'
    if os.path.exists(downloads_dir):
        # 1時間以上古いファイルを削除
        current_time = time.time()
        for filename in os.listdir(downloads_dir):
            file_path = os.path.join(downloads_dir, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 3600:  # 1時間
                    os.remove(file_path)
    
    return jsonify({'success': True})

if __name__ == '__main__':
    # ダウンロードディレクトリを作成
    os.makedirs('downloads', exist_ok=True)
    
    # テンプレートディレクトリを作成
    os.makedirs('templates', exist_ok=True)
    
    # アプリケーションを起動
    app.run(debug=True, port=5001, host='127.0.0.1')