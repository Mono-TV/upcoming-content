#!/usr/bin/env python3
"""
Fix Stranger Things Season 5 poster by searching TMDB properly
"""

import json
import requests
import os

TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '452357e5da52e2ddde20c64414a40637')

def search_stranger_things():
    """Search for Stranger Things on TMDB"""
    try:
        # Search for the TV show
        url = "https://api.themoviedb.org/3/search/tv"
        params = {
            'api_key': TMDB_API_KEY,
            'query': 'Stranger Things',
            'language': 'en-US'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('results'):
            result = data['results'][0]
            print(f"Found: {result['name']} (ID: {result['id']})")
            return result['id'], 'tv'

        return None, None
    except Exception as e:
        print(f"Error searching: {e}")
        return None, None

def get_tmdb_posters(tmdb_id, media_type):
    """Get posters from TMDB with retry logic"""
    import time

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
            print(f"Attempt {attempt + 1}/3 failed: {e}")
            if attempt < 2:
                time.sleep(2)
                continue
            return []
    return []

def fix_stranger_things():
    """Fix Stranger Things Season 5 poster"""

    # Load enriched data
    with open('movies_enriched.json', 'r', encoding='utf-8') as f:
        movies = json.load(f)

    # Find Stranger Things
    st_movie = None
    st_index = None
    for i, movie in enumerate(movies):
        if 'Stranger Things' in movie.get('title', ''):
            st_movie = movie
            st_index = i
            break

    if not st_movie:
        print("Stranger Things not found in data")
        return

    print(f"Found: {st_movie['title']}")
    print(f"Current poster source: {'Binged' if 'binged' in st_movie.get('posters', {}).get('medium', '').lower() else 'TMDB'}")

    # Search TMDB
    print("\nSearching TMDB...")
    tmdb_id, media_type = search_stranger_things()

    if not tmdb_id:
        print("Could not find Stranger Things on TMDB")
        return

    # Get posters
    print(f"Fetching posters for TMDB ID {tmdb_id}...")
    posters = get_tmdb_posters(tmdb_id, media_type)

    if not posters:
        print("No posters found")
        return

    print(f"Found {len(posters)} posters!")

    # Update the movie data
    st_movie['tmdb_id'] = tmdb_id
    st_movie['tmdb_media_type'] = media_type

    st_movie['posters'] = {
        'thumbnail': f"https://image.tmdb.org/t/p/w92{posters[0]}",
        'small': f"https://image.tmdb.org/t/p/w185{posters[0]}",
        'medium': f"https://image.tmdb.org/t/p/w342{posters[0]}",
        'large': f"https://image.tmdb.org/t/p/w500{posters[0]}",
        'xlarge': f"https://image.tmdb.org/t/p/w780{posters[0]}",
        'original': f"https://image.tmdb.org/t/p/original{posters[0]}"
    }

    st_movie['all_posters'] = [
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

    st_movie['poster_url_medium'] = st_movie['posters']['medium']
    st_movie['poster_url_large'] = st_movie['posters']['large']

    movies[st_index] = st_movie

    # Save
    with open('movies_enriched.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Fixed Stranger Things poster!")
    print(f"New poster URL: {st_movie['posters']['medium']}")
    print(f"💾 Saved: movies_enriched.json")

if __name__ == '__main__':
    fix_stranger_things()
