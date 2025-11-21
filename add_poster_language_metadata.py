#!/usr/bin/env python3
"""
Add poster language metadata to all movies by checking TMDB
"""

import json
import os
import requests
import time

TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '452357e5da52e2ddde20c64414a40637')

def get_poster_language(tmdb_id, media_type, current_poster_path):
    """Get the language of the current poster from TMDB"""
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
        params = {'api_key': TMDB_API_KEY}

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        posters = data.get('posters', [])

        # Find the current poster and get its language
        for poster in posters:
            if current_poster_path in poster.get('file_path', ''):
                lang = poster.get('iso_639_1')
                return lang if lang else 'none'

        return 'unknown'
    except Exception as e:
        return 'error'

def add_language_metadata(filename):
    """Add poster language metadata to all movies"""

    with open(filename, 'r', encoding='utf-8') as f:
        movies = json.load(f)

    if not movies:
        return

    print(f"\nProcessing: {filename}")
    print(f"Total movies: {len(movies)}\n")

    updated = 0

    for i, movie in enumerate(movies, 1):
        # Skip if already has language metadata
        if movie.get('poster_language'):
            continue

        title = movie.get('title', 'Unknown')[:45]
        print(f"[{i}/{len(movies)}] {title}... ", end='', flush=True)

        if not movie.get('tmdb_id') or not movie.get('posters', {}).get('medium'):
            print("⊙ No TMDB data")
            continue

        tmdb_id = movie['tmdb_id']
        media_type = movie.get('tmdb_media_type', 'movie')
        current_poster = movie['posters']['medium']

        # Extract poster path from URL
        if '/original/' in current_poster:
            poster_path = current_poster.split('/original/')[-1]
        else:
            # Extract from any size
            parts = current_poster.split('/')
            poster_path = parts[-1] if parts else ''

        if poster_path:
            lang = get_poster_language(tmdb_id, media_type, poster_path)
            movie['poster_language'] = lang
            updated += 1
            print(f"✓ {lang}")
        else:
            print("⊙ Could not extract path")

        time.sleep(0.3)

    # Save
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated {updated} movies with language metadata")
    print(f"💾 Saved: {filename}\n")

def main():
    files = [
        'movies_enriched.json',
        'ott_releases_enriched.json'
    ]

    for filename in files:
        if os.path.exists(filename):
            add_language_metadata(filename)

if __name__ == '__main__':
    main()
