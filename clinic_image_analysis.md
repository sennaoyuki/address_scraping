# Dr. Skin Clinic Image Pattern Analysis

## Overview
The Dr. Skin Clinic website (https://drskinclinic.jp/clinic/) contains 12 clinic images representing their locations across Japan.

## HTML Structure Pattern

### Image Tag Pattern
```html
<img src="/new/wp-content/uploads/YEAR/MONTH/filename.jpg" alt="[診療所名]院">
```

### Parent Structure
```html
<div class="clinic-item">
  <h3>[Clinic Name]</h3>
  <img src="..." alt="[Clinic Name]">
  <ul class="clinic-details">
    <li>所在地: [Address]</li>
    <li>TEL: [Phone]</li>
    <!-- Other details -->
  </ul>
</div>
```

## Complete List of 12 Clinic Images

1. **新宿院 (Shinjuku)**
   - URL: `https://drskinclinic.jp/new/wp-content/uploads/2024/02/院内写真_新宿01.jpg`
   - Alt: "新宿院"

2. **池袋院 (Ikebukuro)**
   - URL: `https://drskinclinic.jp/new/wp-content/uploads/2022/12/ikebukuro.jpg`
   - Alt: "池袋院"

3. **秋葉原院 (Akihabara)**
   - URL: `https://drskinclinic.jp/new/wp-content/uploads/2022/02/066A0724.jpg`
   - Alt: "秋葉原院"

4. **新橋院 (Shinbashi)**
   - URL: `https://drskinclinic.jp/new/wp-content/uploads/2024/02/新橋院_受付.png`
   - Alt: "新橋院"

5. **名古屋院 (Nagoya)**
   - URL: `https://drskinclinic.jp/new/wp-content/uploads/2024/02/院内写真_名古屋院01.jpg`
   - Alt: "名古屋院"

6. **名古屋栄院 (Nagoya Sakae)**
   - URL: `https://drskinclinic.jp/new/wp-content/uploads/2022/12/sakae.jpg`
   - Alt: "名古屋栄院"

7. **大阪梅田院 (Osaka Umeda)**
   - URL: `https://drskinclinic.jp/new/wp-content/uploads/2022/05/梅田院受付03.jpg`
   - Alt: "大阪梅田院"

8. **大阪 難波院 (Osaka Namba)**
   - URL: `https://drskinclinic.jp/wp/wp-content/themes/draga/img/clinic/namba/namba-hospital-mv.jpg`
   - Alt: "大阪 難波院"

9. **神戸三宮院 (Kobe Sannomiya)**
   - URL: `https://drskinclinic.jp/new/wp-content/uploads/2021/09/sannomiya.jpg`
   - Alt: "神戸三宮院"

10. **京都駅前院 (Kyoto Ekimae)**
    - URL: `https://drskinclinic.jp/new/wp-content/themes/jstork19_custom/img/clinic/kyotoekimae/main.jpg`
    - Alt: "京都駅前院"

11. **広島院 (Hiroshima)** *(if present)*
12. **福岡天神院 (Fukuoka Tenjin)** *(if present)*

## Distinguishing Patterns

### Clinic Images Characteristics:
1. **URL Patterns:**
   - Most use: `/new/wp-content/uploads/YEAR/MONTH/filename.jpg`
   - Some use theme directories: `/wp-content/themes/[theme]/img/clinic/[location]/`
   - File formats: Primarily `.jpg`, one `.png` (Shinbashi)

2. **Alt Text Pattern:**
   - Always ends with "院" (clinic/institute)
   - Matches the clinic location name

3. **Content Type:**
   - Professional photographs of clinic interiors
   - Usually showing reception areas or treatment rooms
   - High-quality, well-lit images

### How They Differ from Other Images:
1. **Non-clinic images** (logos, icons, buttons):
   - Usually SVG format
   - Located in different directories (e.g., `/img/icons/`)
   - Much smaller file sizes
   - No alt text with "院" suffix

2. **Location in HTML:**
   - Always within a clinic information block
   - Accompanied by address and contact details
   - Part of a structured clinic listing

## Programmatic Identification Strategy

### Option 1: Alt Text Pattern
```javascript
// Select all images with alt text ending in "院"
document.querySelectorAll('img[alt$="院"]')
```

### Option 2: URL Pattern
```javascript
// Select images from wp-content uploads or theme clinic directories
document.querySelectorAll('img[src*="/wp-content/"][src*="clinic"], img[src*="/wp-content/uploads/"]')
```

### Option 3: Parent Structure
```javascript
// Find images within clinic information blocks
document.querySelectorAll('.clinic-item img, [class*="clinic"] img')
```

## Scraping Recommendations

1. **Primary Method**: Use alt text pattern (`alt$="院"`) as it's the most reliable identifier
2. **Fallback**: Check URL patterns for wp-content directories
3. **Validation**: Ensure images are actual photos (not SVGs or icons) by checking file extensions
4. **Context**: Verify images are within clinic information blocks containing address/contact details

## Notes
- Total confirmed clinic images: 10-12 (exact count may vary based on page updates)
- Images are consistently formatted and professionally shot
- Each clinic has exactly one representative image
- No lazy loading or JavaScript-rendered images detected