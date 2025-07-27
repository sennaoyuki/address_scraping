#!/usr/bin/env python3
"""
Universal Store Information Scraper
A flexible and intelligent scraping system that can extract store information from any website
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag
from collections import Counter
import unicodedata


class PatternMatcher:
    """Pattern matching utilities for information extraction"""
    
    # Japanese address patterns
    ADDRESS_PATTERNS = [
        # With postal code
        (r'〒\s*(\d{3}[-ー－]\d{4})\s*([^\n\r]{1,100})', 100),
        (r'〒\s*(\d{7})\s*([^\n\r]{1,100})', 95),
        
        # Full address patterns
        (r'((?:東京都|大阪府|京都府|北海道|[^\s]{2,4}県)[^\n\r]*?(?:市|区|町|村)[^\n\r]*?(?:\d+(?:[-ー－]\d+)*(?:番地?)?|[一二三四五六七八九十]+丁目)[^\n\r]*)', 90),
        (r'((?:東京都|大阪府|京都府|北海道|[^\s]{2,4}県)[^\n\r]*?[市区町村][^\n\r]*?\d+[-ー－]\d+[-ー－]\d+)', 85),
        
        # Building/Floor patterns
        (r'([^\n\r]*?(?:ビル|ビルディング|タワー|センター|プラザ|[^\s]+館)[^\n\r]*?(?:\d+階|[一二三四五六七八九十]+階|B\d+F?|\d+F))', 70),
    ]
    
    # Access/Station patterns
    ACCESS_PATTERNS = [
        # Station with walking time
        (r'「?([^「」\s]+(?:駅|停留場))」?\s*(?:から|より)?\s*(?:徒歩|歩いて)?\s*(?:約)?\s*(\d+)\s*分', 100),
        (r'([^「」\s]+(?:駅|停留場))\s*(?:徒歩|歩いて)\s*(?:約)?\s*(\d+)\s*分', 95),
        (r'(?:最寄り?駅?[:：]?\s*)([^「」\s]+駅)[^\n\r]*?(\d+)\s*分', 90),
        
        # Station only patterns
        (r'(?:最寄り?駅?[:：]?\s*)「?([^「」\s]+駅)」?', 70),
        (r'(?:アクセス|交通)[^\n\r]*?「?([^「」\s]+駅)」?', 65),
        
        # Line and station
        (r'([^「」\s]+線)\s*「?([^「」\s]+駅)」?', 80),
    ]
    
    # Phone number patterns
    PHONE_PATTERNS = [
        (r'(?:TEL|Tel|tel|電話|☎|📞)\s*[:：]?\s*([\d\-\(\)]{10,})', 100),
        (r'(\d{2,4}[-ー－]\d{2,4}[-ー－]\d{3,4})', 90),
        (r'(\d{10,11})', 70),
    ]
    
    # Business hours patterns
    HOURS_PATTERNS = [
        (r'(?:営業時間|受付時間|診療時間)[^\n\r]*?[:：]?\s*([^\n\r]+)', 100),
        (r'(\d{1,2}[:：]\d{2}\s*[~〜～ー－-]\s*\d{1,2}[:：]\d{2})', 90),
        (r'(?:平日|月.金)\s*[:：]?\s*(\d{1,2}[:：]\d{2}\s*[~〜～ー－-]\s*\d{1,2}[:：]\d{2})', 85),
    ]
    
    @classmethod
    def extract_with_confidence(cls, text: str, patterns: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        """Extract information with confidence scores"""
        results = []
        for pattern, base_confidence in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match).strip()
                else:
                    match = match.strip()
                if match:
                    results.append((match, base_confidence))
        return results


class StructuralAnalyzer:
    """Analyze HTML structure to identify information patterns"""
    
    @staticmethod
    def find_info_tables(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find and analyze information tables"""
        info_tables = []
        
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = tr.find_all(['th', 'td'])
                if len(cells) >= 2:
                    header = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    rows.append({'header': header, 'value': value})
            
            if rows:
                info_tables.append({
                    'element': table,
                    'rows': rows,
                    'confidence': 100 if len(rows) > 3 else 80
                })
        
        return info_tables
    
    @staticmethod
    def find_definition_lists(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find and analyze definition lists (dl/dt/dd)"""
        info_lists = []
        
        for dl in soup.find_all('dl'):
            items = []
            dt_elements = dl.find_all('dt')
            dd_elements = dl.find_all('dd')
            
            for dt, dd in zip(dt_elements, dd_elements):
                if dt and dd:
                    items.append({
                        'header': dt.get_text(strip=True),
                        'value': dd.get_text(strip=True)
                    })
            
            if items:
                info_lists.append({
                    'element': dl,
                    'items': items,
                    'confidence': 95
                })
        
        return info_lists
    
    @staticmethod
    def find_info_sections(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find sections that likely contain store information"""
        info_sections = []
        info_keywords = ['店舗', '住所', 'アクセス', '所在地', '交通', '営業', '電話', 'TEL', 'Address', 'Access', 'Location']
        
        # Check various container elements
        for container in soup.find_all(['div', 'section', 'article']):
            text_content = container.get_text(strip=True)
            
            # Count matching keywords
            keyword_count = sum(1 for keyword in info_keywords if keyword in text_content)
            
            if keyword_count >= 2:
                info_sections.append({
                    'element': container,
                    'keyword_count': keyword_count,
                    'confidence': min(100, 60 + keyword_count * 10)
                })
        
        # Sort by confidence
        info_sections.sort(key=lambda x: x['confidence'], reverse=True)
        return info_sections[:10]  # Top 10 most likely sections


class IntelligentExtractor:
    """Main extraction engine with intelligent pattern recognition"""
    
    def __init__(self):
        self.pattern_matcher = PatternMatcher()
        self.structural_analyzer = StructuralAnalyzer()
    
    def extract_store_name(self, soup: BeautifulSoup, url: str) -> Tuple[str, int]:
        """Extract store name with confidence score"""
        candidates = []
        
        # 1. Check page title
        title_elem = soup.find('title')
        if title_elem:
            title = title_elem.get_text(strip=True)
            # Common patterns in titles
            if any(keyword in title for keyword in ['店', '院', 'クリニック', '店舗', 'ストア', 'ショップ']):
                candidates.append((title.split('|')[0].strip(), 85))
        
        # 2. Check h1 tags
        for h1 in soup.find_all('h1'):
            text = h1.get_text(strip=True)
            if text and len(text) < 100:
                confidence = 90
                if any(keyword in text for keyword in ['店', '院', 'クリニック', '店舗']):
                    confidence = 95
                candidates.append((text, confidence))
        
        # 3. Check h2 tags with store keywords
        for h2 in soup.find_all('h2'):
            text = h2.get_text(strip=True)
            if any(keyword in text for keyword in ['店', '院', 'クリニック', '店舗', 'ストア']):
                candidates.append((text, 80))
        
        # 4. Check meta property og:site_name
        og_site = soup.find('meta', property='og:site_name')
        if og_site and og_site.get('content'):
            candidates.append((og_site['content'], 75))
        
        # 5. Check structured data (JSON-LD)
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get('@type') in ['Store', 'LocalBusiness', 'MedicalClinic']:
                        if data.get('name'):
                            candidates.append((data['name'], 100))
                    elif data.get('name'):
                        candidates.append((data['name'], 70))
            except:
                continue
        
        # Return the highest confidence candidate
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0]
        
        return "", 0
    
    def extract_address(self, soup: BeautifulSoup) -> Tuple[str, int]:
        """Extract address with confidence score"""
        text_content = soup.get_text()
        candidates = []
        
        # 1. Pattern matching on full text
        address_matches = self.pattern_matcher.extract_with_confidence(
            text_content, 
            PatternMatcher.ADDRESS_PATTERNS
        )
        candidates.extend(address_matches)
        
        # 2. Check structured containers
        tables = self.structural_analyzer.find_info_tables(soup)
        for table in tables:
            for row in table['rows']:
                if any(keyword in row['header'] for keyword in ['住所', '所在地', 'Address', 'Location']):
                    candidates.append((row['value'], 95))
        
        # 3. Check definition lists
        dl_lists = self.structural_analyzer.find_definition_lists(soup)
        for dl in dl_lists:
            for item in dl['items']:
                if any(keyword in item['header'] for keyword in ['住所', '所在地', 'Address']):
                    candidates.append((item['value'], 95))
        
        # 4. Check structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('address'):
                    addr = data['address']
                    if isinstance(addr, dict):
                        parts = []
                        if addr.get('postalCode'):
                            parts.append(f"〒{addr['postalCode']}")
                        if addr.get('addressRegion'):
                            parts.append(addr['addressRegion'])
                        if addr.get('addressLocality'):
                            parts.append(addr['addressLocality'])
                        if addr.get('streetAddress'):
                            parts.append(addr['streetAddress'])
                        if parts:
                            candidates.append((' '.join(parts), 100))
                    elif isinstance(addr, str):
                        candidates.append((addr, 100))
            except:
                continue
        
        # Clean and deduplicate
        cleaned_candidates = []
        seen = set()
        for addr, conf in candidates:
            # Clean address
            addr = re.sub(r'\s+', ' ', addr).strip()
            # Normalize
            addr_normalized = unicodedata.normalize('NFKC', addr)
            
            if addr_normalized and addr_normalized not in seen:
                seen.add(addr_normalized)
                cleaned_candidates.append((addr, conf))
        
        if cleaned_candidates:
            cleaned_candidates.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
            return cleaned_candidates[0]
        
        return "", 0
    
    def extract_access(self, soup: BeautifulSoup) -> Tuple[str, int]:
        """Extract access information with confidence score"""
        text_content = soup.get_text()
        candidates = []
        
        # 1. Pattern matching for station access
        access_matches = self.pattern_matcher.extract_with_confidence(
            text_content,
            PatternMatcher.ACCESS_PATTERNS
        )
        
        # Process matches to find the best station info
        station_info = {}
        for match, conf in access_matches:
            # Extract station and minutes
            station_match = re.search(r'([^「」\s]+(?:駅|停留場))', match)
            minutes_match = re.search(r'(\d+)\s*分', match)
            
            if station_match:
                station = station_match.group(1)
                minutes = minutes_match.group(1) if minutes_match else None
                
                if station not in station_info or conf > station_info[station][1]:
                    station_info[station] = (minutes, conf)
        
        # Format station information
        for station, (minutes, conf) in station_info.items():
            if minutes:
                candidates.append((f"{station}から徒歩約{minutes}分", conf))
            else:
                candidates.append((f"{station}最寄り", conf - 20))
        
        # 2. Check structured data
        tables = self.structural_analyzer.find_info_tables(soup)
        for table in tables:
            for row in table['rows']:
                if any(keyword in row['header'] for keyword in ['アクセス', '交通', 'Access', '最寄り駅']):
                    candidates.append((row['value'], 90))
        
        # 3. Check definition lists
        dl_lists = self.structural_analyzer.find_definition_lists(soup)
        for dl in dl_lists:
            for item in dl['items']:
                if any(keyword in item['header'] for keyword in ['アクセス', '交通', 'Access', '最寄り駅']):
                    candidates.append((item['value'], 90))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0]
        
        return "", 0
    
    def extract_phone(self, soup: BeautifulSoup) -> Tuple[str, int]:
        """Extract phone number with confidence score"""
        text_content = soup.get_text()
        candidates = []
        
        # Pattern matching
        phone_matches = self.pattern_matcher.extract_with_confidence(
            text_content,
            PatternMatcher.PHONE_PATTERNS
        )
        
        # Clean phone numbers
        for phone, conf in phone_matches:
            # Remove common non-digit characters
            cleaned = re.sub(r'[^\d\-]', '', phone)
            if cleaned and len(cleaned) >= 10:
                candidates.append((phone, conf))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0]
        
        return "", 0
    
    def extract_hours(self, soup: BeautifulSoup) -> Tuple[str, int]:
        """Extract business hours with confidence score"""
        text_content = soup.get_text()
        candidates = []
        
        # Pattern matching
        hours_matches = self.pattern_matcher.extract_with_confidence(
            text_content,
            PatternMatcher.HOURS_PATTERNS
        )
        candidates.extend(hours_matches)
        
        if candidates:
            candidates.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
            return candidates[0]
        
        return "", 0
    
    def extract_all_info(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract all store information with confidence scores"""
        
        # Extract each piece of information
        name, name_conf = self.extract_store_name(soup, url)
        address, addr_conf = self.extract_address(soup)
        access, access_conf = self.extract_access(soup)
        phone, phone_conf = self.extract_phone(soup)
        hours, hours_conf = self.extract_hours(soup)
        
        # Calculate overall confidence
        total_conf = sum([name_conf, addr_conf, access_conf]) / 3
        
        return {
            'name': name,
            'address': address,
            'access': access,
            'phone': phone,
            'hours': hours,
            'url': url,
            'confidence_scores': {
                'name': name_conf,
                'address': addr_conf,
                'access': access_conf,
                'phone': phone_conf,
                'hours': hours_conf,
                'overall': total_conf
            }
        }


class UniversalStoreScraper:
    """Universal store information scraper with backward compatibility"""
    
    def __init__(self):
        self.intelligent_extractor = IntelligentExtractor()
        
        # Legacy site-specific extractors for backward compatibility
        self.legacy_extractors = {
            'dioclinic': self._extract_dio_clinic,
            'eminal-clinic': self._extract_eminal_clinic,
            'frey-a': self._extract_freya_clinic,
            'seishin-biyou': self._extract_seishin_clinic,
            's-b-c.net': self._extract_sbc_clinic,
            'rizeclinic': self._extract_rize_clinic,
        }
    
    def extract_store_info(self, soup: BeautifulSoup, url: str, store_name: str = "") -> Dict[str, Any]:
        """Main extraction method with fallback to legacy extractors"""
        domain = urlparse(url).netloc
        
        # Check if we have a legacy extractor for this domain
        for pattern, extractor in self.legacy_extractors.items():
            if pattern in domain:
                # Use legacy extractor
                legacy_result = extractor(soup, url, store_name)
                # If legacy extractor returns good results, use them
                if legacy_result.get('name') and (legacy_result.get('address') or legacy_result.get('access')):
                    return legacy_result
        
        # Use intelligent universal extractor
        result = self.intelligent_extractor.extract_all_info(soup, url)
        
        # If store_name was provided and we didn't find a better one, use it
        if store_name and not result['name']:
            result['name'] = store_name
        
        # If confidence is too low, try to enhance with section analysis
        if result['confidence_scores']['overall'] < 70:
            sections = self.intelligent_extractor.structural_analyzer.find_info_sections(soup)
            for section in sections[:3]:  # Check top 3 sections
                section_soup = BeautifulSoup(str(section['element']), 'html.parser')
                section_result = self.intelligent_extractor.extract_all_info(section_soup, url)
                
                # Update with better results
                for field in ['name', 'address', 'access', 'phone', 'hours']:
                    if section_result['confidence_scores'][field] > result['confidence_scores'][field]:
                        result[field] = section_result[field]
                        result['confidence_scores'][field] = section_result['confidence_scores'][field]
        
        return result
    
    # Legacy extractors for backward compatibility
    def _extract_dio_clinic(self, soup: BeautifulSoup, url: str, clinic_name: str) -> Dict[str, Any]:
        """Legacy DIO clinic extractor"""
        clinic_info = {
            'name': clinic_name,
            'address': '',
            'access': '',
            'url': url
        }
        
        name_elem = soup.find('h2', class_='clinic-name')
        if name_elem:
            clinic_info['name'] = name_elem.get_text(strip=True)
        
        address_elem = soup.find('div', class_='address')
        if address_elem:
            clinic_info['address'] = address_elem.get_text(strip=True)
        
        access_elem = soup.find('div', class_='access')
        if access_elem:
            clinic_info['access'] = access_elem.get_text(strip=True)
        
        return clinic_info
    
    def _extract_eminal_clinic(self, soup: BeautifulSoup, url: str, clinic_name: str) -> Dict[str, Any]:
        """Legacy Eminal clinic extractor"""
        clinic_info = {
            'name': clinic_name,
            'address': '',
            'access': '',
            'url': url
        }
        
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
        
        return clinic_info
    
    def _extract_freya_clinic(self, soup: BeautifulSoup, url: str, clinic_name: str) -> Dict[str, Any]:
        """Legacy Freya clinic extractor"""
        clinic_info = {
            'name': clinic_name,
            'address': '',
            'access': '',
            'url': url
        }
        
        h1_elem = soup.find('h1')
        if h1_elem:
            clinic_info['name'] = h1_elem.get_text(strip=True)
        
        for tr in soup.find_all('tr'):
            th = tr.find('th')
            td = tr.find('td')
            if th and td:
                header = th.get_text(strip=True)
                if '所在地' in header:
                    clinic_info['address'] = td.get_text(strip=True)
                elif 'アクセス' in header:
                    clinic_info['access'] = td.get_text(strip=True)
        
        return clinic_info
    
    def _extract_seishin_clinic(self, soup: BeautifulSoup, url: str, clinic_name: str) -> Dict[str, Any]:
        """Legacy Seishin clinic extractor"""
        clinic_info = {
            'name': clinic_name,
            'address': '',
            'access': '',
            'url': url
        }
        
        h1_elem = soup.find('h1')
        if h1_elem:
            clinic_info['name'] = h1_elem.get_text(strip=True)
        
        text_content = soup.get_text()
        
        # Address extraction
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
        
        # Access extraction
        access_patterns = [
            r'([^\s]+駅)[^\n]*?(?:から|より)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
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
    
    def _extract_sbc_clinic(self, soup: BeautifulSoup, url: str, clinic_name: str) -> Dict[str, Any]:
        """Legacy SBC clinic extractor"""
        return self._extract_seishin_clinic(soup, url, clinic_name)  # Similar pattern
    
    def _extract_rize_clinic(self, soup: BeautifulSoup, url: str, clinic_name: str) -> Dict[str, Any]:
        """Legacy Rize clinic extractor"""
        clinic_info = {
            'name': clinic_name,
            'address': '',
            'access': '',
            'url': url
        }
        
        h1_elem = soup.find('h1')
        if h1_elem:
            clinic_info['name'] = h1_elem.get_text(strip=True)
        
        info_table = soup.find('table')
        if info_table:
            for tr in info_table.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    header = th.get_text(strip=True)
                    if '住所' in header:
                        clinic_info['address'] = td.get_text(strip=True)
        
        text_content = soup.get_text()
        station_patterns = [
            r'「([^\s]+駅)」[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
            r'([^\s]+駅)[^\n]*?(?:徒歩|歩いて)[^\n]*?(\d+)分',
        ]
        
        found_station = None
        min_minutes = 999
        
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
        
        return clinic_info


# Export the main class
__all__ = ['UniversalStoreScraper']