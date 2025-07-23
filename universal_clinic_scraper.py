#!/usr/bin/env python3
"""
汎用クリニック画像スクレイピングスクリプト（自動判定版）
メインページで画像が見つからない場合、自動的に下層ページを探索
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re


def download_image(url, save_path):
    """画像をダウンロードして保存"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ ダウンロード完了: {os.path.basename(save_path)}")
        return True
    except Exception as e:
        print(f"✗ ダウンロード失敗: {url}")
        print(f"  エラー: {str(e)}")
        return False


def detect_clinic_images(soup, url):
    """複数のパターンで店舗画像を検出"""
    clinic_image_urls = set()
    domain = urlparse(url).netloc
    
    # DR.スキンクリニック専用パターン（最優先）
    if 'drskinclinic' in domain:
        # altタグが「院」で終わる画像のみを取得
        for img in soup.select('img[alt$="院"]'):
            if img.get('src'):
                absolute_url = urljoin(url, img['src'])
                clinic_image_urls.add(absolute_url)
        
        # このパターンで画像が見つかった場合は、他のパターンは使わない
        if clinic_image_urls:
            return clinic_image_urls
    
    # フレイアクリニック専用パターン
    if 'frey-a' in domain:
        # altタグに「フレイアクリニック」と「院の院内風景」を含む画像を取得
        for img in soup.find_all('img'):
            alt_text = img.get('alt', '')
            if 'フレイアクリニック' in alt_text and '院の院内風景' in alt_text:
                if img.get('src'):
                    absolute_url = urljoin(url, img['src'])
                    clinic_image_urls.add(absolute_url)
        
        # 400x265サイズの画像も追加（フレイアの標準サイズ）
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if '400x265' in src and 'media.frey-a.jp' in src:
                absolute_url = urljoin(url, src)
                clinic_image_urls.add(absolute_url)
        
        # このパターンで画像が見つかった場合は、他のパターンは使わない
        if clinic_image_urls:
            return clinic_image_urls
    
    # リエートクリニック専用パターン（各店舗のメイン画像のみ）
    if 'lietoclinic' in domain:
        # 各店舗のメインスライダーから最初の画像を取得
        for i in range(1, 4):  # 3店舗分
            # js-clinic-mainslick_0X クラスを持つメインスライダーを探す
            main_slider = soup.find(class_=f'js-clinic-mainslick_0{i}')
            if main_slider:
                # 最初の画像を取得
                first_img = main_slider.find('img')
                if first_img and first_img.get('src'):
                    absolute_url = urljoin(url, first_img['src'])
                    clinic_image_urls.add(absolute_url)
        
        # このパターンで画像が見つかった場合は、他のパターンは使わない
        if clinic_image_urls:
            return clinic_image_urls
    
    # リゼクリニック専用パターン
    if 'rizeclinic' in domain:
        # /assets/img/locations/ パスを含む画像を探す
        for img in soup.find_all('img'):
            src = img.get('src', '')
            # img_gallery01.jpg という名前の画像（各店舗のメイン画像）
            if '/assets/img/locations/' in src and 'img_gallery01.jpg' in src:
                absolute_url = urljoin(url, src)
                clinic_image_urls.add(absolute_url)
        
        # このパターンで画像が見つかった場合は、他のパターンは使わない
        if clinic_image_urls:
            return clinic_image_urls
    
    # ビューティースキンクリニック専用パターン
    if 'beautyskinclinic' in domain:
        # altタグに「ビューティースキンクリニック」と「院」を含む画像のみを取得
        for img in soup.find_all('img'):
            alt_text = img.get('alt', '')
            src = img.get('src', '')
            # 店舗画像の条件: altタグに「ビューティースキンクリニック」と「院」を含み、.webp形式
            if 'ビューティースキンクリニック' in alt_text and '院' in alt_text and src.endswith('.webp'):
                absolute_url = urljoin(url, src)
                clinic_image_urls.add(absolute_url)
        
        # このパターンで画像が見つかった場合は、他のパターンは使わない
        if clinic_image_urls:
            return clinic_image_urls
    
    # パターン1: DIOクリニック (p-clinic__item--img クラス)
    clinic_divs = soup.find_all('div', class_='p-clinic__item--img')
    for div in clinic_divs:
        img = div.find('img')
        if img and img.get('src'):
            absolute_url = urljoin(url, img['src'])
            if '/wp-content/uploads/' in absolute_url:
                clinic_image_urls.add(absolute_url)
    
    # パターン2: エミナルクリニック (p-clinic__clinic-card-img クラス)
    clinic_imgs = soup.find_all('img', class_='p-clinic__clinic-card-img')
    for img in clinic_imgs:
        if img.get('src'):
            absolute_url = urljoin(url, img['src'])
            clinic_image_urls.add(absolute_url)
    
    # 既に画像が見つかっている場合は、ここで返す
    if clinic_image_urls:
        return clinic_image_urls
    
    # パターン3: 一般的なクリニック画像パターン（フォールバック）
    # 店舗・クリニック関連のキーワードを含むクラス名
    clinic_keywords = ['clinic', 'store', 'shop', '店舗', 'facility', 'interior', 'exterior']
    
    # クラス名にキーワードを含む画像を探す
    for img in soup.find_all('img'):
        img_class = ' '.join(img.get('class', []))
        parent_class = ' '.join(img.parent.get('class', [])) if img.parent else ''
        
        # クラス名チェック
        if any(keyword in img_class.lower() for keyword in clinic_keywords) or \
           any(keyword in parent_class.lower() for keyword in clinic_keywords):
            if img.get('src'):
                absolute_url = urljoin(url, img['src'])
                # 小さいアイコンやロゴを除外
                if not any(exclude in absolute_url for exclude in ['icon', 'logo', 'button', 'arrow', 'banner']):
                    clinic_image_urls.add(absolute_url)
    
    # パターン4: 画像パスに店舗関連キーワードを含む
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if any(keyword in src.lower() for keyword in ['clinic', 'store', 'shop', 'facility']):
            absolute_url = urljoin(url, src)
            # ロゴやアイコンを除外
            if not any(exclude in absolute_url for exclude in ['logo', 'icon', 'banner', 'line']):
                clinic_image_urls.add(absolute_url)
    
    # data-src属性（遅延読み込み）もチェック
    for img in soup.find_all(attrs={'data-src': True}):
        data_src = img.get('data-src')
        if data_src:
            absolute_url = urljoin(url, data_src)
            # 同様のフィルタリングを適用
            if any(keyword in absolute_url.lower() for keyword in clinic_keywords):
                if not any(exclude in absolute_url for exclude in ['icon', 'logo', 'button', 'arrow', 'banner']):
                    clinic_image_urls.add(absolute_url)
    
    return clinic_image_urls


