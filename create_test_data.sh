#!/bin/bash
# Create test data for all 4 content rows
# This allows frontend testing without scraping

echo "📦 Creating test data files..."

# 1. OTT Releases (already released)
cat > ott_releases_enriched.json << 'EOF'
[
  {
    "title": "Venom: The Last Dance",
    "release_date": "25 Oct 2024",
    "platforms": ["Netflix", "Amazon Prime Video"],
    "content_type": "ott_released",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/aosm8NMQ3UyoBVpSxyimorCQykC.jpg",
    "poster_url_large": "https://image.tmdb.org/t/p/original/aosm8NMQ3UyoBVpSxyimorCQykC.jpg",
    "youtube_id": "HyIyd9joTTc",
    "youtube_url": "https://www.youtube.com/watch?v=HyIyd9joTTc",
    "tmdb_id": 912649,
    "tmdb_media_type": "movie",
    "imdb_id": "tt16366836",
    "imdb_year": "2024",
    "deeplinks": {
      "Netflix": "https://www.netflix.com/title/81234567",
      "Amazon Prime Video": "https://www.primevideo.com/detail/B0ABCDEF"
    }
  },
  {
    "title": "The Wild Robot",
    "release_date": "20 Oct 2024",
    "platforms": ["Jio Hotstar"],
    "content_type": "ott_released",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/wTnV3PCVW5O92JMrFvvrRcV39RU.jpg",
    "youtube_id": "67vbA5ZJdKQ",
    "tmdb_id": 698687,
    "tmdb_media_type": "movie",
    "imdb_id": "tt29623480",
    "deeplinks": {
      "Jio Hotstar": "https://www.hotstar.com/in/movies/the-wild-robot/1234567890"
    }
  },
  {
    "title": "Smile 2",
    "release_date": "18 Oct 2024",
    "platforms": ["Sony LIV"],
    "content_type": "ott_released",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/aE85MnPIsSoSs3978Noo16BRsKN.jpg",
    "youtube_id": "Bczlh29kfS8",
    "tmdb_id": 1100782,
    "imdb_id": "tt30321337"
  }
]
EOF

# 2. OTT Upcoming
cat > movies_enriched.json << 'EOF'
[
  {
    "title": "Mufasa: The Lion King",
    "release_date": "20 Dec 2024",
    "platforms": ["Jio Hotstar"],
    "content_type": "ott_upcoming",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/lurEK87kukWNaHd0zYnsi3yzJrs.jpg",
    "youtube_id": "o17MF9vnabg",
    "tmdb_id": 762509,
    "tmdb_media_type": "movie",
    "imdb_id": "tt13186482"
  },
  {
    "title": "Wicked",
    "release_date": "22 Nov 2024",
    "platforms": ["Netflix"],
    "content_type": "ott_upcoming",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/c5Tqxeo1UpBvnAc3csUm7j3hlQl.jpg",
    "youtube_id": "6COmYeLsz4c",
    "tmdb_id": 402431,
    "imdb_id": "tt1262426"
  },
  {
    "title": "Kraven the Hunter",
    "release_date": "13 Dec 2024",
    "platforms": ["Amazon Prime Video", "Sony LIV"],
    "content_type": "ott_upcoming",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/1GvBhRxY6MELDfxFrete6BNhBB5.jpg",
    "youtube_id": "nxfnIW5ygAw",
    "tmdb_id": 539972,
    "imdb_id": "tt8277246"
  },
  {
    "title": "Gladiator II",
    "release_date": "15 Nov 2024",
    "platforms": ["Netflix", "Jio Hotstar"],
    "content_type": "ott_upcoming",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/2cxhvwyEwRlysAmRH4iodkvo0z5.jpg",
    "youtube_id": "nxfnIW5ygAw",
    "tmdb_id": 558449,
    "imdb_id": "tt9218128"
  }
]
EOF

