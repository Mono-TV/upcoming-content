# Multi-Row Content Implementation Guide

## Overview

This implementation adds 4 distinct content rows to the application:

1. **New Releases (OTT)** - Already released content on streaming platforms
2. **Upcoming OTT Releases** - Future releases on streaming platforms
3. **Movies in Theatre** - Currently playing in theatres (Bangalore)
4. **Upcoming Theatre Releases** - Future theatre releases (before Dec 31, 2025)

## Architecture

### Backend (Python Scrapers)

#### New Files Created

1. **`config.py`** - Centralized configuration
   - Multi-city support for BookMyShow
   - Platform mappings
   - Scraping settings
   - Date ranges

2. **`scrape_ott_releases.py`** - OTT Released Content Scraper
   - Scrapes already-released content from Binged
   - Extracts deeplinks from detail pages
   - Usage: `python3 scrape_ott_releases.py [--pages N] [--debug]`

3. **`scrape_theatre_current.py`** - Current Theatre Movies Scraper
   - Scrapes BookMyShow for current movies
   - Extracts: title, duration, CBFC rating, video formats, trailer
   - Usage: `python3 scrape_theatre_current.py [--city bengaluru] [--debug]`

4. **`scrape_theatre_upcoming.py`** - Upcoming Theatre Releases Scraper
   - Scrapes BookMyShow for upcoming releases
   - Filters movies releasing before Dec 31, 2025
   - Usage: `python3 scrape_theatre_upcoming.py [--city bengaluru] [--debug]`

5. **`update_all_content.py`** - Master Orchestrator
   - Runs all 4 scrapers
   - Enriches with TMDB, IMDb, YouTube data
   - Generates 4 separate output files
   - Usage: `python3 update_all_content.py [--ott-pages N] [--city bengaluru] [--debug]`

#### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. SCRAPING PHASE                                       │
├─────────────────────────────────────────────────────────┤
│ • scrape_ott_releases.py → ott_releases.json           │
│ • update_content.py → ott_upcoming.json                │
│ • scrape_theatre_current.py → theatre_current.json     │
│ • scrape_theatre_upcoming.py → theatre_upcoming.json   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. ENRICHMENT PHASE (TMDB → IMDb → YouTube)            │
├─────────────────────────────────────────────────────────┤
│ • ott_releases_enriched.json                           │
│ • movies_enriched.json (OTT upcoming)                  │
│ • theatre_current_enriched.json                        │
│ • theatre_upcoming_enriched.json                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. FRONTEND RENDERING                                   │
├─────────────────────────────────────────────────────────┤
│ • 4 separate horizontal scrolling rows                  │
│ • Platform filters (OTT only)                           │
│ • Video format badges (theatre)                         │
│ • Deeplinks (OTT released)                             │
└─────────────────────────────────────────────────────────┘
```

### Frontend

#### Modified Files

1. **`index.html`**
   - Added 4 content row sections
   - Row headers with titles and subtitles
   - Separate timeline containers

2. **`script.js`**
   - Multi-source data loading (4 JSON files)
   - Row-specific rendering
   - Theatre content support (video formats)
   - Filter system (OTT only)

3. **`styles.css`**
   - Row-based layout styles
   - Timeline container (replaces single grid)
   - Format badge styling
   - Empty row messages

## Features by Content Type

### OTT Released Content
- ✅ Deeplinks to streaming platforms
- ✅ Platform badges
- ✅ TMDB/IMDb enrichment
- ✅ YouTube trailers
- ✅ Platform filters

### OTT Upcoming Content
- ✅ Platform badges
- ✅ TMDB/IMDb enrichment
- ✅ YouTube trailers
- ✅ Platform filters
- ✅ Content type filters (Movies/Shows)

### Theatre Content (Current & Upcoming)
- ✅ Video format display (IMAX, 3D, Dolby, etc.)
- ✅ TMDB/IMDb enrichment
- ✅ BookMyShow trailer priority → YouTube fallback
- ✅ CBFC ratings
- ✅ Duration information
- ✅ Booking link (saved but not displayed)
- ❌ No platform filters (not applicable)

## Configuration

### Multi-City Support

Edit `config.py` to add/modify cities:

```python
BMS_CONFIG = {
    'default_city': 'bengaluru',
    'cities': {
        'bengaluru': {
            'name': 'Bengaluru',
            'display_name': 'Bengaluru',
            'code': 'bengaluru',
            'region': 'South India'
        },
        # Add more cities here
    }
}
```

### Date Filtering

Modify the date range for upcoming theatre releases:

```python
UPCOMING_THEATRE_DATE_RANGE = {
    'end_date': '2025-12-31',  # Change this date
}
```

### Video Format Priority

Formats are displayed in order of preference (defined in `config.py`):

```python
VIDEO_FORMAT_PRIORITY = [
    'IMAX 3D',
    'IMAX 2D',
    'DOLBY CINEMA 3D',
    '4DX 3D',
    # ... etc
]
```

## Usage Instructions

### 1. Install Dependencies

```bash
pip3 install playwright beautifulsoup4 cinemagoer requests pillow
playwright install chromium
```

### 2. Set API Keys (Optional but Recommended)

```bash
export TMDB_API_KEY="your_tmdb_api_key"
export YOUTUBE_API_KEY="your_youtube_api_key"  # Optional
```

### 3. Run Master Scraper

```bash
# Full pipeline (all 4 content types)
python3 update_all_content.py --ott-pages 5 --city bengaluru --debug