def get_clinic_detail_urls(soup, base_url, domain):
    """各店舗の詳細ページURLを取得"""
    detail_urls = []
    
    # メンズライフクリニックのパターン
    if 'mens-life-clinic' in domain:
        # 「詳細はこちら」リンクを探す
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            # /clinic/で始まり、詳細ページへのリンク
            if href.startswith('/clinic/') and '詳細' in text:
                full_url = urljoin(base_url, href)
                # 重複を避ける
                if full_url not in detail_urls and full_url != base_url:
                    detail_urls.append(full_url)
    else:
        # 汎用パターン: クリニック関連のリンクを探す
        for link in soup.find_all('a'):
            href = link.get('href', '')
            # clinic/店舗名 のパターン
            if re.match(r'.*/clinic/[^/]+/?$', href):
                full_url = urljoin(base_url, href)
                if full_url not in detail_urls and full_url != base_url:
                    detail_urls.append(full_url)
    
    return detail_urls


def get_clinic_images_from_detail_page(url, domain):
    """詳細ページから店舗画像を取得"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        image_urls = []
        
        # メンズライフクリニックのパターン: /uploads/clinic/ を含む画像
        if 'mens-life-clinic' in domain:
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if '/uploads/clinic/' in src:
                    absolute_url = urljoin(url, src)
                    image_urls.append(absolute_url)
        else:
            # 汎用パターン: 通常の検出パターンを使用
            image_urls = list(detect_clinic_images(soup, url))
        
        # 最初の画像（メイン画像）のみを返す
        if image_urls:
            return [image_urls[0]]  # メイン画像のみ
        
        return []
        
    except Exception as e:
        print(f"詳細ページの取得エラー: {url} - {str(e)}")
        return []


def scrape_clinic_images(url):
    """クリニックページから店舗画像をスクレイピング（自動判定）"""
    
    # ドメイン名を取得
    domain = urlparse(url).netloc
    # www.を除外
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # 保存先フォルダを作成（clinic_images/ドメイン名）
    base_folder = "clinic_images"
    save_folder = os.path.join(base_folder, domain)
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"保存先フォルダを作成: {save_folder}")
    
    try:
        # ページを取得
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # まずメインページで画像を検出
        clinic_image_urls = detect_clinic_images(soup, url)
        
        # 有効な画像拡張子でフィルタリング（SVGを除外）
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        filtered_urls = []
        
        for img_url in clinic_image_urls:
            parsed = urlparse(img_url)
            path = parsed.path.lower()
            # SVGを除外し、有効な拡張子のみを許可
            if any(path.endswith(ext) for ext in valid_extensions) and not path.endswith('.svg'):
                filtered_urls.append(img_url)
        
        print(f"メインページで発見した店舗画像数: {len(filtered_urls)}")
        
        # メインページで画像が見つからない場合、下層ページを探索
        if len(filtered_urls) == 0:
            print("\nメインページに画像が見つかりません。下層ページを探索します...")
            
            # 各店舗の詳細ページURLを取得
            detail_urls = get_clinic_detail_urls(soup, url, domain)
            
            if detail_urls:
                print(f"{len(detail_urls)}個の店舗詳細ページを発見しました。")
                
                # 各詳細ページから画像を取得
                for i, detail_url in enumerate(detail_urls, 1):
                    print(f"\n[{i}/{len(detail_urls)}] {detail_url} を処理中...")
                    images = get_clinic_images_from_detail_page(detail_url, domain)
                    filtered_urls.extend(images)
                    time.sleep(1)  # サーバーへの負荷を軽減
                
                print(f"\n下層ページから合計 {len(filtered_urls)} 個の店舗画像を発見しました。")
        
        if len(filtered_urls) == 0:
            print("店舗画像が見つかりませんでした。")
            print("ヒント: ページ構造が特殊な場合は、開発者ツールで画像のクラス名を確認してください。")
            return
        
        # 画像をダウンロード
        downloaded = 0
        for i, img_url in enumerate(filtered_urls, 1):
            # ファイル名を生成
            ext = os.path.splitext(urlparse(img_url).path)[1]
            if not ext:
                ext = '.jpg'
            filename = f"clinic_image_{i:03d}{ext}"
            save_path = os.path.join(save_folder, filename)
            
            if download_image(img_url, save_path):
                downloaded += 1
            time.sleep(0.5)  # サーバーに負荷をかけないよう遅延を入れる
        
        print(f"\n完了: {downloaded}/{len(filtered_urls)} 店舗画像をダウンロードしました")
        print(f"保存先: {os.path.abspath(save_folder)}")
        print(f"ドメイン: {domain}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")


if __name__ == "__main__":
    import sys
    
    # コマンドライン引数からURLを取得
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        print("使用方法: python3 universal_clinic_scraper.py [URL]")
        print("例: python3 universal_clinic_scraper.py https://dioclinic.jp/clinic/")
        print("例: python3 universal_clinic_scraper.py https://www.mens-life-clinic.com/clinic/")
        print("\n自動判定機能:")
        print("- メインページで画像が見つかればそれを使用")
        print("- 見つからない場合は下層ページを自動探索")
        sys.exit(1)
    
    print(f"スクレイピング開始: {target_url}")
    print("-" * 50)
    
    scrape_clinic_images(target_url)