#!/usr/bin/env python3
"""
TDD: ウェブアプリ統合テスト - Rizeクリニック28店舗問題の再現
"""

import unittest
import threading
import time
import requests
from app import app, scrapers
from clinic_info_scraper import ClinicInfoScraper


class TestWebAppRizeClinicIntegration(unittest.TestCase):
    """ウェブアプリでのRizeクリニック統合テスト"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラスのセットアップ - Flaskアプリを起動"""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        cls.test_url = "https://www.rizeclinic.com/locations/"
    
    def setUp(self):
        """各テストのセットアップ"""
        # セッションデータをクリア
        scrapers.clear()
    
    def test_web_app_should_return_28_stores_not_0(self):
        """ウェブアプリは28店舗を返すべき（0件ではない）"""
        # Given: Rizeクリニックの店舗一覧URL
        payload = {'url': self.test_url}
        
        # When: スクレイピングを開始
        response = self.client.post('/api/scrape', 
                                  json=payload,
                                  content_type='application/json')
        
        # Then: 正常にセッションが開始される
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('session_id', data)
        
        session_id = data['session_id']
        
        # スクレイピング完了まで待機
        max_wait_time = 60  # 最大60秒待機
        start_time = time.time()
        completed = False
        final_result = None
        
        while time.time() - start_time < max_wait_time:
            progress_response = self.client.get(f'/api/progress/{session_id}')
            self.assertEqual(progress_response.status_code, 200)
            
            progress_data = progress_response.get_json()
            print(f"Progress: {progress_data}")  # デバッグ用
            
            if progress_data.get('completed'):
                completed = True
                final_result = progress_data.get('result')
                break
            
            time.sleep(1)
        
        # Then: スクレイピングが完了し、28店舗が取得される
        self.assertTrue(completed, "スクレイピングが時間内に完了すべき")
        self.assertIsNotNone(final_result, "結果が返されるべき")
        self.assertTrue(final_result['success'], "スクレイピングが成功すべき")
        
        # 重要: 0件ではなく28件が取得されることを確認
        clinic_count = final_result.get('clinic_count', 0)
        self.assertNotEqual(clinic_count, 0, "店舗数が0件であってはならない")
        self.assertEqual(clinic_count, 28, "28店舗が取得されるべき")
    
    def test_progress_api_includes_clinic_count_during_scraping(self):
        """進捗APIがスクレイピング中にclinic_countを含むべき"""
        # Given: スクレイピングセッションを開始
        payload = {'url': self.test_url}
        response = self.client.post('/api/scrape', 
                                  json=payload,
                                  content_type='application/json')
        
        session_id = response.get_json()['session_id']
        
        # When: 進捗を複数回チェック
        clinic_counts = []
        max_checks = 10
        
        for i in range(max_checks):
            progress_response = self.client.get(f'/api/progress/{session_id}')
            progress_data = progress_response.get_json()
            
            # Then: clinic_countが常に含まれる
            self.assertIn('clinic_count', progress_data, 
                         f"Progress response {i+1} should include clinic_count")
            
            clinic_count = progress_data['clinic_count']
            clinic_counts.append(clinic_count)
            
            if progress_data.get('completed'):
                break
            
            time.sleep(2)
        
        # 最終的に28店舗が取得される
        final_count = clinic_counts[-1] if clinic_counts else 0
        self.assertEqual(final_count, 28, f"最終的に28店舗が取得されるべき。取得数の変遷: {clinic_counts}")
    
    def test_scraper_instance_directly_works(self):
        """スクレイパーインスタンスが直接動作することを確認"""
        # Given: 新しいスクレイパーインスタンス
        scraper = ClinicInfoScraper()
        
        # When: 直接スクレイピングを実行
        success = scraper.scrape_clinics(self.test_url)
        
        # Then: 28店舗が取得される
        self.assertTrue(success, "スクレイピングが成功すべき")
        self.assertEqual(len(scraper.clinic_data), 28, 
                        f"28店舗が取得されるべき。実際: {len(scraper.clinic_data)}")
        
        # 進捗情報も正しい
        progress = scraper.get_progress()
        self.assertEqual(progress['clinic_count'], 28)
        self.assertEqual(progress['progress'], 28)
        self.assertEqual(progress['total'], 28)


class TestCurrentWebAppBehavior(unittest.TestCase):
    """現在のウェブアプリの動作を記録するテスト"""
    
    def test_current_webapp_behavior_documentation(self):
        """現在のウェブアプリの動作を記録（失敗が予想される）"""
        # このテストは現在の問題を記録するためのもの
        # 直接スクレイパーは28店舗を返すが、ウェブアプリでは0店舗になる問題
        
        app.config['TESTING'] = True
        client = app.test_client()
        
        # スクレイピング開始
        response = client.post('/api/scrape', 
                             json={'url': 'https://www.rizeclinic.com/locations/'},
                             content_type='application/json')
        
        if response.status_code == 200:
            session_id = response.get_json()['session_id']
            
            # 短時間だけ待機して進捗をチェック
            time.sleep(3)
            progress_response = client.get(f'/api/progress/{session_id}')
            
            if progress_response.status_code == 200:
                progress_data = progress_response.get_json()
                print(f"現在のウェブアプリの動作: {progress_data}")
                
                # 現在の問題: clinic_countが0になっている可能性が高い
                clinic_count = progress_data.get('clinic_count', 'NOT_FOUND')
                print(f"Clinic count in web app: {clinic_count}")


if __name__ == '__main__':
    unittest.main(verbosity=2)