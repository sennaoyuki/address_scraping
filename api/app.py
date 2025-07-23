from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import time
import json

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper_module import ClinicImageScraper

app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static'
)
CORS(app)

# メモリ内でセッション管理（Vercel用）
sessions = {}

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    """スクレイピングを開始（簡易版）"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'URLが指定されていません'}), 400
    
    # Vercelの制限のため、簡易的な応答を返す
    return jsonify({
        'success': True,
        'message': 'Vercel環境では完全な機能は利用できません。ローカル環境での実行を推奨します。',
        'demo': True
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({'status': 'ok', 'timestamp': time.time()})

# Vercel用のハンドラー
def handler(request, context):
    """Vercel serverless function handler"""
    return app(request, context)