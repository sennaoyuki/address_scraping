# Beauty Skin Clinic Image Pattern Analysis

## Overview
This document identifies the specific patterns for extracting actual clinic store images from https://beautyskinclinic.jp/clinic/, excluding non-clinic images like icons, logos, or decorative elements.

## Identified Patterns for Clinic Store Images

### 1. URL Pattern
All actual clinic store images follow these patterns:
- Domain: `https://beautyskinclinic.jp/`
- Path: `/wp/wp-content/uploads/`
- Filename patterns:
  - `top_sp10_XX.webp` (e.g., top_sp10_03.webp, top_sp10_04.webp)
  - `top_sp12_XX.webp` (e.g., top_sp12_01.webp)
  - Where XX is a numeric identifier

### 2. HTML Structure Pattern
```html
<img 
    src="https://beautyskinclinic.jp/wp/wp-content/uploads/[filename].webp" 
    alt="ビューティースキンクリニック [院名]"
>
```

### 3. Key Identifiers
- **Alt text pattern**: Always contains "ビューティースキンクリニック" followed by the clinic name (e.g., "新宿院", "渋谷院", "池袋院")
- **File extension**: Always `.webp`
- **Image context**: Always appears within a clinic information section, accompanied by:
  - Clinic name (h3 or similar heading)
  - Address information
  - Phone number
  - Google Maps link

### 4. Exclusion Patterns
Images to exclude:
- Logo images (typically in header/footer)
- Icon images (small decorative elements)
- Banner images (promotional content)
- Images without the "ビューティースキンクリニック" alt text pattern

## Verified Clinic Images
Based on the analysis, here are the confirmed clinic store images:

1. **新宿院 (Shinjuku)**
   - URL: `https://beautyskinclinic.jp/wp/wp-content/uploads/top_sp10_03.webp`
   - Alt: `ビューティースキンクリニック 新宿院`

2. **渋谷院 (Shibuya)**
   - URL: `https://beautyskinclinic.jp/wp/wp-content/uploads/top_sp10_04.webp`
   - Alt: `ビューティースキンクリニック 渋谷院`

3. **池袋院 (Ikebukuro)**
   - URL: `https://beautyskinclinic.jp/wp/wp-content/uploads/top_sp12_01.webp`
   - Alt: `ビューティースキンクリニック 池袋院`

## Scraping Strategy Recommendations

### 1. CSS Selector Approach
```css
img[alt*="ビューティースキンクリニック"][alt*="院"]
```

### 2. XPath Approach
```xpath
//img[contains(@alt, 'ビューティースキンクリニック') and contains(@alt, '院')]
```

### 3. URL Pattern Matching
```regex
https://beautyskinclinic\.jp/wp/wp-content/uploads/top_sp\d+_\d+\.webp
```

### 4. Validation Criteria
To ensure only actual clinic images are captured:
1. Check if alt attribute contains "ビューティースキンクリニック" AND "院"
2. Verify image URL matches the pattern above
3. Confirm image is not in header/footer sections
4. Validate image dimensions (clinic photos are typically larger, full-width images)

## Implementation Notes
- The website uses WebP format for images (modern, efficient format)
- Images are hosted on the same domain (no CDN)
- Each clinic has exactly one main store image on the listing page
- The naming convention (top_spXX_YY) appears to be consistent across all clinic images