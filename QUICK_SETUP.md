# Quick Setup Guide

## Current Status

Your website is **already working** with:
- ✅ Movie titles, release dates, and platforms
- ✅ YouTube trailers (100% success rate!)
- ⚠️ Limited posters (only 25% have high-quality posters)
- ⚠️ No IMDb IDs (Cinemagoer API is down - **this is optional**)

## To Get High-Quality Posters

**1. Get a free TMDb API key (takes 2 minutes):**

Visit: https://www.themoviedb.org/settings/api

- Create an account (or login)
- Request an API key (choose "Developer" option)
- Copy your API key

**2. Set the API key in your terminal:**

```bash
export TMDB_API_KEY='your_tmdb_api_key_here'
```

**3. Run the update script:**

```bash
python3 update_content.py --pages 10
```

**Expected output:**
```
✅ ALL DONE!
📊 Summary:
   • Movies scraped: 52
   • With IMDb IDs: 1/52 ⊘ (optional)
   • With YouTube trailers: 52/52 ✓
   • With TMDb posters: 52/52 ✓
```

## Optional: Get YouTube API Key

For more reliable YouTube trailer matching (currently working at 100% without it):

1. Visit: https://console.cloud.google.com/apis/library/youtube.googleapis.com
2. Create a project and enable YouTube Data API v3
3. Create credentials → API key
4. Set it:

```bash
export YOUTUBE_API_KEY='your_youtube_key_here'
```

## What About IMDb?

**IMDb enrichment is OPTIONAL.** The Cinemagoer API is currently down/rate-limited, but your site works perfectly without it.

IMDb is only used to:
- Get release year for better searches (not critical)
- Add IMDb links (nice to have, not essential)

## Running Updates

### Basic Update (Recommended)
```bash
# Set API key once per terminal session
export TMDB_API_KEY='your_key_here'

# Run the update
python3 update_content.py --pages 10
```

### One-Time Setup (Permanent)
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export TMDB_API_KEY='your_tmdb_key_here'
export YOUTUBE_API_KEY='your_youtube_key_here'  # optional
```

Then run:
```bash
source ~/.bashrc  # or ~/.zshrc
python3 update_content.py --pages 10
```

## Automated Updates (GitHub Actions)

To update content automatically every day:

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add repository secrets:
   - `TMDB_API_KEY` = your TMDb key
   - `YOUTUBE_API_KEY` = your YouTube key (optional)

4. The `.github/workflows/update-content.yml` (if you create it) will use these automatically

## Troubleshooting

### "No high-quality posters"
- Check if `TMDB_API_KEY` is set: `echo $TMDB_API_KEY`
- If empty, set it again before running the script

### "IMDb enrichment fails"
- **This is normal** - Cinemagoer API is unreliable
- **Your site works fine without it**
- You can add manual corrections for specific movies if needed

### "YouTube trailers missing"
- Currently working at 100% without API key
- If it fails, set `YOUTUBE_API_KEY` for better reliability

## What Gets Updated

When you run `update_content.py`, it:

1. **Scrapes** latest movies from Binged.com
2. **Enriches** with IMDb data (optional, may fail)
3. **Finds** YouTube trailers (100% success)
4. **Fetches** TMDb posters (needs API key)
5. **Validates** all poster URLs before saving
6. **Uses** manual corrections for problematic titles

## Files Created

- `movies.json` - Raw scraped data
- `movies_with_imdb.json` - + IMDb IDs (if working)
- `movies_with_trailers.json` - + YouTube trailers
- `movies_enriched.json` - **Final file used by website** ⭐

## Next Steps

1. **Set TMDB_API_KEY** (most important for posters)
2. **Run update script** to refresh content
3. **Commit and push** to deploy to GitHub Pages
4. **(Optional)** Set up automated daily updates

---

**That's it!** With just the TMDb API key, your site will have:
- ✅ Beautiful high-quality posters
- ✅ Working YouTube trailers
- ✅ All movie information
- ✅ Smooth Apple Liquid Design animations
