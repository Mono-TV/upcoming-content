#!/usr/bin/env python3
"""
Remove all Binged.png poster references from movies_enriched.json
and prepare for re-enrichment
"""

import json

def fix_binged_posters():
    """Remove all Binged.png posters from the enriched data"""

    # Load the enriched data
    with open('movies_enriched.json', 'r', encoding='utf-8') as f:
        movies = json.load(f)

    print(f"Total movies: {len(movies)}")

    fixed_count = 0

    for movie in movies:
        modified = False

        # Check all poster-related fields for Binged.png
        fields_to_check = [
            'poster_url_medium',
            'poster_url_large',
            'backdrop_url'
        ]

        for field in fields_to_check:
            if field in movie and movie[field] and 'Binged.png' in str(movie[field]):
                del movie[field]
                modified = True

        # Check nested posters object
        if 'posters' in movie and movie['posters']:
            posters = movie['posters']
            if any('Binged.png' in str(v) for v in posters.values() if v):
                del movie['posters']
                modified = True

        # Check all_posters array
        if 'all_posters' in movie and movie['all_posters']:
            for poster_set in movie['all_posters']:
                if any('Binged.png' in str(v) for v in poster_set.values() if v):
                    del movie['all_posters']
                    modified = True
                    break

        # Check backdrops object
        if 'backdrops' in movie and movie['backdrops']:
            backdrops = movie['backdrops']
            if any('Binged.png' in str(v) for v in backdrops.values() if v):
                del movie['backdrops']
                modified = True

        # Check all_backdrops array
        if 'all_backdrops' in movie and movie['all_backdrops']:
            for backdrop_set in movie['all_backdrops']:
                if any('Binged.png' in str(v) for v in backdrop_set.values() if v):
                    del movie['all_backdrops']
                    modified = True
                    break

        # Remove poster_source field if it was from binged
        if 'poster_source' in movie and movie['poster_source'] == 'binged':
            del movie['poster_source']
            modified = True

        if modified:
            fixed_count += 1
            print(f"Fixed: {movie.get('title', 'Unknown')}")

    # Save the cleaned data
    with open('movies_enriched.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Fixed {fixed_count} movies with Binged.png posters")
    print(f"💾 Saved: movies_enriched.json")

    return fixed_count

if __name__ == '__main__':
    fix_binged_posters()
