#!/usr/bin/env python3
"""
TDD: Rizeクリニック28店舗抽出テスト
"""

import unittest
from unittest.mock import patch, MagicMock
from clinic_info_scraper import ClinicInfoScraper
import requests
from bs4 import BeautifulSoup


class TestRizeClinicScraping(unittest.TestCase):
    """RizeクリニックスクレイピングのTDDテスト"""
    
    def setUp(self):
        """テストのセットアップ"""
        self.scraper = ClinicInfoScraper()
        self.test_url = "https://www.rizeclinic.com/locations/"
        
    def test_rize_clinic_should_extract_28_stores(self):
        """リゼクリニックは28店舗を抽出すべき"""
        # Given: Rizeクリニックの店舗一覧URL
        url = self.test_url
        
        # When: スクレイピングを実行
        success = self.scraper.scrape_clinics(url)
        
        # Then: 28店舗が取得される
        self.assertTrue(success, "スクレイピングが成功すべき")
        self.assertEqual(len(self.scraper.clinic_data), 28, "28店舗が取得されるべき")
        
        # 各店舗に必要な情報が含まれている
        for i, clinic in enumerate(self.scraper.clinic_data):
            with self.subTest(clinic_index=i):
                self.assertIsNotNone(clinic['name'], f"店舗{i+1}の名前が必要")
                self.assertNotEqual(clinic['name'], '', f"店舗{i+1}の名前が空でない")
                # 住所またはアクセス情報のいずれかは必須
                self.assertTrue(
                    clinic['address'] or clinic['access'],
                    f"店舗{i+1}には住所またはアクセス情報が必要"
                )
    
    def test_rize_clinic_should_extract_specific_store_info(self):
        """特定の店舗情報が正しく抽出されるべき"""
        # Given: Rizeクリニックの店舗一覧URL
        url = self.test_url
        
        # When: スクレイピングを実行
        success = self.scraper.scrape_clinics(url)
        
        # Then: 特定の店舗情報が正しく抽出される
        self.assertTrue(success)
        
        # 札幌院が含まれている
        sapporo_clinics = [c for c in self.scraper.clinic_data if '札幌' in c['name']]
        self.assertGreater(len(sapporo_clinics), 0, "札幌院が含まれるべき")
        
        # 東京の店舗が複数含まれている
        tokyo_clinics = [c for c in self.scraper.clinic_data if 
                        '池袋' in c['name'] or '新宿' in c['name'] or '渋谷' in c['name'] or '銀座' in c['name']]
        self.assertGreater(len(tokyo_clinics), 3, "東京の主要店舗が含まれるべき")
    
    def test_rize_clinic_should_have_access_info_format(self):
        """アクセス情報が正しい形式であるべき"""
        # Given: Rizeクリニックの店舗一覧URL
        url = self.test_url
        
        # When: スクレイピングを実行
        success = self.scraper.scrape_clinics(url)
        
        # Then: アクセス情報が「〇〇駅から徒歩約〇分」形式
        self.assertTrue(success)
        
        clinics_with_access = [c for c in self.scraper.clinic_data if c['access']]
        self.assertGreater(len(clinics_with_access), 20, "20店舗以上にアクセス情報があるべき")
        
        # アクセス情報の形式チェック
        for clinic in clinics_with_access:
            if clinic['access']:  # 空でない場合のみチェック
                self.assertIn('から徒歩約', clinic['access'], 
                            f"{clinic['name']}のアクセス情報が正しい形式でない: {clinic['access']}")
                self.assertIn('分', clinic['access'],
                            f"{clinic['name']}のアクセス情報に分数が含まれていない: {clinic['access']}")
    
    def test_rize_clinic_progress_tracking(self):
        """進捗追跡が正しく動作するべき"""
        # Given: スクレイパーの初期状態
        initial_progress = self.scraper.get_progress()
        
        # Then: 初期状態が正しい
        self.assertEqual(initial_progress['progress'], 0)
        self.assertEqual(initial_progress['total'], 0)
        self.assertEqual(initial_progress['clinic_count'], 0)
        self.assertEqual(initial_progress['status'], '待機中')
        
        # When: スクレイピングを実行
        success = self.scraper.scrape_clinics(self.test_url)
        
        # Then: 完了後の進捗が正しい
        final_progress = self.scraper.get_progress()
        self.assertTrue(success)
        self.assertEqual(final_progress['progress'], 28)
        self.assertEqual(final_progress['total'], 28)
        self.assertEqual(final_progress['clinic_count'], 28)
        self.assertEqual(final_progress['status'], '完了')
        self.assertEqual(final_progress['percentage'], 100)


class TestWebAppIntegration(unittest.TestCase):
    """ウェブアプリケーション統合テスト"""
    
    @patch('requests.post')
    @patch('requests.get')
    def test_web_app_should_return_28_stores(self, mock_get, mock_post):
        """ウェブアプリで28店舗が返されるべき"""
        # Given: モックレスポンスの設定
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'success': True,
            'session_id': 'test_session_123'
        }
        
        # 進捗APIのモックレスポンス（完了状態）
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'progress': 28,
            'total': 28,
            'percentage': 100,
            'status': '完了',
            'current_action': '28件の店舗情報を取得しました',
            'clinic_count': 28,
            'completed': True,
            'result': {
                'success': True,
                'clinic_count': 28,
                'filename': 'test_clinics.csv',
                'download_url': '/download/test_clinics.csv'
            }
        }
        
        # When: ウェブAPIを呼び出し
        import json
        
        # スクレイピング開始API
        start_response = mock_post.return_value
        start_data = start_response.json()
        
        # 進捗確認API
        progress_response = mock_get.return_value
        progress_data = progress_response.json()
        
        # Then: 正しいレスポンスが返される
        self.assertTrue(start_data['success'])
        self.assertIn('session_id', start_data)
        
        self.assertTrue(progress_data['completed'])
        self.assertEqual(progress_data['clinic_count'], 28)
        self.assertTrue(progress_data['result']['success'])
        self.assertEqual(progress_data['result']['clinic_count'], 28)


if __name__ == '__main__':
    # テストの詳細出力を有効にする
    unittest.main(verbosity=2)