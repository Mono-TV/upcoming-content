# OTTPlay Date-Based Split ✅

## Overview

OTTPlay content is now intelligently split into **Released** and **Upcoming** based on dates within the current month.

## Date Logic

### Released Content (New OTT Releases Row)
**Date Range:** Start of current month → Today
**File:** `ottplay_releases.json`
**Current Count:** 159 items (Nov 1-22, 2025)

### Upcoming Content (Upcoming OTT Releases Row)
**Date Range:** Tomorrow → End of current month
**File:** `ottplay_upcoming.json`
**Current Count:** 5 items (Nov 23-30, 2025)

## Current Data (November 2025)

### Released (159 items)
- **Date Range:** Nov 1, 2025 → Nov 22, 2025 (today)
- **Latest Releases:**
  - Juan Gabriel: I Must, I Can, I Will (Nov 22)
  - Son of a Donkey (Nov 22)
  - Bad Influencer (Nov 22)
  - Just Alice (Nov 22)
  - Heweliusz (Nov 22)

### Upcoming (5 items)
- **Date Range:** Nov 23, 2025 → Nov 30, 2025
- **Upcoming Releases:**
  - Rebirth (Nov 24)
  - Ghoda Dhai Kadam (Nov 27)
  - Raktabeej 2 (Nov 28)
  - Regai (Nov 28)
  - The Great Pre-Wedding Show (Dec 5) *[next month]*

## How It Works

### 1. Date Parsing
The script parses release dates from OTTPlay data:
```
"Nov 01, 2025" → 2025-11-01
"Nov 22, 2025" → 2025-11-22
```

### 2. Splitting Logic
```python
if release_date <= today:
    → ottplay_releases.json (Released)
else:
    → ottplay_upcoming.json (Upcoming)
```

### 3. Sorting
- **Released:** Newest first (descending)
- **Upcoming:** Earliest first (ascending)

## Files Updated

### Scripts
- ✅ `split_ottplay_by_date.py` - Splits data by date

### Data Files
- ✅ `ottplay_releases.json` - Released content (159 items)
- ✅ `ottplay_upcoming.json` - Upcoming content (5 items)

### Configuration
- ✅ `script.js` (Line 800-801) - Updated to load both files
- ✅ `service-worker.js` (Line 1-2) - Cache version v3

## Webpage Display

| Row | Source | Count | Date Range |
|-----|--------|-------|------------|
| **New OTT Releases** | `ottplay_releases.json` | 159 | Nov 1-22 |
| **Upcoming OTT Releases** | `ottplay_upcoming.json` | 5 | Nov 23-30 |
| Movies in Theatre | `theatre_current_enriched.json` | - | - |
| Upcoming Theatre | `theatre_upcoming_enriched.json` | - | - |

## Monthly Update Process

At the start of each month, re-run the split:

```bash
# 1. Scrape fresh data
python3 scrape_ottplay.py

# 2. Enrich with TMDB
export TMDB_API_KEY="your_key"
python3 enrich_ottplay_tmdb.py

# 3. Transform to website format
python3 transform_ottplay.py

# 4. Split by date (NEW STEP)
python3 split_ottplay_by_date.py

# Done! Files are ready for the website
```

## Edge Cases Handled

### Items Without Dates
- Placed in **Upcoming** by default
- Shown at the end (after dated items)

### Dates Outside Current Month
- **Past dates** (before this month) → Released
- **Future dates** (after this month) → Upcoming

### Items with "TBA" Dates
- Treated as no date
- Placed in Upcoming

## Cache Management

**Important:** Browser cache updated to v3
- Hard refresh to see changes: `Cmd/Ctrl + Shift + R`
- Or use: `clear_cache_instructions.html`

## Testing

Open `index.html` and verify:

✅ **New OTT Releases** shows:
- 159 items
- Dates from Nov 1-22
- Newest first (Nov 22 items on top)

✅ **Upcoming OTT Releases** shows:
- 5 items
- Dates from Nov 23 onwards
- Earliest first (Nov 24 on top)

## Benefits

1. **Relevant Content** - Only show current month's releases
2. **Clear Separation** - Easy to see what's out vs coming soon
3. **Auto-Sorting** - Released (newest first), Upcoming (earliest first)
4. **Smart Categorization** - Handles edge cases gracefully

---

**Status:** ✅ Complete and Production Ready
**Last Updated:** 2025-11-22 23:31:08
**Cache Version:** v3
