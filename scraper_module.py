#!/usr/bin/env python3
"""
クリニック画像スクレイピングモジュール
ウェブアプリから呼び出すためのモジュール版
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re
import zipfile
from datetime import datetime
import shutil


class ClinicImageScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        self.progress = 0
        self.total = 0
        self.status = "待機中"
        self.current_action = ""
        self.downloaded_images = []
        
    def get_progress(self):
        """進捗状況を取得"""
        return {
            'progress': self.progress,
            'total': self.total,
            'percentage': int((self.progress / self.total * 100) if self.total > 0 else 0),
            'status': self.status,
            'current_action': self.current_action,
            'downloaded_count': len(self.downloaded_images)
        }
    
    def download_image(self, url, save_path):
        """画像をダウンロードして保存"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_images.append(save_path)
            return True
        except Exception as e:
            print(f"ダウンロードエラー: {url} - {str(e)}")
            return False
    
    def detect_clinic_images(self, soup, url):
        """複数のパターンで店舗画像を検出"""
        clinic_image_urls = set()
        domain = urlparse(url).netloc
        
        # DR.スキンクリニック専用パターン
        if 'drskinclinic' in domain:
            for img in soup.select('img[alt$="院"]'):
                if img.get('src'):
                    absolute_url = urljoin(url, img['src'])
                    clinic_image_urls.add(absolute_url)
            if clinic_image_urls:
                return clinic_image_urls
        
        # フレイアクリニック専用パターン
        if 'frey-a' in domain:
            for img in soup.find_all('img'):
                alt_text = img.get('alt', '')
                if 'フレイアクリニック' in alt_text and '院の院内風景' in alt_text:
                    if img.get('src'):
                        absolute_url = urljoin(url, img['src'])
                        clinic_image_urls.add(absolute_url)
            
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if '400x265' in src and 'media.frey-a.jp' in src:
                    absolute_url = urljoin(url, src)
                    clinic_image_urls.add(absolute_url)
            
            if clinic_image_urls:
                return clinic_image_urls
        
        # リエートクリニック専用パターン
        if 'lietoclinic' in domain:
            for i in range(1, 4):
                main_slider = soup.find(class_=f'js-clinic-mainslick_0{i}')
                if main_slider:
                    first_img = main_slider.find('img')
                    if first_img and first_img.get('src'):
                        absolute_url = urljoin(url, first_img['src'])
                        clinic_image_urls.add(absolute_url)
            if clinic_image_urls:
                return clinic_image_urls
        
        # リゼクリニック専用パターン
        if 'rizeclinic' in domain:
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if '/assets/img/locations/' in src and 'img_gallery01.jpg' in src:
                    absolute_url = urljoin(url, src)
                    clinic_image_urls.add(absolute_url)
            if clinic_image_urls:
                return clinic_image_urls
        
        # ビューティースキンクリニック専用パターン
        if 'beautyskinclinic' in domain:
            for img in soup.find_all('img'):
                alt_text = img.get('alt', '')
                src = img.get('src', '')
                if 'ビューティースキンクリニック' in alt_text and '院' in alt_text and src.endswith('.webp'):
                    absolute_url = urljoin(url, src)
                    clinic_image_urls.add(absolute_url)
            if clinic_image_urls:
                return clinic_image_urls
        
        # DIOクリニックパターン
        clinic_divs = soup.find_all('div', class_='p-clinic__item--img')
        for div in clinic_divs:
            img = div.find('img')
            if img and img.get('src'):
                absolute_url = urljoin(url, img['src'])
                if '/wp-content/uploads/' in absolute_url:
                    clinic_image_urls.add(absolute_url)
        
        # エミナルクリニックパターン
        clinic_imgs = soup.find_all('img', class_='p-clinic__clinic-card-img')
        for img in clinic_imgs:
            if img.get('src'):
                absolute_url = urljoin(url, img['src'])
                clinic_image_urls.add(absolute_url)
        
        if clinic_image_urls:
            return clinic_image_urls
        
        # 一般的なパターン
        clinic_keywords = ['clinic', 'store', 'shop', '店舗', 'facility', 'interior', 'exterior']
        
        for img in soup.find_all('img'):
            img_class = ' '.join(img.get('class', []))
            parent_class = ' '.join(img.parent.get('class', [])) if img.parent else ''
            
            if any(keyword in img_class.lower() for keyword in clinic_keywords) or \
               any(keyword in parent_class.lower() for keyword in clinic_keywords):
                if img.get('src'):
                    absolute_url = urljoin(url, img['src'])
                    if not any(exclude in absolute_url for exclude in ['icon', 'logo', 'button', 'arrow', 'banner']):
                        clinic_image_urls.add(absolute_url)
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if any(keyword in src.lower() for keyword in ['clinic', 'store', 'shop', 'facility']):
                absolute_url = urljoin(url, src)
                if not any(exclude in absolute_url for exclude in ['logo', 'icon', 'banner', 'line']):
                    clinic_image_urls.add(absolute_url)
        
        for img in soup.find_all(attrs={'data-src': True}):
            data_src = img.get('data-src')
            if data_src:
                absolute_url = urljoin(url, data_src)
                if any(keyword in absolute_url.lower() for keyword in clinic_keywords):
                    if not any(exclude in absolute_url for exclude in ['icon', 'logo', 'button', 'arrow', 'banner']):
                        clinic_image_urls.add(absolute_url)
        
        return clinic_image_urls
    
    def get_clinic_detail_urls(self, soup, base_url, domain):
        """各店舗の詳細ページURLを取得"""
        detail_urls = []
        
        if 'mens-life-clinic' in domain:
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if href.startswith('/clinic/') and '詳細' in text:
                    full_url = urljoin(base_url, href)
                    if full_url not in detail_urls and full_url != base_url:
                        detail_urls.append(full_url)
        else:
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if re.match(r'.*/clinic/[^/]+/?$', href):
                    full_url = urljoin(base_url, href)
                    if full_url not in detail_urls and full_url != base_url:
                        detail_urls.append(full_url)
        
        return detail_urls
    
    def get_clinic_images_from_detail_page(self, url, domain):
        """詳細ページから店舗画像を取得"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            image_urls = []
            
            if 'mens-life-clinic' in domain:
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if '/uploads/clinic/' in src:
                        absolute_url = urljoin(url, src)
                        image_urls.append(absolute_url)
            else:
                image_urls = list(self.detect_clinic_images(soup, url))
            
            if image_urls:
                return [image_urls[0]]  # メイン画像のみ
            
            return []
            
        except Exception as e:
            print(f"詳細ページの取得エラー: {url} - {str(e)}")
            return []
    
    def scrape_images(self, url):
        """画像をスクレイピングしてZIPファイルを作成"""
        self.progress = 0
        self.total = 0
        self.status = "処理開始"
        self.current_action = "ページを取得中..."
        self.downloaded_images = []
        
        # ドメイン名を取得
        domain = urlparse(url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # 一時保存フォルダ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_folder = f"temp_{domain}_{timestamp}"
        
        try:
            # ページを取得
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            self.current_action = "画像を検索中..."
            
            # メインページで画像を検出
            clinic_image_urls = self.detect_clinic_images(soup, url)
            
            # フィルタリング
            filtered_urls = []
            for img_url in clinic_image_urls:
                parsed = urlparse(img_url)
                path = parsed.path.lower()
                if any(path.endswith(ext) for ext in self.valid_extensions) and not path.endswith('.svg'):
                    filtered_urls.append(img_url)
            
            # メインページで画像が見つからない場合、下層ページを探索
            if len(filtered_urls) == 0:
                self.status = "下層ページを探索中"
                detail_urls = self.get_clinic_detail_urls(soup, url, domain)
                
                if detail_urls:
                    self.total = len(detail_urls)
                    for i, detail_url in enumerate(detail_urls, 1):
                        self.progress = i
                        self.current_action = f"詳細ページ {i}/{len(detail_urls)} を処理中"
                        images = self.get_clinic_images_from_detail_page(detail_url, domain)
                        filtered_urls.extend(images)
                        time.sleep(0.5)
            
            if len(filtered_urls) == 0:
                self.status = "エラー"
                self.current_action = "画像が見つかりませんでした"
                return None
            
            # 画像をダウンロード
            self.status = "ダウンロード中"
            self.total = len(filtered_urls)
            self.progress = 0
            
            for i, img_url in enumerate(filtered_urls, 1):
                self.progress = i
                self.current_action = f"画像 {i}/{len(filtered_urls)} をダウンロード中"
                
                ext = os.path.splitext(urlparse(img_url).path)[1]
                if not ext:
                    ext = '.jpg'
                filename = f"clinic_image_{i:03d}{ext}"
                save_path = os.path.join(temp_folder, filename)
                
                self.download_image(img_url, save_path)
                time.sleep(0.3)
            
            # ZIPファイルを作成
            self.status = "ZIP作成中"
            self.current_action = "ダウンロードファイルを圧縮中..."
            
            zip_filename = f"{domain}_images_{timestamp}.zip"
            # Vercel環境では/tmpディレクトリを使用
            if os.environ.get('VERCEL'):
                zip_path = os.path.join("/tmp", zip_filename)
            else:
                zip_path = os.path.join("downloads", zip_filename)
                os.makedirs("downloads", exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img_path in self.downloaded_images:
                    arcname = os.path.basename(img_path)
                    zipf.write(img_path, arcname)
            
            # 一時フォルダを削除
            shutil.rmtree(temp_folder)
            
            self.status = "完了"
            self.current_action = f"{len(self.downloaded_images)}枚の画像をダウンロードしました"
            
            return {
                'success': True,
                'filename': zip_filename,
                'download_url': f'/download/{zip_filename}',
                'image_count': len(self.downloaded_images),
                'domain': domain
            }
            
        except Exception as e:
            self.status = "エラー"
            self.current_action = str(e)
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)
            return {
                'success': False,
                'error': str(e)
            }