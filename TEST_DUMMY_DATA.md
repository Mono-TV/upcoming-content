# Quick Frontend Testing with Dummy Data

## Create Minimal Test Files

```bash
# 1. Create dummy OTT releases file
cat > ott_releases_enriched.json << 'EOF'
[
  {
    "title": "Test Movie OTT Released",
    "release_date": "15 Oct 2024",
    "platforms": ["Netflix", "Amazon Prime Video"],
    "content_type": "ott_released",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/test.jpg",
    "youtube_id": "dQw4w9WgXcQ",
    "tmdb_id": 12345,
    "imdb_id": "tt1234567",
    "deeplinks": {
      "Netflix": "https://netflix.com/title/12345",
      "Amazon Prime Video": "https://amazon.com/gp/video/detail/12345"
    }
  }
]
EOF

# 2. Create dummy OTT upcoming file
cat > movies_enriched.json << 'EOF'
[
  {
    "title": "Test Movie OTT Upcoming",
    "release_date": "25 Dec 2025",
    "platforms": ["Jio Hotstar", "Sony LIV"],
    "content_type": "ott_upcoming",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/test.jpg",
    "youtube_id": "dQw4w9WgXcQ",
    "tmdb_id": 67890,
    "imdb_id": "tt7654321"
  }
]
EOF

# 3. Create dummy theatre current file
cat > theatre_current_enriched.json << 'EOF'
[
  {
    "title": "Test Movie Theatre Now",
    "release_date": "1 Nov 2024",
    "content_type": "theatre_current",
    "location": "Bengaluru",
    "video_formats": ["IMAX 3D", "DOLBY CINEMA", "4DX"],
    "cbfc_rating": "UA",
    "duration": "2h 30m",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/test.jpg",
    "youtube_id": "dQw4w9WgXcQ",
    "tmdb_id": 11111,
    "imdb_id": "tt1111111"
  }
]
EOF

# 4. Create dummy theatre upcoming file
cat > theatre_upcoming_enriched.json << 'EOF'
[
  {
    "title": "Test Movie Theatre Upcoming",
    "release_date": "20 Dec 2025",
    "content_type": "theatre_upcoming",
    "location": "Bengaluru",
    "video_formats": ["IMAX 2D", "3D", "2D"],
    "cbfc_rating": "U",
    "duration": "2h 15m",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/test.jpg",
    "youtube_id": "dQw4w9WgXcQ",
    "tmdb_id": 22222,
    "imdb_id": "tt2222222"
  }
]
EOF

# 5. Start local server
python3 -m http.server 8000
```

Then visit: **http://localhost:8000**

## What to Check
- ✅ All 4 rows should appear
- ✅ Each row should have 1 test movie
- ✅ Video format badges should appear on theatre movies (hover over cards)
- ✅ Platform badges should appear on OTT movies (hover over cards)
- ✅ Click on cards to test trailer playback

## Clean Up Test Files
```bash
rm ott_releases_enriched.json movies_enriched.json theatre_current_enriched.json theatre_upcoming_enriched.json
```
