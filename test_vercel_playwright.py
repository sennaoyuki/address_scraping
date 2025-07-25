#!/usr/bin/env python3
"""
Playwright実装: 実際のVercelアプリでRizeクリニック0店舗問題を再現・デバッグ
"""

import asyncio
from playwright.async_api import async_playwright
import json
import time

async def test_vercel_app():
    print("🎭 Playwright: Vercelアプリでの実際のテスト開始")
    
    async with async_playwright() as p:
        # ブラウザを起動（デバッグ用にheadful）
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # コンソールログをキャプチャ
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[CONSOLE] {msg.type}: {msg.text}"))
        
        # ネットワークリクエストをキャプチャ
        network_logs = []
        page.on("response", lambda response: network_logs.append({
            "url": response.url,
            "status": response.status,
            "method": response.request.method
        }))
        
        try:
            print("📍 1. Vercelアプリにアクセス中...")
            await page.goto("https://address-scraping.vercel.app/")
            await page.wait_for_load_state("networkidle")
            
            print("📍 2. URLを入力...")
            url_input = page.locator("#urlInput")
            await url_input.fill("https://www.rizeclinic.com/locations/")
            
            print("📍 3. スクレイピング開始ボタンをクリック...")
            submit_btn = page.locator("#submitBtn")
            await submit_btn.click()
            
            print("📍 4. 進捗エリアが表示されるのを待機...")
            await page.wait_for_selector("#progressArea", state="visible", timeout=10000)
            
            print("📍 5. 完了まで監視...")
            max_wait_time = 60  # 60秒まで待機
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                # 結果エリアが表示されたかチェック
                result_area = page.locator("#resultArea")
                if await result_area.is_visible():
                    print("✅ 結果エリアが表示されました！")
                    
                    # 結果メッセージを取得
                    result_message = await page.locator("#resultMessage").text_content()
                    print(f"📊 結果メッセージ: '{result_message}'")
                    
                    # 0件かどうかチェック
                    if "0 件" in result_message or "0件" in result_message:
                        print("❌ 問題確認: 0件と表示されています")
                    else:
                        print("✅ 正常: 0件以外の結果が表示されています")
                    
                    break
                
                # エラーエリアが表示されたかチェック
                error_area = page.locator("#errorArea")
                if await error_area.is_visible():
                    error_message = await page.locator("#errorMessage").text_content()
                    print(f"❌ エラーが発生: {error_message}")
                    break
                
                await asyncio.sleep(1)
            else:
                print("⏰ タイムアウト: 60秒経過しても完了しませんでした")
            
            print("\n📋 コンソールログの解析:")
            for log in console_logs[-20:]:  # 最後の20件
                print(f"  {log}")
            
            print("\n🌐 ネットワークリクエストの解析:")
            api_requests = [req for req in network_logs if "/api/" in req["url"]]
            for req in api_requests[-10:]:  # 最後の10件のAPIリクエスト
                print(f"  {req['method']} {req['url']} → {req['status']}")
            
            # APIレスポンスの詳細を取得
            print("\n🔍 APIレスポンスの詳細調査...")
            
            # 直接APIを呼び出してレスポンスを確認
            print("📡 /api/scrape を直接呼び出し...")
            scrape_response = await page.evaluate("""
                fetch('/api/scrape', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: 'https://www.rizeclinic.com/locations/'})
                }).then(r => r.json())
            """)
            print(f"scrape response: {scrape_response}")
            
            if scrape_response.get('success') and scrape_response.get('session_id'):
                session_id = scrape_response['session_id']
                print(f"📝 セッションID: {session_id}")
                
                # 数秒待ってから進捗をチェック
                await asyncio.sleep(5)
                
                print("📡 /api/progress を直接呼び出し...")
                progress_response = await page.evaluate(f"""
                    fetch('/api/progress/{session_id}').then(r => r.json())
                """)
                print(f"progress response: {json.dumps(progress_response, ensure_ascii=False, indent=2)}")
                
                # スクレイピング完了まで待機
                for i in range(30):  # 30回チェック（30秒）
                    await asyncio.sleep(2)
                    progress_response = await page.evaluate(f"""
                        fetch('/api/progress/{session_id}').then(r => r.json())
                    """)
                    
                    status = progress_response.get('status', 'unknown')
                    clinic_count = progress_response.get('clinic_count', 0)
                    completed = progress_response.get('completed', False)
                    
                    print(f"[{i+1:2d}] {status} | clinics: {clinic_count} | completed: {completed}")
                    
                    if completed:
                        print("🎯 スクレイピング完了！")
                        result = progress_response.get('result', {})
                        print(f"Final result: {json.dumps(result, ensure_ascii=False, indent=2)}")
                        
                        # 問題の詳細分析
                        result_clinic_count = result.get('clinic_count')
                        progress_clinic_count = progress_response.get('clinic_count')
                        
                        print(f"\n🔍 詳細分析:")
                        print(f"  result.clinic_count: {result_clinic_count} (type: {type(result_clinic_count)})")
                        print(f"  progress.clinic_count: {progress_clinic_count} (type: {type(progress_clinic_count)})")
                        print(f"  result.success: {result.get('success')}")
                        
                        if result_clinic_count == 0:
                            print("❌ 問題発見: result.clinic_count が 0 です！")
                        elif progress_clinic_count == 0:
                            print("❌ 問題発見: progress.clinic_count が 0 です！")
                        else:
                            print(f"✅ APIレスポンスは正常です")
                        
                        break
            
        except Exception as e:
            print(f"❌ エラーが発生: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            print("\n📱 ブラウザを5秒後に閉じます...")
            await asyncio.sleep(5)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_vercel_app())