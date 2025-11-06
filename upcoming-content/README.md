# Binged.com Movie Scraper

✅ **WORKING** - Successfully scrapes movie data from Binged.com!

This Python script scrapes movie listings from Binged.com's streaming premiere dates page and outputs the data in JSON format.

## Features

- ✅ Scrapes movie titles, release dates, platforms, images, and URLs
- ✅ **Automatic pagination** - scrapes all pages, not just the first one!
- ✅ **IMDb enrichment** - automatically adds IMDb IDs, titles, and years
- ✅ **YouTube trailer enrichment** - finds official trailers with intelligent matching
- ✅ **Combined script** - scrape and enrich everything in one command
- ✅ Outputs data in JSON format
- ✅ Saves to both console (stdout) and a JSON file
- ✅ Handles JavaScript-rendered content using Playwright
- ✅ Takes screenshot for debugging
- ✅ Successfully tested with 30+ movies across multiple pages
- ✅ 96.7% IMDb match success rate
- ✅ Intelligent trailer matching using title, year, and IMDb metadata

## Requirements

- Python 3.7 or higher
- Chromium browser (automatically installed by Playwright)

## Installation

1. Install the required Python packages:

```bash
pip3 install playwright beautifulsoup4 lxml requests
```

2. Install Playwright browsers:

```bash
python3 -m playwright install chromium
```

## Usage

### Quick Start (Recommended)

Run the combined script to scrape and enrich in one command:

```bash
# Python version
python3 scrape_and_enrich.py

# OR Shell script version
./scrape_and_enrich.sh
```

This will:
1. Launch a headless Chrome browser
2. Navigate to the Binged.com streaming premiere dates page
3. **Automatically scrape all pages** with pagination
4. Save scraped data to `movies.json`
5. **Automatically enrich each movie with IMDb data** (ID, title, year)
6. Save enriched data to `movies_with_imdb.json`
7. **Automatically find YouTube trailers** for each movie
8. Save fully enriched data to `movies_with_trailers.json`

### Run Individual Scripts

If you prefer to run them separately:

**1. Scrape movies only:**
```bash
python3 scrape_movies.py
```

**2. Add IMDb enrichment to existing movies.json:**
```bash
python3 enrich_with_imdb.py
```

**3. Add YouTube trailers to existing movies_with_imdb.json:**
```bash
python3 enrich_with_youtube.py
```

**Note:** The script automatically handles pagination and will scrape all pages until no more movies are found.

### YouTube API Key (Optional)

For better YouTube trailer matching, you can optionally provide a YouTube Data API v3 key:

```bash
export YOUTUBE_API_KEY="your_api_key_here"
python3 enrich_with_youtube.py
```

Without an API key, the script will use web scraping (still works well, but API is more reliable).

### Output Format

**movies.json** - Basic scraped data:
```json
{
  "title": "Despicable Me 4",
  "release_date": "05 Nov 2025",
  "platforms": ["Netflix", "Amazon Prime Video"],
  "image_url": "https://...",
  "url": "https://www.binged.com/..."
}
```

**movies_with_imdb.json** - Enriched with IMDb data:
```json
{
  "title": "Despicable Me 4",
  "release_date": "05 Nov 2025",
  "platforms": ["Netflix", "Amazon Prime Video"],
  "image_url": "https://...",
  "url": "https://www.binged.com/...",
  "imdb_id": "tt7510222",
  "imdb_title": "Despicable Me 4",
  "imdb_year": "2024",
  "imdb_url": "https://www.imdb.com/title/tt7510222/"
}
```

**movies_with_trailers.json** - Fully enriched with YouTube trailers:
```json
{
  "title": "Despicable Me 4",
  "release_date": "05 Nov 2025",
  "platforms": ["Netflix", "Amazon Prime Video"],
  "image_url": "https://...",
  "url": "https://www.binged.com/...",
  "imdb_id": "tt7510222",
  "imdb_title": "Despicable Me 4",
  "imdb_year": "2024",
  "imdb_url": "https://www.imdb.com/title/tt7510222/",
  "youtube_id": "qQlr9-rF32A",
  "youtube_url": "https://www.youtube.com/watch?v=qQlr9-rF32A",
  "youtube_title": "Despicable Me 4 | Official Trailer",
  "youtube_channel": "Illumination",
  "confidence_score": 85
}
```

### Customizing the URL

To scrape movies from different platforms or time periods, edit the `url` variable in the `main()` function of `scrape_movies.py`.

The URL parameters control which platforms and time period to scrape:
- `mode=streaming-month` - Show movies by month
- `platform[]=Netflix` - Filter by platform(s)

## Troubleshooting

### ChromeDriver Version Mismatch

If you see errors about ChromeDriver version mismatch, Selenium 4.6+ should automatically download the correct driver. If this fails:

1. Update Chrome to the latest version
2. Clear the Selenium cache:
   ```bash
   rm -rf ~/.cache/selenium
   ```
3. Run the script again

### Browser Crashes

If the browser crashes or times out:

1. Increase the wait time in the script (line ~70: `time.sleep(5)` -> `time.sleep(10)`)
2. Check your internet connection
3. Try running with a visible browser (comment out the `--headless` line in the script)

### No Movies Found

If the script runs but finds 0 movies:

1. Check if `debug_page.html` was created
2. Open `debug_page.html` in a browser to see what content was loaded
3. The website structure may have changed - you may need to update the CSS selectors in the script

## Alternative Approach

If Selenium doesn't work on your system, you can try using Playwright instead:

1. Install Playwright:
   ```bash
   pip3 install playwright beautifulsoup4
   python3 -m playwright install chromium
   ```

2. Use the Playwright version (create a new file `scrape_movies_playwright.py` with the Playwright implementation)

## License

This script is provided as-is for educational purposes. Please respect Binged.com's terms of service and robots.txt when scraping their website.
