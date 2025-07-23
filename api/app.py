from flask import Flask, render_template, jsonify
import os

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
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-body text-center">
                            <h1 class="card-title">🏥 クリニック画像スクレイパー</h1>
                            <div class="alert alert-info mt-4">
                                <h5>Vercel環境での制限</h5>
                                <p>完全な機能を利用するには、ローカル環境で実行してください：</p>
                                <code>git clone https://github.com/sennaoyuki/ClinicStore_Scraping.git</code><br>
                                <code>cd ClinicStore_Scraping</code><br>
                                <code>pip install -r requirements.txt</code><br>
                                <code>python app.py</code>
                            </div>
                            <div class="alert alert-success">
                                <h6>対応サイト</h6>
                                <p class="mb-0">DIOクリニック、エミナルクリニック、DR.スキンクリニック、フレイアクリニック、リエートクリニック、リゼクリニック、ビューティースキンクリニック、メンズライフクリニックなど</p>
                            </div>
                            <a href="https://github.com/sennaoyuki/ClinicStore_Scraping" class="btn btn-primary">
                                GitHubで詳細を見る
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/health')
def health():
    """ヘルスチェック"""
    return jsonify({'status': 'ok'})

# Vercel用のハンドラー
app = app