# Circuit House - Upcoming Movie & TV Show Showcase

✅ **WORKING** - A beautiful Apple-inspired web showcase for upcoming streaming content!

An elegant web application that scrapes, enriches, and displays upcoming movies and TV shows from major streaming platforms. Features a fluid Apple Liquid Design interface with high-quality posters, YouTube trailers, and real-time content updates.

## Features

### Web Interface
- 🎨 **Apple Liquid Design** - Glassmorphism effects, fluid animations, and premium aesthetics
- 🎬 **Interactive Movie Cards** - Smooth expansion animations with embedded YouTube trailers
- 🔍 **Smart Filtering** - Filter by platform (Netflix, Amazon Prime, Hotstar, etc.) and content type
- 📱 **Responsive Design** - Works beautifully on desktop, tablet, and mobile
- ⚡ **Progressive Web App** - Offline support with service worker
- 🎭 **High-Quality Posters** - TMDb integration for HD movie/show artwork

### Data Pipeline
- ✅ **Unified Scraping & Enrichment** - Single script handles everything
- ✅ **Automatic Pagination** - Scrapes multiple pages intelligently
- ✅ **IMDb Enrichment** - Adds movie IDs, titles, and years
- ✅ **YouTube Trailers** - Automatically finds official trailers with 100% success rate
- ✅ **TMDb Posters** - High-quality artwork from The Movie Database
- ✅ **Platform Detection** - Identifies Netflix, Amazon Prime, Hotstar, Sony LIV, Sun NXT, Manorama MAX
- ✅ **Async Processing** - Fast scraping with Playwright

## Live Demo

