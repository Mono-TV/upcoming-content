# Manual Corrections Guide

## When to Use Manual Corrections

Use `manual_corrections.json` when automatic API matching fails for:

1. **Generic titles** - "Mom", "Her", "It", etc. that match wrong movies
2. **Regional films** - Hindi/Tamil/Telugu films matching Hollywood versions
3. **Remakes** - When there are multiple versions across languages
4. **Series vs Movies** - When TV show matched instead of movie
5. **Wrong year** - When IMDb returns different release year

## How to Add Corrections

### 1. Identify the Problem

Run the update script and check the output:
```bash
python3 update_content.py --pages 2
```

Look for suspicious matches:
- Wrong year (too old for upcoming release)
- Generic titles that might be ambiguous
- Mismatched media types (TV vs movie)

### 2. Find Correct IDs

**For IMDb:**
- Search on https://www.imdb.com/
- Copy the IMDb ID from URL (e.g., `tt5690360`)
- Note the release year

**For TMDb:**
- Search on https://www.themoviedb.org/
- Copy the TMDb ID from URL (e.g., `433498`)
- Note if it's a movie or tv show

### 3. Add to manual_corrections.json

```json
{
  "corrections": {
    "Exact Title from Binged": {
      "imdb_id": "tt1234567",
      "imdb_year": "2017",
      "tmdb_id": 123456,
      "tmdb_media_type": "movie",
      "reason": "Brief explanation why manual correction needed"
    }
  }
}
```

### 4. Re-run Update Script

```bash
python3 update_content.py --pages 5
```

The script will show:
```
📋 Loaded 1 manual corrections
[1/40] Mom... ✓ tt5690360 (manual)
```

## Example Corrections

### Generic Title (Mom)

**Problem:** "Mom" matched wrong 2013 TV series instead of 2017 Hindi film

```json
{
  "Mom": {
    "imdb_id": "tt5690360",
    "imdb_year": "2017",
    "tmdb_id": 433498,
    "tmdb_media_type": "movie",
    "reason": "Generic title - needs to match 2017 Hindi film with Sridevi"
  }
}
```

### Regional Film with Common Name

**Problem:** Hindi film "Hero" matching Hollywood "Hero" (2002)

```json
{
  "Hero": {
    "imdb_id": "tt2181931",
    "imdb_year": "2015",
    "tmdb_id": 297638,
    "tmdb_media_type": "movie",
    "reason": "Hindi film by Nikkhil Advani, not Hollywood Hero"
  }
}
```

### TV Series vs Movie

**Problem:** Movie title matching TV series with same name

```json
{
  "The Office": {
    "imdb_id": "tt0386676",
    "imdb_year": "2005",
    "tmdb_id": 2316,
    "tmdb_media_type": "tv",
    "reason": "TV series, not movie"
  }
}
```

## Field Reference

### Required Fields

- **imdb_id** (string): IMDb ID with 'tt' prefix (e.g., "tt5690360")
- **imdb_year** (string): Release year as string (e.g., "2017")

### Optional Fields

- **tmdb_id** (integer): TMDb ID number (e.g., 433498)
- **tmdb_media_type** (string): Either "movie" or "tv"
- **reason** (string): Why this correction is needed (for documentation)

## Verification

### Check if Correction is Applied

After adding a correction, verify it's working:

```bash
python3 -c "
import json
with open('movies_enriched.json') as f:
    movies = json.load(f)
    for m in movies:
        if m['title'] == 'Mom':
            print('IMDb ID:', m.get('imdb_id'))
            print('IMDb Year:', m.get('imdb_year'))
            print('TMDb ID:', m.get('tmdb_id'))
            break
"
```

Expected output:
```
IMDb ID: tt5690360
IMDb Year: 2017
TMDb ID: 433498
```

### Test Poster URL

Verify the poster is accessible:

```bash
curl -I "https://image.tmdb.org/t/p/w500/poster_path.jpg"
```

Should return `HTTP/2 200` if valid.

## Troubleshooting

### Correction Not Applied

1. **Check JSON syntax** - Use a JSON validator
2. **Verify exact title match** - Title must match exactly from Binged.com
3. **Check file location** - `manual_corrections.json` must be in same directory as script

### Still Wrong Poster/Trailer

1. **Verify TMDb ID** - Check on https://www.themoviedb.org/
2. **Check media_type** - Must be "movie" or "tv"
3. **Run fix_mom_poster.py** - For poster-specific fixes

## Best Practices

1. **Always add reason** - Document why correction is needed
2. **Verify before adding** - Check IMDb/TMDb URLs manually
3. **Test immediately** - Run update script after adding correction
4. **One at a time** - Add corrections incrementally and test
5. **Document patterns** - Note if certain types of titles always fail

## Safety Features

The manual corrections system includes:

✓ **Automatic loading** - Checked at script startup
✓ **Priority override** - Manual corrections applied before API searches
✓ **Poster validation** - URLs tested before saving
✓ **Clear logging** - Shows which movies use manual corrections
✓ **Graceful fallback** - Script continues if file missing

## Future Improvements

Consider adding to manual corrections as you discover issues with:
- Sequels/franchises with similar names
- International remakes
- Documentaries vs narrative films
- Short films vs feature films
