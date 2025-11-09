# Complete Testing Guide for Claude Code Terminal

## 🚀 Quick Start - What to Run First

### Step 1: Frontend Test with Dummy Data (2 minutes)

```bash
# Create minimal test data
cat > ott_releases_enriched.json << 'EOF'
[{"title": "Test OTT Released", "release_date": "15 Oct 2024", "platforms": ["Netflix"], "content_type": "ott_released", "poster_url_medium": "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg", "youtube_id": "dQw4w9WgXcQ", "deeplinks": {"Netflix": "https://netflix.com"}}]
EOF

cat > movies_enriched.json << 'EOF'
[{"title": "Test OTT Upcoming", "release_date": "25 Dec 2025", "platforms": ["Jio Hotstar"], "content_type": "ott_upcoming", "poster_url_medium": "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg", "youtube_id": "dQw4w9WgXcQ"}]
EOF

cat > theatre_current_enriched.json << 'EOF'
[{"title": "Test Theatre Now", "release_date": "1 Nov 2024", "content_type": "theatre_current", "video_formats": ["IMAX 3D", "DOLBY CINEMA"], "cbfc_rating": "UA", "duration": "2h 30m", "poster_url_medium": "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg", "youtube_id": "dQw4w9WgXcQ"}]
EOF

cat > theatre_upcoming_enriched.json << 'EOF'
[{"title": "Test Theatre Upcoming", "release_date": "20 Dec 2025", "content_type": "theatre_upcoming", "video_formats": ["IMAX 2D", "3D"], "cbfc_rating": "U", "duration": "2h 15m", "poster_url_medium": "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg", "youtube_id": "dQw4w9WgXcQ"}]
EOF

# Start server and test
python3 -m http.server 8000 &
SERVER_PID=$!
echo "🌐 Server started at http://localhost:8000"
echo "📝 Open browser and verify all 4 rows display"
echo "⏹️  Press Ctrl+C when done, then run: kill $SERVER_PID"
```

**Expected Result:**
- ✅ 4 content rows visible
- ✅ 1 movie in each row
- ✅ Video format badges visible on theatre movies (hover to see)
- ✅ Platform badges visible on OTT movies (hover to see)

**Clean up:**
```bash
kill $SERVER_PID
rm ott_releases_enriched.json movies_enriched.json theatre_current_enriched.json theatre_upcoming_enriched.json
```

---

### Step 2: Test Single Scraper (5-10 minutes)

**Test the OTT releases scraper first (fastest and simplest):**

```bash
# Run with minimal data and no deeplinks for speed
python3 scrape_ott_releases.py --pages 1 --no-deeplinks --debug
```

**Expected Output:**
- ✅ Browser starts (headless)
- ✅ Scrapes 1 page from Binged
- ✅ Saves `ott_releases.json`
- ✅ Shows count of movies scraped (typically 10-15)

**Check the output:**
```bash
# Verify file was created
ls -lh ott_releases.json

# View first movie
head -30 ott_releases.json | jq '.[0]' 2>/dev/null || head -30 ott_releases.json
```

**If successful, test theatre scraper:**
```bash
python3 scrape_theatre_current.py --city bengaluru --debug
```

**Expected Output:**
- ✅ Auto-scrolls BookMyShow page
- ✅ Extracts movie details
- ✅ Saves `theatre_current_bengaluru.json`
- ✅ Shows count of movies (typically 30-50)

---

### Step 3: Test Enrichment (10-15 minutes)

**Note:** This requires TMDB API key

```bash
# Check if API key is set
if [ -z "$TMDB_API_KEY" ]; then
    echo "⚠️  TMDB_API_KEY not set. Set it with:"
    echo "export TMDB_API_KEY='your_key_here'"
    exit 1
fi

# Test enrichment on the OTT releases we scraped
python3 -c "
from update_content import ContentUpdater
import json

# Load scraped data
with open('ott_releases.json', 'r') as f:
    movies = json.load(f)

# Take only first 5 movies for quick test
movies = movies[:5]

print(f'Testing enrichment on {len(movies)} movies...')

# Create updater
updater = ContentUpdater()
updater.movies = movies

# Run enrichment
print('\n--- TMDB Enrichment ---')
updater.enrich_with_tmdb_complete()

print('\n--- IMDb Enrichment ---')
updater.enrich_with_imdb_fallback()

print('\n--- YouTube Enrichment ---')
updater.enrich_with_youtube_trailers()

# Save enriched
with open('ott_releases_enriched_test.json', 'w') as f:
    json.dump(updater.movies, f, indent=2)

print(f'\n✅ Saved to ott_releases_enriched_test.json')
"
```

**Check enrichment results:**
```bash
# View enriched movie
head -50 ott_releases_enriched_test.json | jq '.[0]' 2>/dev/null || head -50 ott_releases_enriched_test.json
```

**Look for:**
- ✅ `tmdb_id` present
- ✅ `imdb_id` present
- ✅ `poster_url_medium` or `poster_url_large` present
- ✅ `youtube_id` present (if trailer found)

---

### Step 4: Full Pipeline Test (60-85 minutes)

**Only run this if you have time. This scrapes all 4 content types with enrichment.**

```bash
# Run with minimal pages for faster testing
python3 update_all_content.py \
    --ott-pages 2 \
    --city bengaluru \
    --debug 2>&1 | tee test_run.log
```

**Expected Output Files:**
```bash
ls -lh ott_releases_enriched.json
ls -lh movies_enriched.json
ls -lh theatre_current_enriched.json
ls -lh theatre_upcoming_enriched.json
```

