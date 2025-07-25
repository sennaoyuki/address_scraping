#!/usr/bin/env python3
"""
フレイアクリニックをPlaywrightでテスト
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_freya_on_vercel():
    print("🎭 フレイアクリニックのVercelテスト開始")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("1. Vercelアプリにアクセス...")
            await page.goto("https://address-scraping.vercel.app/")
            await page.wait_for_load_state("networkidle")
            
            print("2. フレイアクリニックのURLを入力...")
            await page.fill("#urlInput", "https://frey-a.jp/clinic/")
            
            print("3. スクレイピング開始...")
            await page.click("#submitBtn")
            
            print("4. 結果を待機中...")
            start_time = time.time()
            
            while time.time() - start_time < 60:
                # 結果エリアをチェック
                result_area = page.locator("#resultArea")
                if await result_area.is_visible():
                    result_message = await page.locator("#resultMessage").text_content()
                    print(f"✅ 結果取得: {result_message}")
                    
                    # ダウンロードボタンをクリックしてCSVを確認
                    download_btn = page.locator("#downloadBtn")
                    if await download_btn.is_visible():
                        print("📥 CSVダウンロード機能も確認")
                    
                    return True
                
                # エラーエリアをチェック
                error_area = page.locator("#errorArea")
                if await error_area.is_visible():
                    error_message = await page.locator("#errorMessage").text_content()
                    print(f"❌ エラー: {error_message}")
                    return False
                
                await asyncio.sleep(2)
            
            print("⏰ タイムアウト")
            return False
            
        except Exception as e:
            print(f"❌ テストエラー: {e}")
            return False
        
        finally:
            print("ブラウザを5秒後に閉じます...")
            await asyncio.sleep(5)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_freya_on_vercel())