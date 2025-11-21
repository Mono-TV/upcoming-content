#!/usr/bin/env python3
"""
Fix poster aspect ratios by re-fetching TMDB posters
Focuses on items that have Binged posters or incorrect aspect ratios
"""

import json
import os
import requests
import time

# TMDB API Key
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '452357e5da52e2ddde20c64414a40637')

def get_tmdb_posters(tmdb_id, media_type):
    """Get posters from TMDB"""
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
        params = {'api_key': TMDB_API_KEY}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        posters = data.get('posters', [])

        # Sort by vote average (quality)
        posters.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

        # Return file paths
        return [img['file_path'] for img in posters if img.get('file_path')]
    except Exception as e:
        print(f"    Error fetching posters: {e}")
        return []

def fix_posters():
    """Fix poster aspect ratios in enriched data"""

    # Load enriched data
    with open('movies_enriched.json', 'r', encoding='utf-8') as f:
        movies = json.load(f)

    print(f"\nTotal movies: {len(movies)}")

    # Find movies with Binged posters or no TMDB posters
    movies_to_fix = []
    for movie in movies:
        if movie.get('poster_source') == 'binged' or (movie.get('tmdb_id') and not movie.get('posters', {}).get('thumbnail', '').startswith('https://image.tmdb.org')):
            movies_to_fix.append(movie)

    print(f"Movies with incorrect poster aspect ratios: {len(movies_to_fix)}")

    if not movies_to_fix:
        print("\n✅ All posters are already using correct TMDB format!")
        return

    print("\n" + "="*60)
    print("FIXING POSTER ASPECT RATIOS")
    print("="*60 + "\n")

    fixed_count = 0

    for i, movie in enumerate(movies_to_fix, 1):
        title = movie.get('title', 'Unknown')
        print(f"[{i}/{len(movies_to_fix)}] {title[:50]}... ", end='', flush=True)

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

            # Remove Binged poster source marker
            if 'poster_source' in movie:
                del movie['poster_source']

            fixed_count += 1
            print(f"✓ Fixed with {len(posters)} TMDB poster(s)")
        else:
            print("⊙ No TMDB posters available, keeping current")

        time.sleep(0.25)  # Rate limiting

    # Save updated data
    with open('movies_enriched.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Fixed {fixed_count}/{len(movies_to_fix)} posters")
    print(f"💾 Saved: movies_enriched.json")

    # Summary
    with_tmdb_posters = sum(1 for m in movies if m.get('posters', {}).get('thumbnail', '').startswith('https://image.tmdb.org'))
    print(f"\n📊 Final status: {with_tmdb_posters}/{len(movies)} movies have correct TMDB posters")

if __name__ == '__main__':
    fix_posters()
