#!/usr/bin/env python3
"""
最終検証: Rizeクリニック28店舗の完全な動作確認
"""

import unittest
import time
from app import app, scrapers


class TestFinalRizeClinicVerification(unittest.TestCase):
    """最終検証: Rizeクリニック28店舗の問題解決確認"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラスのセットアップ"""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        cls.test_url = "https://www.rizeclinic.com/locations/"
    
    def setUp(self):
        """各テストのセットアップ"""
        scrapers.clear()
    
    def test_complete_rize_clinic_workflow(self):
        """完全なRizeクリニックワークフローの検証"""
        print("\n=== Rizeクリニック完全ワークフローテスト ===")
        
        # Step 1: スクレイピング開始
        print("Step 1: スクレイピング開始")
        response = self.client.post('/api/scrape', 
                                  json={'url': self.test_url},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        start_data = response.get_json()
        self.assertTrue(start_data['success'])
        session_id = start_data['session_id']
        print(f"  ✓ セッション開始: {session_id}")
        
        # Step 2: 進捗追跡
        print("Step 2: 進捗追跡")
        max_wait = 45
        clinic_counts = []
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            progress_response = self.client.get(f'/api/progress/{session_id}')
            self.assertEqual(progress_response.status_code, 200)
            
            progress_data = progress_response.get_json()
            clinic_count = progress_data.get('clinic_count', 0)
            clinic_counts.append(clinic_count)
            
            status = progress_data.get('status', '')
            progress = progress_data.get('progress', 0)
            total = progress_data.get('total', 0)
            
            if progress_data.get('completed'):
                print(f"  ✓ 完了: {clinic_count}件取得")
                break
            else:
                if progress % 5 == 0 or progress < 5:  # 5の倍数または最初の5件で表示
                    print(f"  進行中: {progress}/{total} - {clinic_count}件")
            
            time.sleep(1)
        
        # Step 3: 最終結果の検証
        print("Step 3: 最終結果の検証")
        final_response = self.client.get(f'/api/progress/{session_id}')
        final_data = final_response.get_json()
        
        self.assertTrue(final_data.get('completed'), "スクレイピングが完了すべき")
        
        # 結果の詳細検証
        result = final_data.get('result', {})
        self.assertTrue(result.get('success'), "スクレイピングが成功すべき")
        self.assertEqual(result.get('clinic_count'), 28, "28店舗が取得されるべき")
        self.assertIsNotNone(result.get('filename'), "ファイル名があるべき")
        self.assertIsNotNone(result.get('download_url'), "ダウンロードURLがあるべき")
        
        # 進捗部分の検証
        self.assertEqual(final_data.get('clinic_count'), 28, "進捗のclinic_countも28であるべき")
        self.assertEqual(final_data.get('progress'), 28, "進捗が28であるべき")
        self.assertEqual(final_data.get('total'), 28, "総数が28であるべき")
        self.assertEqual(final_data.get('percentage'), 100, "進捗率が100%であるべき")
        
        print(f"  ✓ 最終結果: {result.get('clinic_count')}件")
        print(f"  ✓ ファイル: {result.get('filename')}")
        print(f"  ✓ ダウンロードURL: {result.get('download_url')}")
        
        # Step 4: 進捗の推移確認
        print("Step 4: 進捗の推移確認")
        print(f"  Clinic count progression: {clinic_counts}")
        
        # 0から28まで増加していることを確認
        self.assertGreaterEqual(max(clinic_counts), 28, "最大値が28以上であるべき")
        self.assertEqual(clinic_counts[0], 0, "最初は0件から始まるべき")
        self.assertEqual(clinic_counts[-1], 28, "最後は28件で終わるべき")
        
        print("  ✓ 進捗が0から28まで正しく増加")
        print("\n🎉 すべてのテストが成功しました！")
    
    def test_response_structure_matches_frontend_expectations(self):
        """レスポンス構造がフロントエンドの期待に合致することを確認"""
        print("\n=== フロントエンド互換性テスト ===")
        
        # スクレイピング実行
        response = self.client.post('/api/scrape', 
                                  json={'url': self.test_url},
                                  content_type='application/json')
        session_id = response.get_json()['session_id']
        
        # 完了まで待機
        time.sleep(35)  # 十分な時間待機
        
        final_response = self.client.get(f'/api/progress/{session_id}')
        final_data = final_response.get_json()
        
        # フロントエンドが期待するフィールドが全て存在することを確認
        self.assertIn('completed', final_data)
        self.assertIn('result', final_data)
        
        result = final_data['result']
        self.assertIn('success', result)
        self.assertIn('clinic_count', result)
        self.assertIn('filename', result)
        self.assertIn('download_url', result)
        
        # 型も正しいことを確認
        self.assertIsInstance(result['success'], bool)
        self.assertIsInstance(result['clinic_count'], int)
        self.assertIsInstance(result['filename'], str)
        self.assertIsInstance(result['download_url'], str)
        
        self.assertEqual(result['clinic_count'], 28)
        print("  ✓ フロントエンドの期待する構造と一致")


if __name__ == '__main__':
    unittest.main(verbosity=2)