# Skip OTT content
python3 update_all_content.py --skip-ott --city bengaluru

# Skip theatre content
python3 update_all_content.py --skip-theatre --ott-pages 5

# Skip enrichment (scraping only)
python3 update_all_content.py --skip-enrichment
```

### 4. Run Individual Scrapers

```bash
# OTT releases
python3 scrape_ott_releases.py --pages 3 --debug

# Theatre current
python3 scrape_theatre_current.py --city bengaluru --debug

# Theatre upcoming
python3 scrape_theatre_upcoming.py --city bengaluru --debug
```

### 5. Serve Frontend Locally

```bash
python3 -m http.server 8000
# Visit: http://localhost:8000
```

## Testing Checklist

### Backend Testing

- [ ] Test OTT releases scraper
  ```bash
  python3 scrape_ott_releases.py --pages 1 --debug
  ```

- [ ] Test theatre current scraper
  ```bash
  python3 scrape_theatre_current.py --city bengaluru --debug
  ```

- [ ] Test theatre upcoming scraper
  ```bash
  python3 scrape_theatre_upcoming.py --city bengaluru --debug
  ```

- [ ] Test master orchestrator
  ```bash
  python3 update_all_content.py --ott-pages 2 --debug
  ```

- [ ] Verify output files exist:
  - `ott_releases_enriched.json`
  - `movies_enriched.json`
  - `theatre_current_enriched.json`
  - `theatre_upcoming_enriched.json`

### Frontend Testing

- [ ] Serve locally: `python3 -m http.server 8000`
- [ ] Verify all 4 rows display correctly
- [ ] Test OTT platform filters
- [ ] Test content type filters (Movies/Shows)
- [ ] Verify video format badges display (theatre content)
- [ ] Test trailer playback
- [ ] Verify empty rows are hidden
- [ ] Test horizontal scrolling in each row
- [ ] Test responsive layout

### Data Quality Checks

- [ ] Check deeplinks in OTT released content
- [ ] Verify video formats in theatre content
- [ ] Confirm TMDB enrichment (posters, metadata)
- [ ] Validate YouTube trailers
- [ ] Check date filtering (upcoming theatre < Dec 31, 2025)

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip3 install -r requirements.txt
   playwright install chromium
   ```

2. **Empty data files**
   - Check internet connection
   - Verify source websites are accessible
   - Run with `--debug` flag for detailed output

3. **Rate limiting**
   - Increase delays in `config.py`
   - Reduce number of pages: `--ott-pages 2`

4. **Missing API keys**
   - Set `TMDB_API_KEY` environment variable
   - Fallback mechanisms exist for most features

5. **BookMyShow scraping fails**
   - Website structure may have changed
   - Run with `--debug` to save screenshots
   - Check `debug_theatre_*.png` files

## Future Enhancements

### Potential Additions

1. **Multi-city switching** - UI toggle for different cities
2. **Format filtering** - Filter theatre movies by IMAX, 3D, etc.
3. **Deeplink buttons** - Display "Watch Now" buttons for OTT content
4. **Booking integration** - "Book Tickets" button for theatre content
5. **Date range selector** - Custom date filtering
6. **Search functionality** - Search across all content types
7. **Favorites** - Save movies to watchlist
8. **Notifications** - Alert for new releases

### Code Improvements

1. **Error recovery** - Better handling of partial failures
2. **Caching** - Cache enrichment API responses
3. **Parallel processing** - Speed up enrichment
4. **Progress indicators** - Real-time scraping progress
5. **Logging** - Structured logging with levels

## API Reference

### ContentUpdater Class

Used by `update_all_content.py` for enrichment:

```python
from update_content import ContentUpdater

updater = ContentUpdater(
    enable_posters=True,
    enable_trailers=True,
    generate_placeholders=True
)
updater.movies = items
updater.enrich_with_tmdb_complete()
updater.enrich_with_imdb_fallback()
updater.enrich_with_youtube_trailers()
```

### Configuration Constants

```python
from config import (
    BMS_CONFIG,
    BINGED_CONFIG,
    CONTENT_TYPES,
    VIDEO_FORMAT_PRIORITY
)
```

## Performance Metrics

### Expected Scraping Times

| Content Type | Pages/Items | Estimated Time |
|--------------|-------------|----------------|
| OTT Released | 5 pages | ~15-20 minutes |
| OTT Upcoming | 5 pages | ~10-15 minutes |
| Theatre Current | ~50 movies | ~20-30 minutes |
| Theatre Upcoming | ~30 movies | ~15-20 minutes |
| **Total (Full Run)** | | **~60-85 minutes** |

### Optimization Tips

1. **Reduce pages**: `--ott-pages 2` (faster testing)
2. **Skip deeplinks**: `--no-deeplinks` flag (OTT scraper)
3. **Skip enrichment**: `--skip-enrichment` (scraping only)
4. **Single content type**: Use individual scrapers
5. **Parallel execution**: Not yet implemented

## License & Credits

- **Binged.com**: OTT release data source
- **BookMyShow**: Theatre movie data source
- **TMDB**: Metadata and poster enrichment
- **IMDb (via Cinemagoer)**: Fallback metadata
- **YouTube**: Trailer sourcing

---

**Built with**: Python, Playwright, BeautifulSoup, TMDB API, Cinemagoer

**Last Updated**: 2025-11-09