**Verify data quality:**
```bash
# Check counts
echo "OTT Released: $(jq 'length' ott_releases_enriched.json 2>/dev/null || echo 'N/A')"
echo "OTT Upcoming: $(jq 'length' movies_enriched.json 2>/dev/null || echo 'N/A')"
echo "Theatre Current: $(jq 'length' theatre_current_enriched.json 2>/dev/null || echo 'N/A')"
echo "Theatre Upcoming: $(jq 'length' theatre_upcoming_enriched.json 2>/dev/null || echo 'N/A')"

# Check enrichment quality
echo -e "\n--- Enrichment Stats (OTT Released) ---"
jq '[.[] | {
  has_tmdb: (.tmdb_id != null),
  has_imdb: (.imdb_id != null),
  has_youtube: (.youtube_id != null),
  has_poster: (.poster_url_medium != null or .poster_url_large != null),
  has_deeplink: (.deeplinks != null)
}] | {
  total: length,
  with_tmdb: [.[] | select(.has_tmdb)] | length,
  with_imdb: [.[] | select(.has_imdb)] | length,
  with_youtube: [.[] | select(.has_youtube)] | length,
  with_poster: [.[] | select(.has_poster)] | length,
  with_deeplink: [.[] | select(.has_deeplink)] | length
}' ott_releases_enriched.json 2>/dev/null

echo -e "\n--- Enrichment Stats (Theatre Current) ---"
jq '[.[] | {
  has_tmdb: (.tmdb_id != null),
  has_formats: (.video_formats != null and (.video_formats | length) > 0),
  has_cbfc: (.cbfc_rating != null),
  has_duration: (.duration != null)
}] | {
  total: length,
  with_tmdb: [.[] | select(.has_tmdb)] | length,
  with_formats: [.[] | select(.has_formats)] | length,
  with_cbfc: [.[] | select(.has_cbfc)] | length,
  with_duration: [.[] | select(.has_duration)] | length
}' theatre_current_enriched.json 2>/dev/null
```

**Test Frontend:**
```bash
python3 -m http.server 8000
# Visit http://localhost:8000
```

---

## 🔍 Troubleshooting

### Issue: "Module not found" errors

```bash
pip3 install playwright beautifulsoup4 cinemagoer requests pillow
playwright install chromium
```

### Issue: Empty JSON files

```bash
# Check debug output
python3 scrape_ott_releases.py --pages 1 --debug

# Look for screenshot
ls -lh debug_ott_releases.png

# View screenshot to see what went wrong
open debug_ott_releases.png  # Mac
xdg-open debug_ott_releases.png  # Linux
```

### Issue: Rate limiting / Connection errors

```bash
# Increase delays in config.py
# Or reduce pages:
python3 scrape_ott_releases.py --pages 1
```

### Issue: Missing API keys

```bash
# TMDB (required for enrichment)
export TMDB_API_KEY="your_key_from_themoviedb.org"

# YouTube (optional, has fallback)
export YOUTUBE_API_KEY="your_key_from_console.cloud.google.com"
```

### Issue: BookMyShow scraping fails

```bash
# Run with debug to save screenshot
python3 scrape_theatre_current.py --city bengaluru --debug

# Check screenshot
ls -lh debug_theatre_current.png
```

---

## ✅ Success Criteria

### Frontend Display
- [ ] All 4 content rows visible
- [ ] Each row has horizontal scrolling
- [ ] Cards display properly with posters
- [ ] Hover shows platform badges (OTT) or format badges (theatre)
- [ ] Click on card plays trailer (if available)
- [ ] Platform filters work (OTT rows only)
- [ ] Content type filters work (Movies/Shows)
- [ ] Empty rows are hidden

### Data Quality
- [ ] At least 70% of movies have TMDB data
- [ ] At least 50% of movies have IMDb IDs
- [ ] At least 40% of movies have YouTube trailers
- [ ] OTT released movies have deeplinks
- [ ] Theatre movies have video formats

### Performance
- [ ] Page loads in < 3 seconds
- [ ] Horizontal scrolling is smooth
- [ ] Images load progressively (lazy loading)
- [ ] No console errors

---

## 📊 Expected Run Times

| Task | Duration |
|------|----------|
| Frontend test (dummy data) | 2 minutes |
| Single scraper test | 5-10 minutes |
| Enrichment test (5 movies) | 3-5 minutes |
| Full pipeline (--ott-pages 2) | 30-40 minutes |
| Full pipeline (--ott-pages 5) | 60-85 minutes |

---

## 🎯 Recommended Testing Sequence

1. **Frontend with dummy data** (2 min) ← **START HERE**
2. **Single OTT scraper** (5-10 min)
3. **Enrichment test** (5 min)
4. **Frontend with real data** (2 min)
5. **Full pipeline** (60-85 min) ← Only if deploying to production

---

## 📝 For Claude Code Terminal

When testing with Claude Code in terminal, provide this context:

**Testing Context:**
- Repository: `~/upcoming-content`
- Branch: `claude/add-three-content-rows-011CUwpsGds948Ze9khjgEeX` (or main after merge)
- Python version: 3.7+
- Required: TMDB_API_KEY environment variable

**Commands to run in sequence:**
1. Create dummy test files and test frontend
2. Test individual scrapers with `--debug` flag
3. Test enrichment on small dataset
4. Run full pipeline if time permits
5. Report any errors with debug output

**Expected Issues:**
- BookMyShow website structure may have changed (check debug screenshots)
- Rate limiting on heavy scraping (add delays in config.py)
- Missing API keys (set TMDB_API_KEY)
- Network timeouts (retry with fewer pages)
