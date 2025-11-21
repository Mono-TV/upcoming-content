#!/usr/bin/env python3
"""
Fix non-TMDB posters in OTT releases to use proper TMDB posters
"""

import json
import os
import requests
import time

TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '452357e5da52e2ddde20c64414a40637')

def get_tmdb_posters(tmdb_id, media_type):
    """Get posters from TMDB with retry logic"""
    for attempt in range(3):
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
            params = {'api_key': TMDB_API_KEY}

            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            posters = data.get('posters', [])
            posters.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

            return [img['file_path'] for img in posters if img.get('file_path')]
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            print(f"    Error: {e}")
            return []
    return []

def fix_ott_posters():
    """Fix all non-TMDB posters in OTT releases"""

    # Load data
    with open('ott_releases_enriched.json', 'r', encoding='utf-8') as f:
        movies = json.load(f)

    print(f"\nTotal OTT releases: {len(movies)}")

    # Find movies with non-TMDB posters
    movies_to_fix = []
    for movie in movies:
        poster_url = movie.get('posters', {}).get('medium', '')
        # Check if poster is NOT from TMDB
        if poster_url and not poster_url.startswith('https://image.tmdb.org'):
            movies_to_fix.append(movie)

    print(f"Movies with non-TMDB posters: {len(movies_to_fix)}")

    if not movies_to_fix:
        print("\n✅ All posters are already using TMDB format!")
        return

    print("\n" + "="*70)
    print("FIXING NON-TMDB POSTERS IN OTT RELEASES")
    print("="*70 + "\n")

    fixed_count = 0

    for i, movie in enumerate(movies_to_fix, 1):
        title = movie.get('title', 'Unknown')
        current_source = 'IMDb' if 'amazon' in movie.get('posters', {}).get('medium', '').lower() else 'Other'

        print(f"[{i}/{len(movies_to_fix)}] {title[:45]}...", end=' ', flush=True)
        print(f"({current_source}) ", end='', flush=True)

        if not movie.get('tmdb_id') or not movie.get('tmdb_media_type'):
            print("✗ No TMDB ID")
            continue

        tmdb_id = movie['tmdb_id']
        media_type = movie['tmdb_media_type']

        # Get TMDB posters
        posters = get_tmdb_posters(tmdb_id, media_type)

        if posters:
            # Update with TMDB posters
            movie['posters'] = {
                'thumbnail': f"https://image.tmdb.org/t/p/w92{posters[0]}",
                'small': f"https://image.tmdb.org/t/p/w185{posters[0]}",
                'medium': f"https://image.tmdb.org/t/p/w342{posters[0]}",
                'large': f"https://image.tmdb.org/t/p/w500{posters[0]}",
                'xlarge': f"https://image.tmdb.org/t/p/w780{posters[0]}",
                'original': f"https://image.tmdb.org/t/p/original{posters[0]}"
            }

            movie['all_posters'] = [
                {
                    'thumbnail': f"https://image.tmdb.org/t/p/w92{p}",
                    'small': f"https://image.tmdb.org/t/p/w185{p}",
                    'medium': f"https://image.tmdb.org/t/p/w342{p}",
                    'large': f"https://image.tmdb.org/t/p/w500{p}",
                    'xlarge': f"https://image.tmdb.org/t/p/w780{p}",
                    'original': f"https://image.tmdb.org/t/p/original{p}"
                }
                for p in posters[:5]
            ]

            movie['poster_url_medium'] = movie['posters']['medium']
            movie['poster_url_large'] = movie['posters']['large']

            fixed_count += 1
            print(f"✓ Fixed ({len(posters)} TMDB posters)")
        else:
            print("⊙ No TMDB posters found, keeping current")

        time.sleep(0.3)  # Rate limiting

    # Save updated data
    with open('ott_releases_enriched.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Fixed {fixed_count}/{len(movies_to_fix)} posters")
    print(f"💾 Saved: ott_releases_enriched.json")

    # Summary
    with_tmdb = sum(1 for m in movies if m.get('posters', {}).get('thumbnail', '').startswith('https://image.tmdb.org'))
    print(f"\n📊 Final status: {with_tmdb}/{len(movies)} movies have TMDB posters")

if __name__ == '__main__':
    fix_ott_posters()
