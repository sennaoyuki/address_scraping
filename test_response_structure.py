#!/usr/bin/env python3
"""
実際のレスポンス構造を確認
"""

import json
from app import app, scrapers
from clinic_info_scraper import ClinicInfoScraper

# Flaskアプリのテストクライアント
app.config['TESTING'] = True
client = app.test_client()

print("=== レスポンス構造の確認 ===")

# スクレイピング開始
response = client.post('/api/scrape', 
                     json={'url': 'https://www.rizeclinic.com/locations/'},
                     content_type='application/json')

print(f"Start Response: {response.get_json()}")

if response.status_code == 200:
    session_id = response.get_json()['session_id']
    
    # スクレイピングが完了するまで待機
    import time
    max_wait = 40
    wait_count = 0
    
    while wait_count < max_wait:
        time.sleep(1)
        wait_count += 1
        
        progress_response = client.get(f'/api/progress/{session_id}')
        progress_data = progress_response.get_json()
        
        if progress_data.get('completed'):
            print(f"\n=== 完了時のレスポンス構造 ===")
            print(f"Full Response: {json.dumps(progress_data, indent=2, ensure_ascii=False)}")
            
            # 重要なフィールドを個別確認
            result = progress_data.get('result', {})
            print(f"\n=== result 部分 ===")
            print(f"result.success: {result.get('success')}")
            print(f"result.clinic_count: {result.get('clinic_count')}")
            print(f"result.filename: {result.get('filename')}")
            print(f"result.download_url: {result.get('download_url')}")
            
            # progress部分も確認
            print(f"\n=== progress 部分 ===")
            print(f"progress.clinic_count: {progress_data.get('clinic_count')}")
            print(f"progress.progress: {progress_data.get('progress')}")
            print(f"progress.total: {progress_data.get('total')}")
            
            break
        elif wait_count % 5 == 0:
            print(f"待機中... ({wait_count}/{max_wait}) - Clinic count: {progress_data.get('clinic_count', 'N/A')}")
    
    else:
        print("タイムアウト: 完了を確認できませんでした")