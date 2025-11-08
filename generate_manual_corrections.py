#!/usr/bin/env python3
"""
Generate manual corrections from existing enriched data
Useful when IMDb API is failing
"""

import json

print("Generating manual corrections from existing enriched data...")

# Load current enriched data
try:
    with open('movies_enriched.json', 'r', encoding='utf-8') as f:
        movies = json.load(f)
except FileNotFoundError:
    print("❌ movies_enriched.json not found")
    print("Run the scraper first or use existing data")
    exit(1)

# Load existing corrections
try:
    with open('manual_corrections.json', 'r', encoding='utf-8') as f:
        corrections_data = json.load(f)
        existing_corrections = corrections_data.get('corrections', {})
except:
    existing_corrections = {}

# Generate corrections from movies that have IMDb/TMDb data
new_corrections = {}
count = 0

for movie in movies:
    title = movie.get('title')
    imdb_id = movie.get('imdb_id')
    imdb_year = movie.get('imdb_year')
    tmdb_id = movie.get('tmdb_id')
    tmdb_media_type = movie.get('tmdb_media_type')

    # Only add if we have IMDb data and it's not already in corrections
    if title and imdb_id and title not in existing_corrections:
        correction = {
            'imdb_id': imdb_id,
            'imdb_year': imdb_year or '',
        }

        # Add TMDb data if available
        if tmdb_id:
            correction['tmdb_id'] = tmdb_id
            correction['tmdb_media_type'] = tmdb_media_type or 'movie'

        correction['reason'] = 'Auto-generated from existing enriched data'

        new_corrections[title] = correction
        count += 1

print(f"\n✅ Generated {count} new corrections from existing data")
print(f"📋 Keeping {len(existing_corrections)} existing corrections")

# Merge with existing
all_corrections = {**existing_corrections, **new_corrections}

# Save
output = {
    "_comment": "Manual corrections for movies with ambiguous titles or incorrect matches",
    "_instructions": "Add entries here to override automatic matching. Auto-generated entries can be edited.",
    "corrections": all_corrections
}

with open('manual_corrections.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n💾 Saved {len(all_corrections)} total corrections to manual_corrections.json")
print("\nThese corrections will be used automatically on next update")
print("This bypasses the IMDb API completely for these titles")
