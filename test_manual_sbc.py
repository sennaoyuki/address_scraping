#!/usr/bin/env python3
"""
SBCサイトの手動テスト手順
"""

print("=== SBC湘南美容クリニック 手動テスト手順 ===")
print()
print("1. ブラウザで https://address-scraping.vercel.app/ を開く")
print("2. URLフィールドに以下を入力:")
print("   https://www.s-b-c.net/clinic/")
print("3. 「スクレイピング開始」ボタンをクリック")
print()
print("期待される結果:")
print("- 成功: 「〇件の店舗情報を取得しました！」と表示")
print("- タイムアウト: 「アクセスタイムアウト: このサイトは現在アクセスできない可能性があります」と表示")
print("- エラー: その他のエラーメッセージ")
print()
print("もし「サーバーとの通信に失敗しました」と表示される場合:")
print("1. ブラウザの開発者ツール（F12）を開く")
print("2. Networkタブを選択")
print("3. 再度「スクレイピング開始」をクリック")
print("4. 'scrape' リクエストの詳細を確認")
print()
print("エラー詳細の確認方法:")
print("- Consoleタブでエラーメッセージを確認")
print("- Networkタブで失敗したリクエストの詳細を確認")