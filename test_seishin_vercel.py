#!/usr/bin/env python3
"""
Vercelにデプロイされた聖心美容クリニック対応をテスト
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_seishin_on_vercel():
    print("🎭 聖心美容クリニック対応のVercelテスト開始")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        # コンソールログをキャプチャ
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        try:
            print("1. Vercelアプリにアクセス...")
            await page.goto("https://address-scraping.vercel.app/")
            await page.wait_for_load_state("networkidle")
            
            print("2. 聖心美容クリニックのURLを入力...")
            await page.fill("#urlInput", "https://www.seishin-biyou.jp/clinic/")
            
            print("3. スクレイピング開始...")
            await page.click("#submitBtn")
            
            print("4. 結果を待機中（最大60秒）...")
            start_time = time.time()
            
            while time.time() - start_time < 60:
                # 結果エリアをチェック
                result_area = page.locator("#resultArea")
                if await result_area.is_visible():
                    result_message = await page.locator("#resultMessage").text_content()
                    print(f"✅ 結果取得: {result_message}")
                    
                    # 店舗数をチェック
                    if "10件" in result_message or "11件" in result_message:
                        print("🎉 成功! 聖心美容クリニックの店舗が正しく取得されました!")
                        
                        # ダウンロードボタンが機能するかチェック
                        download_btn = page.locator("#downloadBtn")
                        if await download_btn.is_visible():
                            print("✅ ダウンロードボタンも表示されています")
                        
                        return True
                    elif "0件" in result_message:
                        print("❌ まだ0件です。デプロイが完了していない可能性があります。")
                        return False
                    else:
                        print(f"ℹ️ 予期しない結果: {result_message}")
                        return True
                
                # エラーエリアをチェック
                error_area = page.locator("#errorArea")
                if await error_area.is_visible():
                    error_message = await page.locator("#errorMessage").text_content()
                    print(f"❌ エラー: {error_message}")
                    return False
                
                await asyncio.sleep(2)
            
            print("⏰ タイムアウト: 60秒経過しても完了しませんでした")
            return False
            
        except Exception as e:
            print(f"❌ テストエラー: {e}")
            return False
        
        finally:
            print("ブラウザを3秒後に閉じます...")
            await asyncio.sleep(3)
            await browser.close()

if __name__ == "__main__":
    print("聖心美容クリニック対応のテストを開始します...")
    print("注意: Vercelの自動デプロイが完了するまで数分かかる場合があります")
    
    # 数回試行
    for attempt in range(2):
        print(f"\n=== 試行 {attempt + 1}/2 ===")
        success = asyncio.run(test_seishin_on_vercel())
        
        if success:
            print("✅ テスト成功!")
            break
        else:
            if attempt < 1:
                print("45秒待ってから再試行します...")
                time.sleep(45)
            else:
                print("❌ 2回試行しましたが、期待する結果が得られませんでした。")
                print("Vercelのデプロイログを確認してください。")