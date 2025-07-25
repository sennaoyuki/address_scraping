# Universal Store Information Scraper Guide

## Overview

The Universal Store Information Scraper is an intelligent web scraping system that can automatically extract store information from ANY website without requiring site-specific code. It uses advanced pattern matching, structural analysis, and heuristic algorithms to identify and extract store data.

## Key Features

### 1. Intelligent Information Extraction
- **Store Name Detection**: Automatically identifies store names from titles, headers, and structured data
- **Address Extraction**: Recognizes Japanese addresses with postal codes, prefectures, cities, and building information
- **Access Information**: Extracts station names and walking times using pattern recognition
- **Phone Numbers**: Detects various phone number formats
- **Business Hours**: Identifies operating hours in multiple formats

### 2. Multi-Layer Extraction Strategy
- **Pattern Matching**: Uses regex patterns with confidence scoring
- **Structural Analysis**: Analyzes HTML tables, definition lists, and semantic containers
- **JSON-LD Support**: Extracts data from structured data markup
- **Heuristic Detection**: Identifies information sections based on keywords and context

### 3. Backward Compatibility
- Maintains support for previously hardcoded sites (DIO, Eminal, Freya, etc.)
- Falls back to legacy extractors when available for optimal accuracy
- Seamlessly switches between universal and site-specific extraction

## Architecture

### Core Components

#### 1. PatternMatcher Class
Handles regex-based pattern matching with confidence scoring:
- Address patterns (postal codes, full addresses, buildings)
- Access patterns (stations, walking times)
- Phone patterns (various formats)
- Business hours patterns

#### 2. StructuralAnalyzer Class
Analyzes HTML structure to find information:
- Information tables (table/tr/td structures)
- Definition lists (dl/dt/dd structures)
- Information sections (divs/sections with relevant keywords)

#### 3. IntelligentExtractor Class
Main extraction engine that combines multiple strategies:
- Extracts each type of information with confidence scores
- Aggregates results from multiple sources
- Handles edge cases and data cleaning

#### 4. UniversalStoreScraper Class
Top-level interface that:
- Manages legacy extractors for backward compatibility
- Calls the intelligent extractor for new sites
- Provides a unified API for all extraction needs

## How It Works

### 1. Store Name Extraction Process
```
1. Check <title> tag for store keywords
2. Analyze <h1> tags (highest priority)
3. Check <h2> tags with store keywords
4. Look for og:site_name meta tag
5. Parse JSON-LD structured data
6. Return highest confidence match
```

### 2. Address Extraction Process
```
1. Apply regex patterns to full page text
2. Check information tables for address fields
3. Analyze definition lists for address data
4. Parse JSON-LD address objects
5. Clean and normalize results
6. Return highest confidence match
```

### 3. Access Information Extraction
```
1. Find station names with walking times
2. Identify station-only mentions
3. Extract line and station combinations
4. Process structured data
5. Format as "XX駅から徒歩約Y分"
```

### 4. Confidence Scoring
Each extraction has a confidence score (0-100):
- 90-100: Very high confidence (structured data, perfect pattern match)
- 70-89: High confidence (good pattern match, table data)
- 50-69: Medium confidence (partial match, context clues)
- Below 50: Low confidence (weak indicators)

## Usage Examples

### Basic Usage
```python
from universal_scraper import UniversalStoreScraper
from bs4 import BeautifulSoup

# Initialize scraper
scraper = UniversalStoreScraper()

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Extract information
result = scraper.extract_store_info(soup, url)

# Access results
print(f"Store Name: {result['name']}")
print(f"Address: {result['address']}")
print(f"Access: {result['access']}")
print(f"Phone: {result.get('phone', '')}")
print(f"Hours: {result.get('hours', '')}")
```

### With Confidence Scores
```python
# Get confidence scores
if 'confidence_scores' in result:
    print(f"Name confidence: {result['confidence_scores']['name']}%")
    print(f"Overall confidence: {result['confidence_scores']['overall']}%")
```

## Supported Patterns

### Address Patterns
- `〒123-4567 東京都渋谷区...` (with postal code)
- `大阪府大阪市北区梅田1-2-3` (full address)
- `〇〇ビル 5階` (building and floor)

### Access Patterns
- `「新宿駅」から徒歩5分`
- `渋谷駅徒歩約3分`
- `最寄り駅：品川駅`
- `JR山手線 東京駅`

### Phone Patterns
- `TEL: 03-1234-5678`
- `電話：0120-123-456`
- `☎ 03-1234-5678`

### Business Hours Patterns
- `営業時間：10:00～19:00`
- `平日 9:00-18:00`
- `受付時間：月〜金 10:00〜20:00`

## Extending the Scraper

### Adding New Patterns
To add support for new patterns, update the pattern lists in `PatternMatcher`:

```python
# Add to ADDRESS_PATTERNS
(r'your_regex_pattern', confidence_score),

# Add to ACCESS_PATTERNS
(r'your_station_pattern', confidence_score),
```

### Adding Site-Specific Extractors
For sites that need special handling, add to `legacy_extractors`:

```python
self.legacy_extractors = {
    'domain.com': self._extract_special_site,
    # ...
}
```

## Best Practices

1. **URL Quality**: Provide direct store page URLs for best results
2. **Confidence Thresholds**: Consider confidence scores when using extracted data
3. **Fallback Handling**: Have fallback logic for low-confidence extractions
4. **Testing**: Test with various sites to understand extraction patterns

## Troubleshooting

### Low Confidence Scores
- Check if the page has clear store information
- Verify the page is fully loaded (no JavaScript rendering issues)
- Consider if the site needs a custom extractor

### Missing Information
- Some sites may not have all information types
- Check confidence scores to understand extraction quality
- Review the page structure for unusual patterns

### Performance Optimization
- The scraper analyzes the full page for maximum accuracy
- For large-scale scraping, consider caching results
- Use appropriate delays between requests

## Future Enhancements

1. **Machine Learning Integration**: Train models on extracted patterns
2. **Multi-language Support**: Extend beyond Japanese addresses
3. **Image OCR**: Extract information from images
4. **JavaScript Rendering**: Support for dynamic content
5. **API Integration**: Direct integration with geocoding APIs

## Conclusion

The Universal Store Information Scraper provides a robust, extensible solution for extracting store information from any website. Its intelligent pattern matching and structural analysis ensure high accuracy while maintaining flexibility for new sites and formats.