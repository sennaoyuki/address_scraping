#!/usr/bin/env python3
"""
クリニック店舗情報スクレイピングモジュール
店舗名、住所、アクセス情報を取得してCSV出力
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re
import csv
from datetime import datetime
import json


class ClinicInfoScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.progress = 0
        self.total = 0
        self.status = "待機中"
        self.current_action = ""
        self.clinic_data = []
        
    def get_progress(self):
        """進捗状況を取得"""
        return {
            'progress': self.progress,
            'total': self.total,
            'percentage': int((self.progress / self.total * 100) if self.total > 0 else 0),
            'status': self.status,
            'current_action': self.current_action,
            'clinic_count': len(self.clinic_data)
        }
    
    def extract_clinic_info(self, soup, url, clinic_name=""):
        """ページから店舗情報を抽出"""
        clinic_info = {
            'name': clinic_name,
            'address': '',
            'access': '',
            'url': url
        }
        
        domain = urlparse(url).netloc
        
        # DIOクリニック
        if 'dioclinic' in domain:
            # 店舗名
            name_elem = soup.find('h2', class_='clinic-name')
            if name_elem:
                clinic_info['name'] = name_elem.get_text(strip=True)
            
            # 住所
            address_elem = soup.find('div', class_='address')
            if address_elem:
                clinic_info['address'] = address_elem.get_text(strip=True)
            
            # アクセス
            access_elem = soup.find('div', class_='access')
            if access_elem:
                clinic_info['access'] = access_elem.get_text(strip=True)
        
        # エミナルクリニック
        elif 'eminal-clinic' in domain:
            # 店舗情報テーブルから抽出
            for tr in soup.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    header = th.get_text(strip=True)
                    if '院名' in header:
                        clinic_info['name'] = td.get_text(strip=True)
                    elif '住所' in header:
                        clinic_info['address'] = td.get_text(strip=True)
                    elif 'アクセス' in header:
                        clinic_info['access'] = td.get_text(strip=True)
        
        # フレイアクリニック
        elif 'frey-a' in domain:
            # 店舗名
            h1_elem = soup.find('h1')
            if h1_elem:
                clinic_info['name'] = h1_elem.get_text(strip=True)
            
            # テーブルから情報抽出
            for tr in soup.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    header = th.get_text(strip=True)
                    if '所在地' in header:
                        clinic_info['address'] = td.get_text(strip=True)
                    elif 'アクセス' in header:
                        clinic_info['access'] = td.get_text(strip=True)
        
        # 聖心美容クリニック
        elif 'seishin-biyou' in domain:
            # 店舗名 - h1タグまたはページタイトルから取得
            h1_elem = soup.find('h1')
            if h1_elem:
                clinic_info['name'] = h1_elem.get_text(strip=True)
            
            # 住所の抽出 - より広範囲の検索
            text_content = soup.get_text()
            
            # 住所パターンの改良
            address_patterns = [
                r'〒\d{3}-\d{4}\s*[^\n]*?(?:市|区|町|村)[^\n]*?(?:丁目|番地|[0-9]+F?)',
                r'〒\d{3}-\d{4}[^\n]*',
                r'(?:東京都|大阪府|京都府|北海道|.*?県)[^\n]*?(?:市|区|町|村)[^\n]*?[0-9]',
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, text_content)
                if match:
                    address = match.group(0).strip()
                    # 余分な改行や空白を除去
                    address = re.sub(r'\s+', ' ', address)
                    clinic_info['address'] = address
                    break
            
            # アクセス情報の抽出 - 聖心美容クリニック専用パターン
            access_patterns = [
                r'([^\s]+駅)[^\n]*?(?:から|より)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
                r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
                r'アクセス[^\n]*?([^\s]+駅)[^\n]*?(\d+)分',
            ]
            
            found_station = None
            min_minutes = 999
            
            for pattern in access_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    if len(match) == 2:
                        station = match[0]
                        try:
                            minutes = int(match[1])
                            if minutes < min_minutes:
                                min_minutes = minutes
                                found_station = f"{station}から徒歩約{minutes}分"
                        except ValueError:
                            continue
            
            if found_station:
                clinic_info['access'] = found_station
            
            # もしアクセス情報が見つからない場合、「○○駅」だけでも検索
            if not clinic_info['access']:
                simple_station_pattern = r'([^\s]+駅)'
                matches = re.findall(simple_station_pattern, text_content)
                if matches:
                    # 最初に見つかった駅を使用
                    clinic_info['access'] = f"{matches[0]}最寄り"
        
        # SBC湘南美容クリニック
        elif 's-b-c.net' in domain:
            # 店舗名 - h1タグから取得
            h1_elem = soup.find('h1')
            if h1_elem:
                clinic_info['name'] = h1_elem.get_text(strip=True)
            
            # タイトルからも店舗名を取得試行
            if not clinic_info['name']:
                title_elem = soup.find('title')
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    if '院' in title_text or 'クリニック' in title_text:
                        clinic_info['name'] = title_text
            
            # 住所の抽出
            text_content = soup.get_text()
            address_patterns = [
                r'〒\d{3}-\d{4}\s*[^\n]*?(?:市|区|町|村)[^\n]*?(?:丁目|番地|[0-9]+F?)',
                r'〒\d{3}-\d{4}[^\n]*',
                r'(?:東京都|大阪府|京都府|北海道|.*?県)[^\n]*?(?:市|区|町|村)[^\n]*?[0-9]',
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, text_content)
                if match:
                    address = match.group(0).strip()
                    address = re.sub(r'\s+', ' ', address)
                    clinic_info['address'] = address
                    break
            
            # アクセス情報の抽出
            access_patterns = [
                r'([^\s]+駅)[^\n]*?(?:から|より)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
                r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
                r'アクセス[^\n]*?([^\s]+駅)[^\n]*?(\d+)分',
            ]
            
            found_station = None
            min_minutes = 999
            
            for pattern in access_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    if len(match) == 2:
                        station = match[0]
                        try:
                            minutes = int(match[1])
                            if minutes < min_minutes:
                                min_minutes = minutes
                                found_station = f"{station}から徒歩約{minutes}分"
                        except ValueError:
                            continue
            
            if found_station:
                clinic_info['access'] = found_station
            
            # アクセス情報が見つからない場合、駅名だけでも検索
            if not clinic_info['access']:
                simple_station_pattern = r'([^\s]+駅)'
                matches = re.findall(simple_station_pattern, text_content)
                if matches:
                    clinic_info['access'] = f"{matches[0]}最寄り"
        
        # リゼクリニック
        elif 'rizeclinic' in domain:
            # 店舗名 - h1タグから取得
            h1_elem = soup.find('h1')
            if h1_elem:
                clinic_info['name'] = h1_elem.get_text(strip=True)
            
            # テーブルから住所を取得
            info_table = soup.find('table')
            if info_table:
                for tr in info_table.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td')
                    if th and td:
                        header = th.get_text(strip=True)
                        if '住所' in header:
                            clinic_info['address'] = td.get_text(strip=True)
            
            # アクセス情報は正規表現で抽出
            text_content = soup.get_text()
            # 複数の駅情報パターンを探す
            station_patterns = [
                r'「([^\s]+駅)」[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
                r'「([^\s]+停留場)」[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
                r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            ]
            
            found_station = None
            min_minutes = 999
            
            # 最も近い駅を探す
            for pattern in station_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    if len(match) == 2:
                        station = match[0]
                        try:
                            minutes = int(match[1])
                            if minutes < min_minutes:
                                min_minutes = minutes
                                found_station = f"{station}から徒歩約{minutes}分"
                        except ValueError:
                            continue
            
            if found_station:
                clinic_info['access'] = found_station
        
        # 汎用的な抽出（上記以外のサイト）
        else:
            # 店舗名の抽出（h1, h2タグ）
            if not clinic_info['name']:
                for tag in ['h1', 'h2']:
                    elem = soup.find(tag)
                    if elem:
                        text = elem.get_text(strip=True)
                        if '院' in text or 'クリニック' in text:
                            clinic_info['name'] = text
                            break
            
            # 住所の抽出（住所っぽいパターン）
            address_patterns = [
                r'〒\d{3}-\d{4}.*?(?:都|道|府|県).*?(?:市|区|町|村)',
                r'(?:東京都|大阪府|京都府|北海道|.*?県).*?(?:市|区|町|村).*?\d+',
            ]
            
            text_content = soup.get_text()
            for pattern in address_patterns:
                match = re.search(pattern, text_content)
                if match:
                    clinic_info['address'] = match.group(0)
                    break
            
            # アクセス情報の抽出（駅名と徒歩分数）
            access_patterns = [
                r'([^\s]+駅).*?(?:徒歩|歩いて).*?(\d+)分',
                r'([^\s]+停留場).*?(?:徒歩|歩いて).*?(\d+)分',
            ]
            
            found_station = None
            min_minutes = 999
            
            for pattern in access_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    if len(match) == 2:
                        station = match[0]
                        try:
                            minutes = int(match[1])
                            if minutes < min_minutes:
                                min_minutes = minutes
                                found_station = f"{station}から徒歩約{minutes}分"
                        except ValueError:
                            continue
            
            if found_station:
                clinic_info['access'] = found_station
        
        return clinic_info
    
    def find_clinic_links(self, soup, base_url):
        """店舗一覧ページから各店舗のリンクを取得"""
        clinic_links = []
        domain = urlparse(base_url).netloc
        
        # 店舗リンクのパターン
        link_patterns = [
            r'/clinic/[^/]+/?$',
            r'/store/[^/]+/?$',
            r'/shop/[^/]+/?$',
            r'/access/[^/]+/?$',
            r'/locations/[^/]+/?$',  # リゼクリニック用
            r'/clinic/branch/[^/]+/?$',  # SBC湘南美容クリニック用
            r'/hifuka/[^/]+/?$',  # SBC湘南美容クリニック用
        ]
        
        # すべてのリンクを確認
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(base_url, href)
            
            # パターンマッチング
            for pattern in link_patterns:
                if re.search(pattern, href):
                    # 一覧ページ自身へのリンクは除外
                    if absolute_url.rstrip('/') != base_url.rstrip('/'):
                        clinic_links.append({
                            'url': absolute_url,
                            'name': a.get_text(strip=True)
                        })
                        break
        
        # 重複を除去
        seen = set()
        unique_links = []
        for link in clinic_links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        return unique_links
    
    def scrape_clinics(self, url):
        """メイン処理"""
        try:
            self.status = "ページを取得中..."
            self.current_action = f"URL: {url}"
            
            # ページ取得
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # まず現在のページから情報を抽出
            self.status = "店舗情報を抽出中..."
            current_page_info = self.extract_clinic_info(soup, url)
            
            # 店舗情報が取得できた場合は追加
            if current_page_info['name'] and (current_page_info['address'] or current_page_info['access']):
                self.clinic_data.append(current_page_info)
                self.progress = 1
                self.total = 1
            
            # 店舗一覧ページかチェック（複数の店舗リンクがある場合）
            clinic_links = self.find_clinic_links(soup, url)
            
            if len(clinic_links) > 3:  # 3つ以上のリンクがある場合は一覧ページと判断
                self.total = len(clinic_links)
                self.progress = 0
                
                for i, link in enumerate(clinic_links):
                    self.progress = i + 1
                    self.status = f"店舗情報を取得中... ({self.progress}/{self.total})"
                    self.current_action = f"取得中: {link['name']}"
                    
                    try:
                        # 各店舗ページを取得
                        clinic_response = requests.get(link['url'], headers=self.headers, timeout=10)
                        clinic_response.raise_for_status()
                        clinic_soup = BeautifulSoup(clinic_response.content, 'html.parser')
                        
                        # 店舗情報を抽出
                        clinic_info = self.extract_clinic_info(clinic_soup, link['url'], link['name'])
                        if clinic_info['name']:
                            self.clinic_data.append(clinic_info)
                        
                        time.sleep(1)  # サーバー負荷軽減
                        
                    except Exception as e:
                        print(f"店舗ページ取得エラー: {link['url']} - {str(e)}")
                        continue
            
            self.status = "完了"
            self.current_action = f"{len(self.clinic_data)}件の店舗情報を取得しました"
            
            return True
            
        except Exception as e:
            self.status = "エラー"
            self.current_action = str(e)
            return False
    
    def save_to_csv(self, filename=None):
        """取得したデータをCSVに保存"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = urlparse(self.clinic_data[0]['url']).netloc if self.clinic_data else 'clinics'
            filename = f"downloads/{domain}_clinics_{timestamp}.csv"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['店舗名', '住所', 'アクセス', 'URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for clinic in self.clinic_data:
                writer.writerow({
                    '店舗名': clinic['name'],
                    '住所': clinic['address'],
                    'アクセス': clinic['access'],
                    'URL': clinic['url']
                })
        
        return filename


# テスト用
if __name__ == "__main__":
    # テストURL
    test_url = input("クリニックのURLを入力してください: ").strip()
    
    scraper = ClinicInfoScraper()
    
    print("スクレイピングを開始します...")
    success = scraper.scrape_clinics(test_url)
    
    if success and scraper.clinic_data:
        csv_file = scraper.save_to_csv()
        print(f"\nCSVファイルを保存しました: {csv_file}")
        print(f"取得した店舗数: {len(scraper.clinic_data)}")
        
        # 結果を表示
        for clinic in scraper.clinic_data:
            print(f"\n店舗名: {clinic['name']}")
            print(f"住所: {clinic['address']}")
            print(f"アクセス: {clinic['access']}")
    else:
        print("スクレイピングに失敗しました")