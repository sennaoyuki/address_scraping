#!/usr/bin/env python3
"""
APIを直接テストして問題を特定
"""

import requests
import time
import json

base_url = "http://127.0.0.1:5001"
test_url = "https://www.rizeclinic.com/locations/"

print("=== APIテスト開始 ===")

# 1. スクレイピング開始
print("\n1. スクレイピング開始リクエスト...")
response = requests.post(f"{base_url}/api/scrape", 
                        json={"url": test_url},
                        headers={"Content-Type": "application/json"})

print(f"Response status: {response.status_code}")
print(f"Response data: {response.json()}")

if response.status_code == 200:
    data = response.json()
    if data.get("success") and data.get("session_id"):
        session_id = data["session_id"]
        print(f"Session ID: {session_id}")
        
        # 2. 進捗を追跡
        print("\n2. 進捗追跡開始...")
        completed = False
        check_count = 0
        
        while not completed and check_count < 60:  # 最大60秒待つ
            time.sleep(1)
            check_count += 1
            
            progress_response = requests.get(f"{base_url}/api/progress/{session_id}")
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                
                print(f"\n[Check {check_count}] Progress data:")
                print(f"  - Status: {progress_data.get('status')}")
                print(f"  - Progress: {progress_data.get('progress')}/{progress_data.get('total')}")
                print(f"  - Percentage: {progress_data.get('percentage')}%")
                print(f"  - Clinic count: {progress_data.get('clinic_count')}")
                print(f"  - Completed: {progress_data.get('completed')}")
                
                if progress_data.get('completed'):
                    completed = True
                    print("\n=== 完了 ===")
                    if progress_data.get('result'):
                        result = progress_data['result']
                        print(f"Result:")
                        print(f"  - Success: {result.get('success')}")
                        print(f"  - Clinic count: {result.get('clinic_count')}")
                        print(f"  - Download URL: {result.get('download_url')}")
                        print(f"  - Error: {result.get('error')}")
                    break
            else:
                print(f"Progress check failed: {progress_response.status_code}")
                break
        
        if not completed:
            print("\nタイムアウト: 60秒経過しても完了しませんでした")
    else:
        print("スクレイピング開始に失敗しました")
else:
    print(f"APIエラー: {response.status_code}")