# 3. Theatre Current (Bangalore)
cat > theatre_current_enriched.json << 'EOF'
[
  {
    "title": "Bhool Bhulaiyaa 3",
    "release_date": "1 Nov 2024",
    "content_type": "theatre_current",
    "location": "Bengaluru",
    "video_formats": ["IMAX 3D", "DOLBY CINEMA", "4DX", "3D", "2D"],
    "cbfc_rating": "UA",
    "duration": "2h 38m",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/4qr1Btk46yp6qpbMyh7O5YyFSWD.jpg",
    "youtube_id": "crUkRJvPLJI",
    "tmdb_id": 1100856,
    "imdb_id": "tt27688034",
    "detail_url": "https://in.bookmyshow.com/movies/bhool-bhulaiyaa-3/ET00395211",
    "booking_link": "https://in.bookmyshow.com/buytickets/bhool-bhulaiyaa-3-bengaluru/movie-bang-ET00395211-MT/20241109"
  },
  {
    "title": "Singham Again",
    "release_date": "1 Nov 2024",
    "content_type": "theatre_current",
    "location": "Bengaluru",
    "video_formats": ["IMAX 2D", "DOLBY ATMOS", "3D", "2D"],
    "cbfc_rating": "UA",
    "duration": "2h 24m",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/cIZv1lJPXzgRWyF5KHGIByuJYOY.jpg",
    "youtube_id": "rGfW_mNTxHw",
    "tmdb_id": 1100857,
    "imdb_id": "tt27688035",
    "detail_url": "https://in.bookmyshow.com/movies/singham-again/ET00395212"
  },
  {
    "title": "Venom: The Last Dance",
    "release_date": "25 Oct 2024",
    "content_type": "theatre_current",
    "location": "Bengaluru",
    "video_formats": ["IMAX 3D", "4DX 3D", "MX4D 3D", "3D", "2D"],
    "cbfc_rating": "UA",
    "duration": "1h 49m",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/aosm8NMQ3UyoBVpSxyimorCQykC.jpg",
    "youtube_id": "HyIyd9joTTc",
    "tmdb_id": 912649,
    "imdb_id": "tt16366836"
  },
  {
    "title": "Amaran",
    "release_date": "31 Oct 2024",
    "content_type": "theatre_current",
    "location": "Bengaluru",
    "video_formats": ["DOLBY ATMOS", "2D"],
    "cbfc_rating": "UA",
    "duration": "2h 48m",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/zHqU5CqZN00c1Kn5q0uf9NhVGke.jpg",
    "youtube_id": "1C1YDpWc6eI",
    "tmdb_id": 1235672,
    "imdb_id": "tt27688036"
  }
]
EOF

# 4. Theatre Upcoming
cat > theatre_upcoming_enriched.json << 'EOF'
[
  {
    "title": "Pushpa 2: The Rule",
    "release_date": "6 Dec 2024",
    "content_type": "theatre_upcoming",
    "location": "Bengaluru",
    "video_formats": ["IMAX 3D", "IMAX 2D", "DOLBY CINEMA", "4DX", "3D", "2D"],
    "cbfc_rating": "UA",
    "duration": "TBA",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/dA9tfq6GQkl0IXbVNFUZLLJlx4w.jpg",
    "youtube_id": "ZU1HbG-0oHg",
    "tmdb_id": 1084736,
    "imdb_id": "tt21807222",
    "detail_url": "https://in.bookmyshow.com/movies/pushpa-2-the-rule/ET00356724"
  },
  {
    "title": "Mufasa: The Lion King",
    "release_date": "20 Dec 2024",
    "content_type": "theatre_upcoming",
    "location": "Bengaluru",
    "video_formats": ["IMAX 3D", "DOLBY CINEMA 3D", "3D SCREEN X", "3D", "2D"],
    "cbfc_rating": "U",
    "duration": "TBA",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/lurEK87kukWNaHd0zYnsi3yzJrs.jpg",
    "youtube_id": "o17MF9vnabg",
    "tmdb_id": 762509,
    "imdb_id": "tt13186482"
  },
  {
    "title": "Wicked",
    "release_date": "22 Nov 2024",
    "content_type": "theatre_upcoming",
    "location": "Bengaluru",
    "video_formats": ["IMAX 2D", "DOLBY ATMOS", "2D"],
    "cbfc_rating": "UA",
    "duration": "2h 40m",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/c5Tqxeo1UpBvnAc3csUm7j3hlQl.jpg",
    "youtube_id": "6COmYeLsz4c",
    "tmdb_id": 402431,
    "imdb_id": "tt1262426"
  },
  {
    "title": "Gladiator II",
    "release_date": "15 Nov 2024",
    "content_type": "theatre_upcoming",
    "location": "Bengaluru",
    "video_formats": ["IMAX 2D", "DOLBY CINEMA", "2D"],
    "cbfc_rating": "UA",
    "duration": "2h 28m",
    "poster_url_medium": "https://image.tmdb.org/t/p/w500/2cxhvwyEwRlysAmRH4iodkvo0z5.jpg",
    "youtube_id": "nxfnIW5ygAw",
    "tmdb_id": 558449,
    "imdb_id": "tt9218128"
  }
]
EOF

echo "✅ Test data files created:"
ls -lh ott_releases_enriched.json movies_enriched.json theatre_current_enriched.json theatre_upcoming_enriched.json

echo ""
echo "🌐 Start server with: python3 -m http.server 8000"
echo "📱 Visit: http://localhost:8000"
echo ""
echo "🧹 Clean up with: rm *_enriched.json"
