# Movie Enrichment Guide

This guide explains the different enrichment options available for adding metadata and posters to your movies.

## Overview

There are two main enrichment approaches:

1. **TMDB Enrichment** (Primary) - Uses The Movie Database API
2. **qdMovieAPI Enrichment** (Alternative) - Uses IMDB data via local API service

---

## Option 1: TMDB Enrichment (Recommended)

### Advantages
- Official API with comprehensive data
- High-quality posters and backdrops
- Multiple poster sizes
- Cast, crew, and trailer information
- No local service required

### Setup

1. Get a free TMDB API key:
   - Visit: https://www.themoviedb.org/settings/api
   - Sign up for a free account
   - Request an API key

2. Set the environment variable:
   ```bash
   export TMDB_API_KEY='your_api_key_here'
   ```

### Usage

**Full scraping and enrichment:**
```bash
python3 update_content.py --pages 5
```

**Re-enrich only missing posters:**
```bash
python3 re_enrich_posters.py
```

**Options:**
- `--pages N` - Number of pages to scrape (default: 5)
- `--no-trailers` - Skip trailer enrichment
- `--test` - Test mode (process only 3 movies)

### What gets enriched:
- ✓ Multiple poster sizes (92px to original)
- ✓ Multiple backdrop images
- ✓ Overview/description
- ✓ Genres
- ✓ Cast and crew
- ✓ Directors and writers
- ✓ IMDB ID
- ✓ TMDB ratings
- ✓ YouTube trailers
- ✓ Runtime
- ✓ Release dates
- ✓ Original language

---

## Option 2: qdMovieAPI Enrichment (Alternative)

### Advantages
- Uses IMDB data directly
- No API key required
- Good for when TMDB is unavailable
- Provides IMDB ratings and metadata

### Disadvantages
- Requires running a local API service
- Less comprehensive than TMDB
- Single poster quality
- Slower performance

### Setup

**Step 1: Clone and run qdMovieAPI**

Choose one method:

**Option A: With Docker (Recommended)**
```bash
# Clone the repository
git clone https://github.com/tveronesi/qdMovieAPI.git
cd qdMovieAPI

# Run with Docker
docker compose up --build
```

**Option B: Without Docker**
```bash
# Clone the repository
git clone https://github.com/tveronesi/qdMovieAPI.git
cd qdMovieAPI

# Install dependencies
pip install -r requirements.txt

# Run the API
python api.py
```

The API will run on `http://127.0.0.1:5000`

**Step 2: Verify API is running**
```bash
# Test the connection
curl http://127.0.0.1:5000/
```

### Usage

**From your upcoming-content directory:**
```bash
# Enrich all movies missing data
python3 enrich_with_qdmovie.py

# Test mode (only 3 movies)
python3 enrich_with_qdmovie.py --test

# Custom API URL
python3 enrich_with_qdmovie.py --api-url http://localhost:5000
```

### What gets enriched:
- ✓ IMDB ID
- ✓ Poster image
- ✓ Plot/description
- ✓ Genres
- ✓ IMDB rating
- ✓ Runtime
- ✓ Director
- ✓ Cast/actors
- ✓ Release year

---

## Comparison Table

| Feature | TMDB | qdMovieAPI |
|---------|------|------------|
| Setup complexity | Easy (API key) | Medium (local service) |
| Poster quality | Multiple sizes | Single size |
| Backdrop images | ✓ | ✗ |
| Cast & crew | Detailed | Basic |
| Trailers | ✓ | ✗ |
| IMDB ID | ✓ | ✓ |
| Ratings | TMDB + vote count | IMDB |
| Speed | Fast | Slower |
| API key required | Yes | No |

---

## Troubleshooting

### TMDB Issues

**Error: "TMDB API KEY REQUIRED"**
```bash
# Make sure to export the key
export TMDB_API_KEY='your_key_here'

# Verify it's set
echo $TMDB_API_KEY
```

**Error: Rate limiting**
- The script includes automatic rate limiting (0.25s delay)
- If you hit limits, increase the delay in the script

### qdMovieAPI Issues

**Error: "Cannot connect to qdMovieAPI"**
- Make sure the service is running: `curl http://127.0.0.1:5000/`
- Check Docker containers: `docker ps`
- Check the API logs for errors

**Error: "Not found" for many movies**
- IMDB search can be less accurate than TMDB
- Try cleaning up movie titles manually
- Consider using TMDB for better results

---

## Hybrid Approach

You can use both enrichment methods together:

1. Run TMDB enrichment first (gets most data)
2. Run qdMovieAPI for movies that TMDB couldn't find
3. This gives you the best coverage

```bash
# First pass with TMDB
export TMDB_API_KEY='your_key'
python3 re_enrich_posters.py

# Second pass with qdMovieAPI (for remaining movies)
python3 enrich_with_qdmovie.py
```

---

## Output Files

- `movies.json` - Raw scraped data from Binged.com
- `movies_enriched.json` - Final enriched data (used by the website)

---

## Best Practices

1. **Start with TMDB** - It's more comprehensive and easier to use
2. **Use qdMovieAPI as fallback** - For movies TMDB doesn't have
3. **Test first** - Use `--test` flag to verify before processing all movies
4. **Check the results** - Review `movies_enriched.json` after enrichment
5. **Re-run periodically** - New movies may get better metadata over time

---

## Need Help?

- TMDB API docs: https://developers.themoviedb.org/3
- qdMovieAPI repo: https://github.com/tveronesi/qdMovieAPI
- Check script output for specific error messages
