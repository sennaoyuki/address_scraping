#!/usr/bin/env python3
"""
リアルタイムウェブアプリデバッグ
実際のブラウザ操作をシミュレートして問題を特定
"""

import threading
import time
import requests
from flask import Flask
from app import app, scrapers

def debug_webapp_issue():
    print("=== 実際のウェブアプリでの0店舗問題デバッグ ===")
    
    # Flaskアプリを別スレッドで起動
    def run_flask():
        app.run(debug=True, port=5001, host='127.0.0.1', use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # アプリが起動するまで少し待機
    print("Flaskアプリの起動を待機中...")
    time.sleep(3)
    
    # 実際のHTTPリクエストでテスト
    base_url = "http://127.0.0.1:5001"
    test_url = "https://www.rizeclinic.com/locations/"
    
    try:
        # 1. スクレイピング開始リクエスト
        print("\n1. スクレイピング開始リクエスト")
        response = requests.post(f"{base_url}/api/scrape", 
                               json={"url": test_url},
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code != 200:
            print("❌ スクレイピング開始に失敗")
            return
            
        session_id = response.json().get('session_id')
        if not session_id:
            print("❌ セッションIDが取得できませんでした")
            return
            
        print(f"✅ セッション開始: {session_id}")
        
        # 2. 進捗を追跡（ブラウザの動作をシミュレート）
        print("\n2. 進捗追跡開始")
        max_checks = 60
        check_count = 0
        
        while check_count < max_checks:
            check_count += 1
            time.sleep(1)  # ブラウザと同じ1秒間隔
            
            try:
                progress_response = requests.get(f"{base_url}/api/progress/{session_id}", timeout=5)
                
                if progress_response.status_code != 200:
                    print(f"❌ 進捗取得エラー: {progress_response.status_code}")
                    continue
                    
                progress_data = progress_response.json()
                
                # 詳細なログ出力（ブラウザコンソールと同等）
                status = progress_data.get('status', 'N/A')
                progress = progress_data.get('progress', 0)
                total = progress_data.get('total', 0)
                clinic_count = progress_data.get('clinic_count', 0)
                completed = progress_data.get('completed', False)
                
                print(f"[{check_count:2d}] {status} | {progress}/{total} | clinics: {clinic_count} | done: {completed}")
                
                if completed:
                    print("\n🎯 スクレイピング完了！")
                    result = progress_data.get('result', {})
                    
                    print("=== 最終結果詳細 ===")
                    print(f"result.success: {result.get('success')}")
                    print(f"result.clinic_count: {result.get('clinic_count')} (type: {type(result.get('clinic_count'))})")
                    print(f"result.filename: {result.get('filename')}")
                    print(f"result.download_url: {result.get('download_url')}")
                    
                    print(f"progress.clinic_count: {progress_data.get('clinic_count')} (type: {type(progress_data.get('clinic_count'))})")
                    
                    # 問題の特定
                    result_count = result.get('clinic_count', 0)
                    progress_count = progress_data.get('clinic_count', 0)
                    
                    if result_count == 0:
                        print("❌ 問題発見: result.clinic_count が 0 です！")
                        print("📍 これがフロントエンドで0店舗と表示される原因です")
                    elif progress_count == 0:
                        print("❌ 問題発見: progress.clinic_count が 0 です！")
                    else:
                        print(f"✅ 両方とも正常: result={result_count}, progress={progress_count}")
                    
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ リクエストエラー: {e}")
                continue
                
        else:
            print("⏰ タイムアウト: 60秒経過しても完了しませんでした")
            
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_webapp_issue()