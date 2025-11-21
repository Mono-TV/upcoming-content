# Binged.com Scraping Analysis

## Overview

This document analyzes the scraping URLs and data structure used to extract upcoming streaming content from Binged.com.

## Base URL Structure

### Main URL
```
https://www.binged.com/streaming-premiere-dates/
```

### Default Scraping URL (with filters)
```
https://www.binged.com/streaming-premiere-dates/
?mode=streaming-soon-month
&platform[]=Aha%20Video
&platform[]=Amazon
&platform[]=Apple%20Tv%20Plus
&platform[]=Jio%20Hotstar
&platform[]=Manorama%20MAX
&platform[]=Netflix
&platform[]=Sony%20LIV
&platform[]=Sun%20NXT
&platform[]=Zee5
```

## URL Parameters

### `mode` Parameter
- **Values:**
  - `streaming-soon-month` - Content premiering this month
  - `streaming-soon-week` - Content premiering this week
  - `streaming-soon-day` - Content premiering today
  - (Other modes may exist)

### `platform[]` Parameter
Multiple platform filters can be applied. Available platforms:
- `Aha%20Video` (URL encoded: `Aha Video`)
- `Amazon` (Amazon Prime Video)
- `Apple%20Tv%20Plus` (Apple TV+)
- `Jio%20Hotstar` (Disney+ Hotstar)
- `Manorama%20MAX`
- `Netflix`
- `Sony%20LIV`
- `Sun%20NXT`
- `Zee5`

**Note:** Multiple `platform[]` parameters can be added to filter by multiple platforms.

## Data Structure

### Scraped Movie/Show Item
Each item contains:

```json
{
  "title": "Movie/Show Title",
  "url": "https://www.binged.com/movies/movie-slug",
  "release_date": "January 15, 2024",
  "platforms": [
    "Netflix",
    "Amazon Prime Video"
  ]
}
```

### Field Details

#### `title` (string, required)
- Extracted from: `.bng-movies-table-item-title a`
- May contain separators like "Title | Subtitle" - only first part is extracted
- Whitespace is normalized

#### `url` (string, optional)
- Extracted from: `.bng-movies-table-item-title a[href]`
- Can be relative (`/movies/...`) or absolute
- Automatically converted to absolute URL if relative

#### `release_date` (string, optional)
- Extracted from: `.bng-movies-table-date span`
- Format varies (e.g., "January 15, 2024", "Jan 15", etc.)
- Stored as-is from source

#### `platforms` (array, optional)
- Extracted from: `.bng-movies-table-platform .streaming-item-platform img[src]`
- Platform IDs are extracted from image URLs (e.g., `/30.webp` = Netflix)
- Mapped to human-readable names using platform mapping

## Platform ID Mapping

Platform IDs are extracted from image filenames in the format: `/{id}.webp` or `/{id}.png`

| ID | Platform Name |
|----|---------------|
| 4  | Amazon Prime Video |
| 5  | Apple TV+ |
| 6  | Sun NXT |
| 8  | Zee5 |
| 10 | Jio Hotstar |
| 21 | Manorama MAX |
| 30 | Netflix |
| 53 | Sony LIV |
| 55 | Aha Video |
| 71 | ALT Balaji |
| 72 | Discovery Plus |
| 73 | ErosNow |
| 74 | Hoichoi |

## HTML Structure

### Main Container
```html
<div class="bng-movies-table-item">
  <!-- Movie/Show content -->
</div>
```

### Title Section
```html
<div class="bng-movies-table-item-title">
  <a href="/movies/movie-slug">Movie Title</a>
</div>
```

### Date Section
```html
<div class="bng-movies-table-date">
  <span>January 15, 2024</span>
</div>
```

### Platform Section
```html
<div class="bng-movies-table-platform">
  <div class="streaming-item-platform">
    <img src="/30.webp" />  <!-- Netflix -->
    <img src="/4.webp" />   <!-- Amazon Prime -->
  </div>
</div>
```

### Items to Exclude
- Headers: `.bng-movies-table-item-th`
- Loaders: `.bng-movies-table-item-preloader`

## Pagination

### Next Button Selector
```css
.bng-movies-table-pagination span:has-text("Next")
```

### Pagination Flow
1. Click "Next" button
2. Wait for `domcontentloaded` state
3. Wait additional 2-4 seconds for content to render
4. Scrape new page content
5. Repeat until no more pages or max pages reached

## Scraping Strategy

### 1. Initial Page Load
- Navigate to URL
- Wait for `.bng-movies-table-item` selector (15s timeout)
- Additional 3s delay for JavaScript rendering

### 2. Content Extraction
- Parse HTML with BeautifulSoup
- Filter out headers and loaders
- Extract data from each valid item

### 3. Pagination
- Find "Next" button
- Click and wait for page load
- Extract content from new page
- Continue until no more pages

### 4. Anti-Detection Measures
- Custom user agent
- Hide `navigator.webdriver` property
- Realistic viewport size (1920x1080)
- Delays between actions

## Example Usage

### Basic Scraping
```python
from scrape_binged import BingedScraper

scraper = BingedScraper(max_pages=5)
movies = await scraper.scrape()
scraper.save_to_json(movies, 'output.json')
```

### Custom URL
```python
custom_url = "https://www.binged.com/streaming-premiere-dates/?mode=streaming-soon-week"
movies = await scraper.scrape(custom_url)
```

### Command Line
```bash
# Scrape 5 pages (default)
python3 scrape_binged.py

# Scrape 10 pages
python3 scrape_binged.py --pages 10

# Custom output file
python3 scrape_binged.py --output my_data.json

# Test mode (1 page only)
python3 scrape_binged.py --test
```

## Output Format

The scraper outputs a JSON array:

```json
[
  {
    "title": "Movie Title 1",
    "url": "https://www.binged.com/movies/movie-1",
    "release_date": "January 15, 2024",
    "platforms": ["Netflix", "Amazon Prime Video"]
  },
  {
    "title": "Movie Title 2",
    "url": "https://www.binged.com/movies/movie-2",
    "release_date": "January 20, 2024",
    "platforms": ["Disney+ Hotstar"]
  }
]
```

## Notes

1. **Rate Limiting**: The scraper includes delays to avoid overwhelming the server
2. **Error Handling**: Continues scraping even if individual pages fail
3. **Data Validation**: Only items with valid titles are included
4. **URL Normalization**: Relative URLs are converted to absolute
5. **Platform Deduplication**: Same platform won't appear twice for one item

## Potential Issues

1. **Website Changes**: HTML structure may change, breaking selectors
2. **Rate Limiting**: Too many requests may trigger anti-scraping measures
3. **JavaScript Rendering**: Some content may require JavaScript execution
4. **Pagination**: Next button selector may change
5. **Platform IDs**: New platforms may not be in the mapping

## Future Enhancements

1. Support for additional URL parameters (genre, language, etc.)
2. Dynamic platform ID detection
3. More robust error recovery
4. Parallel page scraping (with rate limiting)
5. Support for different time modes (week, day, etc.)