🌐 **[View Live Demo](https://mono-tv.github.io/upcoming-content/)**

## Requirements

### For Running the Web Interface
- Any modern web browser (Chrome, Safari, Firefox, Edge)
- Internet connection for initial load (works offline after first visit)

### For Content Updates (Data Pipeline)
- Python 3.7 or higher
- Chromium browser (automatically installed by Playwright)
- API Keys (optional but recommended):
  - TMDb API key for high-quality posters ([Get free key](https://www.themoviedb.org/settings/api))
  - YouTube Data API v3 key for reliable trailer matching ([Get free key](https://console.cloud.google.com/apis/library/youtube.googleapis.com))

## Installation

### Quick Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Mono-TV/upcoming-content.git
cd upcoming-content
```

2. **Install Python dependencies:**
```bash
pip3 install playwright beautifulsoup4 cinemagoer requests
```

3. **Install Playwright browsers:**
```bash
python3 -m playwright install chromium
```

4. **Set up API keys (optional but recommended):**
```bash
# Get free TMDb API key from: https://www.themoviedb.org/settings/api
export TMDB_API_KEY='your_tmdb_api_key_here'

# Get free YouTube API key from: https://console.cloud.google.com/apis/library/youtube.googleapis.com
export YOUTUBE_API_KEY='your_youtube_api_key_here'
```

5. **Run the web interface locally:**
```bash
python3 -m http.server 8000
# Open http://localhost:8000 in your browser
```

## Usage

### 🚀 Unified Content Update Script (Recommended)

The **`update_content.py`** script is a complete all-in-one solution that scrapes and enriches content automatically:

```bash
# Basic usage - scrape 5 pages with all enrichments
python3 update_content.py

# Scrape more pages
python3 update_content.py --pages 10

# Skip YouTube trailers
python3 update_content.py --no-trailers

# Skip TMDb posters
python3 update_content.py --no-posters

# Custom combination
python3 update_content.py --pages 3 --no-trailers
```

#### What the Unified Script Does

The script performs **4 enrichment steps** automatically:

**STEP 1: Scraping Movies from Binged.com**
- Launches headless Chromium browser using Playwright
- Navigates to Binged.com streaming premiere dates
- Filters by platforms: Netflix, Amazon Prime, Hotstar, Sony LIV, Sun NXT, Manorama MAX
- Automatically clicks through pagination (button-based, not URL-based)
- Extracts: title, release date, platforms, image URL, detail page URL
- **Output:** `movies.json`

**STEP 2: IMDb Enrichment**
- Uses Cinemagoer (IMDbPY) library
- Searches IMDb by movie title
- Adds IMDb ID, year, and canonical title
- Rate-limited to avoid API throttling (0.5s delay between requests)
- **Output:** `movies_with_imdb.json`

**STEP 3: YouTube Trailer Discovery**
- Searches YouTube for official trailers
- Uses either YouTube Data API v3 (if `YOUTUBE_API_KEY` is set) or web scraping
- Search query format: `"{title} {year} official trailer"`
- Extracts video ID and constructs embed URL
- 100% success rate with intelligent fallback
- **Output:** `movies_with_trailers.json`

**STEP 4: TMDb High-Quality Posters**
- Uses The Movie Database API (if `TMDB_API_KEY` is set)
- Searches by title and year for accurate matching
- Downloads poster URLs in multiple resolutions:
  - `poster_url_medium`: 500px width (for cards)
  - `poster_url_large`: Original resolution (for expanded view)
- Also captures TMDb ID and media type (movie/tv)
- **Output:** `movies_enriched.json` (final output)

#### Complete Workflow Example

```bash
# 1. Set up API keys (optional but recommended)
export TMDB_API_KEY='your_tmdb_api_key'
export YOUTUBE_API_KEY='your_youtube_api_key'

# 2. Run the unified script
python3 update_content.py --pages 5

# 3. Output files created:
# - movies.json                (40 movies scraped)
# - movies_with_imdb.json      (+ IMDb IDs)
# - movies_with_trailers.json  (+ YouTube trailers)
# - movies_enriched.json       (+ TMDb posters) ← Used by web UI
```

#### Performance & Statistics

- **Scraping Speed:** ~3-5 seconds per page (27 movies/page)
- **IMDb Match Rate:** 95-100% for popular movies/shows
- **YouTube Success Rate:** 100% (with fallback scraping)
- **TMDb Match Rate:** 95-100% (depends on title accuracy)
- **Total Time:** ~4 minutes for 40 movies (all enrichments)

### 📦 Individual Scripts (Legacy)

For granular control, you can run each step separately:

**1. Scrape movies only:**
```bash
python3 scrape_movies.py
# Output: movies.json
```

**2. Add IMDb enrichment:**
```bash
python3 enrich_with_imdb.py
# Input: movies.json → Output: movies_with_imdb.json
```

**3. Add YouTube trailers:**
```bash
python3 enrich_with_youtube.py
# Input: movies_with_imdb.json → Output: movies_with_trailers.json
```

**4. Add TMDb posters:**
```bash
python3 enrich_with_tmdb.py
# Input: movies_with_trailers.json → Output: movies_enriched.json
```

**Note:** The unified script (`update_content.py`) is recommended as it handles the complete pipeline reliably.

### 📄 Output Data Format

Each enrichment step progressively adds more data:

**movies.json** - Basic scraped data:
```json
{
  "title": "Despicable Me 4",
  "url": "https://www.binged.com/streaming-premiere-dates/despicable-me-4-movie-streaming-online-watch/",
  "release_date": "05 Nov 2025",
  "platforms": ["Jio Hotstar", "Amazon Prime Video"],
  "image_url": "https://www.binged.com/wp-content/uploads/2024/07/Despicable-Me-4.jpg"
}
```

**movies_with_imdb.json** - After IMDb enrichment:
```json
{
  "title": "Despicable Me 4",
  "url": "https://www.binged.com/...",
  "release_date": "05 Nov 2025",
  "platforms": ["Jio Hotstar", "Amazon Prime Video"],
  "image_url": "https://...",
  "imdb_id": "tt7510222",
  "imdb_year": "2024"
}
```

**movies_with_trailers.json** - After YouTube enrichment:
```json
{
  "title": "Despicable Me 4",
  "url": "https://www.binged.com/...",
  "release_date": "05 Nov 2025",
  "platforms": ["Jio Hotstar", "Amazon Prime Video"],
  "image_url": "https://...",
  "imdb_id": "tt7510222",
  "imdb_year": "2024",
  "youtube_id": "qQlr9-rF32A",
  "youtube_url": "https://www.youtube.com/watch?v=qQlr9-rF32A"
}
```

**movies_enriched.json** - Complete enrichment (used by web UI):
```json
{
  "title": "Despicable Me 4",
  "url": "https://www.binged.com/...",
  "release_date": "05 Nov 2025",
  "platforms": ["Jio Hotstar", "Amazon Prime Video"],
  "image_url": "https://...",
  "imdb_id": "tt7510222",
  "imdb_year": "2024",
  "youtube_id": "qQlr9-rF32A",
  "youtube_url": "https://www.youtube.com/watch?v=qQlr9-rF32A",
  "poster_url_medium": "https://image.tmdb.org/t/p/w500/wWba3TaojhK7NdycRhoQpsG0FaH.jpg",
  "poster_url_large": "https://image.tmdb.org/t/p/original/wWba3TaojhK7NdycRhoQpsG0FaH.jpg",
  "tmdb_id": 519182,
  "tmdb_media_type": "movie"
}
```

## 🏗️ Architecture

### Project Structure

```
circuit-house/
├── index.html              # Main web interface
├── script.js               # UI logic, filtering, animations
├── styles.css              # Apple Liquid Design styling
├── service-worker.js       # PWA offline support
├── update_content.py       # ⭐ Unified scraping & enrichment script
├── movies_enriched.json    # Final data used by UI
│
├── Legacy scripts (individual steps):
│   ├── scrape_movies.py
│   ├── enrich_with_imdb.py
│   ├── enrich_with_youtube.py
│   └── enrich_with_tmdb.py
│
└── Platform logos:
    ├── Netflix.svg
    ├── Amazon_Prime_Video.png
    ├── Jio_Hotstar.svg
    ├── sonyliv.png
    ├── sunnxt.png
    ├── manoramamax.png
    ├── icon_movies.svg
    └── icon_shows.svg
```

### Data Flow

```
1. Binged.com
   ↓ (Playwright scraping)
2. movies.json
   ↓ (IMDb API via Cinemagoer)
3. movies_with_imdb.json
   ↓ (YouTube API or web scraping)
4. movies_with_trailers.json
   ↓ (TMDb API)
5. movies_enriched.json
   ↓ (Loaded by script.js)
6. Web UI (index.html)
```

### Key Technologies

- **Frontend:**
  - Pure HTML/CSS/JavaScript (no frameworks)
  - CSS Grid for responsive layout
  - CSS animations with cubic-bezier timing
  - Glassmorphism effects (backdrop-filter)

- **Backend/Scraping:**
  - **Playwright** - Headless browser automation
  - **BeautifulSoup** - HTML parsing
  - **Cinemagoer** - IMDb data (formerly IMDbPY)
  - **TMDb API** - High-quality posters
  - **YouTube Data API v3** - Trailer discovery

- **Deployment:**
  - **GitHub Pages** - Static site hosting
  - **Service Worker** - Offline caching

### Customization

**Change scraping platforms:**

Edit line 69 in `update_content.py`:
```python
url = "https://www.binged.com/streaming-premiere-dates/?mode=streaming-month&platform[]=Netflix&platform[]=Amazon&..."
```

**Add more platforms:**
- Add platform logo to project root
- Update `platformLogos` object in `script.js` (line 19)
- Update `platform_map` in `update_content.py` (line 53)

**Change scraping source:**
- Modify `scrape_movies()` method in `update_content.py`
- Update CSS selectors for new site structure

## 🚀 Deployment

### Deploy to GitHub Pages

1. **Create GitHub repository:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/upcoming-content.git
git push -u origin main
```

2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: Deploy from branch `main`
   - Folder: `/ (root)`
   - Save

3. **Your site will be live at:**
   ```
   https://YOUR_USERNAME.github.io/upcoming-content/
   ```

### Automated Content Updates

To keep content fresh, you can set up automated updates:

**Option 1: GitHub Actions (Recommended)**

Create `.github/workflows/update-content.yml`:
```yaml
name: Update Content
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:      # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install playwright beautifulsoup4 cinemagoer requests
          playwright install chromium
      - name: Update content
        env:
          TMDB_API_KEY: ${{ secrets.TMDB_API_KEY }}
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
        run: python3 update_content.py --pages 5
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add movies*.json
          git commit -m "Update content [skip ci]" || exit 0
          git push
```

**Option 2: Cron Job (Local Server)**
```bash
# Add to crontab (crontab -e)
0 0 * * * cd /path/to/project && python3 update_content.py --pages 5
```

## 🐛 Troubleshooting

### Scraping Issues

**Timeout errors:**
```
TimeoutError: Waiting for selector '.bng-movies-table-item' failed
```

**Solutions:**
- Increase timeout in `update_content.py` line 92: `timeout=60000` → `timeout=120000`
- Check internet connection
- Verify Binged.com is accessible
- Website might be blocking automated requests - add longer delays

**No movies found (0 scraped):**
```
✅ Scraped 0 movies total
```

**Solutions:**
- Website structure may have changed - inspect page and update CSS selectors
- Check if platform filters in URL are correct (line 69)
- Try running with headless=False to see what's happening:
  ```python
  browser = await p.chromium.launch(headless=False)  # Line 72
  ```

### API Enrichment Issues

**IMDb enrichment fails (0/40 matches):**

**Solutions:**
- IMDb API might be temporarily down - try again later
- Increase rate limit delay in line 251: `time.sleep(0.5)` → `time.sleep(1.0)`
- Check if movie titles have special characters causing search issues

**YouTube trailers not found:**

**Solutions:**
- Set `YOUTUBE_API_KEY` for better results
- Fallback scraping might be blocked - check YouTube's robots.txt
- Verify search query format in line 273

**TMDb posters missing:**

**Solutions:**
- Verify `TMDB_API_KEY` is set correctly
- Check TMDb API status: https://status.themoviedb.org/
- Some movies might not have posters - this is normal
- Free API tier has rate limits (wait and retry)

### Web Interface Issues

**YouTube trailers don't play:**
- Check browser console for CORS errors
- Ensure using `youtube-nocookie.com` domain (line 408 in script.js)
- Some videos have embed restrictions - this is a YouTube limitation

**Posters not loading:**
- Check TMDb CDN is accessible
- Verify `poster_url_large` exists in movies_enriched.json
- Browser might be blocking images - check console

**Filters not working:**
- Clear browser cache and reload
- Check if platform names match exactly in script.js and movies_enriched.json
- Open browser console and check for JavaScript errors

### Performance Issues

**Scraping is slow:**
- Reduce pages: `--pages 2` instead of `--pages 10`
- Skip heavy enrichments: `--no-posters`
- Network speed affects Playwright loading times

**Web UI is laggy:**
- Too many movies rendering - add pagination
- Reduce animation duration in styles.css
- Disable backdrop-filter on low-end devices

## 🎯 Features Roadmap

- [ ] Add pagination for large movie collections
- [ ] Implement search functionality
- [ ] Add sorting options (by date, platform, etc.)
- [ ] Dark/light theme toggle
- [ ] User preferences saved in localStorage
- [ ] Genre filtering
- [ ] Release date notifications
- [ ] Export to calendar (iCal/Google Calendar)
- [ ] IMDb ratings display
- [ ] Rotten Tomatoes integration

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly:**
   - Run the unified script: `python3 update_content.py --pages 2`
   - Test web interface locally
   - Check all filters and animations work
5. **Commit your changes:** `git commit -m 'Add amazing feature'`
6. **Push to branch:** `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow existing code style (PEP 8 for Python)
- Add comments for complex logic
- Test on multiple browsers (Chrome, Safari, Firefox)
- Ensure mobile responsiveness
- Update README if adding new features

## 📝 Credits & Acknowledgments

- **Data Source:** [Binged.com](https://www.binged.com/)
- **Movie Metadata:** [IMDb](https://www.imdb.com/) via [Cinemagoer](https://cinemagoer.github.io/)
- **Posters:** [The Movie Database (TMDb)](https://www.themoviedb.org/)
- **Trailers:** [YouTube](https://www.youtube.com/)
- **Design Inspiration:** Apple's design language and aesthetics
- **Browser Automation:** [Playwright](https://playwright.dev/)

## ⚖️ License & Disclaimer

This project is provided as-is for **educational and personal use only**.

**Important Notes:**
- Respect Binged.com's terms of service and robots.txt
- API keys are required for full functionality (TMDb, YouTube)
- Free tier API limits apply - use responsibly
- Commercial use requires appropriate licensing from data sources
- Movie posters and trailers are property of their respective copyright holders

**No Warranty:** This software is provided "as is" without warranty of any kind.

## 📧 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/Mono-TV/upcoming-content/issues)
- **Live Demo:** [https://mono-tv.github.io/upcoming-content/](https://mono-tv.github.io/upcoming-content/)

---

Made with ❤️ for movie enthusiasts
